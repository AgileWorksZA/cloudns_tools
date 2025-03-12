#!/usr/bin/env python3
"""
ClouDNS Domain Sharing Tool

This script allows you to:
1. Login to the ClouDNS API
2. List all domains associated with your account
3. Share specified domains with another user (by email)
4. Verify the domains have been shared correctly

Usage:
    python cloudns_domain_share.py --list-domains
    python cloudns_domain_share.py --share-domains example.com,example.org --email user@example.com
    python cloudns_domain_share.py --share-file domains.txt --email user@example.com
    python cloudns_domain_share.py --verify-sharing example.com,example.org --email user@example.com
    
Authentication:
    Set environment variables:
        CLOUDNS_AUTH_ID - Your ClouDNS auth ID
        CLOUDNS_AUTH_PASSWORD - Your ClouDNS auth password
    
    Or provide command-line arguments:
        --auth-id - Your ClouDNS auth ID
        --auth-password - Your ClouDNS auth password
"""

import argparse
import json
import os
import requests
import sys
import time
from typing import List, Dict, Any, Optional

# ClouDNS API Configuration
API_URL = "https://api.cloudns.net"

# Default to environment variables if available
AUTH_ID = os.environ.get("CLOUDNS_AUTH_ID", "")
AUTH_PASSWORD = os.environ.get("CLOUDNS_AUTH_PASSWORD", "")

def make_api_request(endpoint: str, params: Dict[str, Any]) -> Dict:
    """Make an API request to ClouDNS and handle errors"""
    # Check if we have auth credentials
    if not AUTH_ID or not AUTH_PASSWORD:
        print("Error: Missing authentication credentials.")
        print("Please set CLOUDNS_AUTH_ID and CLOUDNS_AUTH_PASSWORD environment variables")
        print("or provide --auth-id and --auth-password command-line arguments.")
        sys.exit(1)
    
    # Add auth parameters to every request
    params["auth-id"] = AUTH_ID
    params["auth-password"] = AUTH_PASSWORD
    
    url = f"{API_URL}/{endpoint}"
    
    # Store the last response description as a global variable for error tracking
    global _last_status_description
    _last_status_description = ""
    
    # Try the request up to 3 times with exponential backoff
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()  # Raise exception for 4xx and 5xx responses
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"Error: Unable to parse API response: {response.text}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                sys.exit(1)
            
            # Check for API errors
            if isinstance(data, dict) and data.get("status") == "Failed":
                _last_status_description = data.get('statusDescription', 'Unknown error')
                print(f"API Error: {_last_status_description}")
                
                # Don't exit for "already shared" errors to maintain backward compatibility
                if "already shared" in _last_status_description.lower():
                    return data
                sys.exit(1)
                
            return data
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Network error: {str(e)}")
                print(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to connect to API after {max_retries} attempts: {str(e)}")
                sys.exit(1)
    
    # This should never be reached, but just in case
    print("Unexpected error in API request")
    sys.exit(1)

def login() -> bool:
    """Test login credentials"""
    print("Testing login credentials...")
    try:
        response = make_api_request("login/login.json", {})
        if response.get("status") == "Success":
            print("Login successful!")
            return True
        else:
            print(f"Login failed: {response.get('statusDescription', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def get_total_pages(rows_per_page: int = 100) -> int:
    """Get the total number of pages for domain listing"""
    # From the API testing, it seems the returned response is just the number
    # rather than a dict with a "count" key
    params = {"rows-per-page": rows_per_page}
    response = make_api_request("dns/get-pages-count.json", params)
    
    if isinstance(response, int):
        return response
    elif isinstance(response, dict) and "count" in response:
        return int(response["count"])
    else:
        # Try to convert to int directly
        try:
            return int(response)
        except (ValueError, TypeError):
            print(f"Unexpected response format for pages count: {response}")
            return 1  # Default to 1 page if we can't determine

def list_domains(all_pages: bool = True, page: int = 1, rows_per_page: int = 100) -> List[str]:
    """List domains in the account
    
    Args:
        all_pages: If True, fetch all pages of domains
        page: The page number to fetch if all_pages is False
        rows_per_page: Number of domains per page
        
    Returns:
        List of domain names
    """
    domains = []
    
    if all_pages:
        total_pages = get_total_pages(rows_per_page)
        print(f"Fetching all domains across {total_pages} pages...")
        
        for current_page in range(1, total_pages + 1):
            print(f"Fetching page {current_page}/{total_pages}...")
            
            params = {
                "page": current_page,
                "rows-per-page": rows_per_page
            }
            
            response = make_api_request("dns/list-zones.json", params)
            
            # The actual response appears to be a list of dictionaries
            if isinstance(response, list):
                for domain_data in response:
                    if isinstance(domain_data, dict) and 'name' in domain_data:
                        domains.append(domain_data['name'])
            # If it's still a dict, try the old way
            elif isinstance(response, dict):
                domains.extend(list(response.keys()))
            else:
                print(f"Unexpected response format on page {current_page}: {response}")
    else:
        print(f"Fetching domains from page {page}...")
        
        params = {
            "page": page,
            "rows-per-page": rows_per_page
        }
        
        response = make_api_request("dns/list-zones.json", params)
        
        # The actual response appears to be a list of dictionaries
        if isinstance(response, list):
            for domain_data in response:
                if isinstance(domain_data, dict) and 'name' in domain_data:
                    domains.append(domain_data['name'])
        # If it's still a dict, try the old way
        elif isinstance(response, dict):
            domains = list(response.keys())
        else:
            print(f"Unexpected response format: {response}")
    
    return domains

def share_domain(domain: str, email: str) -> bool:
    """Share a domain with another user by email"""
    print(f"Sharing domain {domain} with {email}...")
    
    params = {
        "domain-name": domain,
        "mail": email
    }
    
    try:
        response = make_api_request("dns/add-shared-account.json", params)
        if response.get("status") == "Success":
            print(f"Successfully shared {domain} with {email}")
            return True
        else:
            status_desc = response.get('statusDescription', 'Unknown error')
            if "already shared" in status_desc.lower():
                print(f"Domain {domain} is already shared with {email}")
                return True  # Consider already shared as success
            else:
                print(f"Failed to share {domain}: {status_desc}")
                return False
    except Exception as e:
        print(f"Error sharing domain {domain}: {str(e)}")
        return False

def verify_sharing(domain: str, email: Optional[str] = None) -> bool:
    """Verify that a domain is shared with a specific email (if provided)"""
    print(f"Verifying sharing for domain {domain}...")
    
    params = {
        "domain-name": domain
    }
    
    try:
        response = make_api_request("dns/list-shared-accounts.json", params)
        
        # If the response is a dictionary with status, the domain isn't shared
        if isinstance(response, dict) and response.get("status") == "Failed":
            print(f"Domain {domain} is not shared with anyone")
            return False
        
        # If response is a list, it contains the shared emails
        if isinstance(response, list):
            if not response:
                print(f"Domain {domain} is not shared with anyone")
                return False
                
            # Extract shared emails - the API returns a list of strings (emails)
            shared_emails = []
            for item in response:
                if isinstance(item, str):
                    # Direct string email in the list
                    shared_emails.append(item)
                elif isinstance(item, dict):
                    # Dictionary with mail/email key
                    if 'mail' in item:
                        shared_emails.append(item.get('mail'))
                    elif 'email' in item:
                        shared_emails.append(item.get('email'))
            
            # If email is provided, check if it's in the list
            if email:
                # Check both lowercase and original case
                email_lower = email.lower().strip()
                shared_emails_lower = [e.lower().strip() for e in shared_emails]
                
                if email_lower in shared_emails_lower:
                    print(f"Domain {domain} is shared with {email}")
                    return True
                else:
                    print(f"Domain {domain} is not shared with {email}")
                    print(f"It is shared with: {', '.join(shared_emails)}")
                    return False
            else:
                # Just list all shared accounts
                print(f"Domain {domain} is shared with: {', '.join(shared_emails)}")
                return bool(shared_emails)
        
        print(f"Unexpected response format for domain {domain}: {response}")
        return False
        
    except Exception as e:
        print(f"Error verifying sharing for domain {domain}: {str(e)}")
        return False

def load_domains_from_file(file_path: str) -> List[str]:
    """Load domains from a text file, one domain per line"""
    try:
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        return domains
    except Exception as e:
        print(f"Error loading domains from file {file_path}: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ClouDNS Domain Sharing Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-domains", action="store_true", help="List all domains in the account")
    group.add_argument("--share-domains", type=str, help="Comma-separated list of domains to share")
    group.add_argument("--share-file", type=str, help="Path to file containing domains to share (one per line)")
    group.add_argument("--verify-sharing", type=str, help="Comma-separated list of domains to verify sharing")
    group.add_argument("--test-login", action="store_true", help="Test login credentials only")
    
    parser.add_argument("--email", type=str, help="Email address to share domains with")
    parser.add_argument("--output-file", type=str, help="Output file for domain list")
    parser.add_argument("--verbose", action="store_true", help="Show detailed log information")
    
    # Authentication arguments
    parser.add_argument("--auth-id", type=str, help="ClouDNS Auth ID (overrides CLOUDNS_AUTH_ID env var)")
    parser.add_argument("--auth-password", type=str, help="ClouDNS Auth Password (overrides CLOUDNS_AUTH_PASSWORD env var)")
    
    args = parser.parse_args()
    
    # Set global auth variables from command-line args if provided
    global AUTH_ID, AUTH_PASSWORD
    if args.auth_id:
        AUTH_ID = args.auth_id
    if args.auth_password:
        AUTH_PASSWORD = args.auth_password
    
    # Login to ensure credentials are valid
    if not login():
        sys.exit(1)
    
    # Handle test login (do nothing else)
    if args.test_login:
        print("Login test complete. Credentials are valid.")
        sys.exit(0)
    
    # Handle listing domains
    if args.list_domains:
        domains = list_domains(all_pages=True)
        print(f"Found {len(domains)} domains")
        
        # If output file is provided, write domains to file
        if args.output_file:
            try:
                with open(args.output_file, 'w') as f:
                    for domain in domains:
                        f.write(f"{domain}\n")
                print(f"Domain list saved to {args.output_file}")
            except Exception as e:
                print(f"Error writing to output file: {str(e)}")
        else:
            # Otherwise, print to console
            for domain in domains:
                print(domain)
    
    # Handle sharing domains
    elif args.share_domains or args.share_file:
        if not args.email:
            print("Error: --email is required when sharing domains")
            sys.exit(1)
        
        # Get domains from file or command line argument
        if args.share_file:
            domains = load_domains_from_file(args.share_file)
            print(f"Loaded {len(domains)} domains from {args.share_file}")
        else:
            domains = [d.strip() for d in args.share_domains.split(",")]
            print(f"Processing {len(domains)} domains from command line")
        
        if len(domains) == 0:
            print("No domains to share. Exiting.")
            sys.exit(0)
        
        # Share each domain
        success_count = 0
        already_shared_count = 0
        failed_domains = []
        
        for domain in domains:
            try:
                if share_domain(domain, args.email):
                    success_count += 1
                    # Check if it was already shared
                    if "already shared" in globals().get("_last_status_description", "").lower():
                        already_shared_count += 1
                else:
                    failed_domains.append(domain)
            except Exception as e:
                print(f"Unexpected error sharing {domain}: {str(e)}")
                failed_domains.append(domain)
        
        print(f"\nSummary:")
        print(f"- Total domains processed: {len(domains)}")
        print(f"- Successfully shared: {success_count - already_shared_count}")
        print(f"- Already shared: {already_shared_count}")
        print(f"- Failed: {len(failed_domains)}")
        
        if failed_domains and args.verbose:
            print("\nFailed domains:")
            for domain in failed_domains:
                print(f"- {domain}")
    
    # Handle verifying sharing
    elif args.verify_sharing:
        domains = [d.strip() for d in args.verify_sharing.split(",")]
        
        # Verify sharing for each domain
        success_count = 0
        failed_domains = []
        
        for domain in domains:
            if verify_sharing(domain, args.email):
                success_count += 1
            else:
                failed_domains.append(domain)
        
        print(f"\nSummary:")
        print(f"- Total domains verified: {len(domains)}")
        print(f"- Successfully shared: {success_count}")
        print(f"- Not shared: {len(failed_domains)}")
        
        if args.email:
            print(f"- Shared with: {args.email}")
            
        if failed_domains and args.verbose:
            print("\nNot shared domains:")
            for domain in failed_domains:
                print(f"- {domain}")

if __name__ == "__main__":
    main()
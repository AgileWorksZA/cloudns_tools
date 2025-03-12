# ClouDNS Domain Sharing Tool

A command-line tool for managing domain sharing in your ClouDNS account.

## Features

- List all domains in your ClouDNS account
- Share domains with other users by email
- Verify that domains have been shared correctly
- Secure authentication via environment variables or command-line parameters
- Network resilience with automatic retries and exponential backoff
- Detailed summary output of sharing operations
- Test credential validity without performing other operations

## Prerequisites

- Python 3.6 or higher
- `requests` library (`pip install requests`)

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install requests
```

3. Make the scripts executable (Linux/Mac):

```bash
chmod +x cloudns_domain_share.py
chmod +x share_domains.sh
```

## Authentication

You have two ways to provide your ClouDNS authentication credentials:

### Using Environment Variables

```bash
# For Linux/Mac
export CLOUDNS_AUTH_ID=your_auth_id
export CLOUDNS_AUTH_PASSWORD=your_auth_password

# For Windows
set CLOUDNS_AUTH_ID=your_auth_id
set CLOUDNS_AUTH_PASSWORD=your_auth_password
```

### Using Command Line Arguments

You can also provide your credentials as command-line arguments with any command:

```bash
./cloudns_domain_share.py --list-domains --auth-id=your_auth_id --auth-password=your_auth_password
```

## Usage

### Command-line Options

The tool provides several command-line options:

```
usage: cloudns_domain_share.py [-h] 
                              (--list-domains | --share-domains SHARE_DOMAINS | --share-file SHARE_FILE | 
                               --verify-sharing VERIFY_SHARING | --test-login)
                              [--email EMAIL] [--output-file OUTPUT_FILE] [--verbose]
                              [--auth-id AUTH_ID] [--auth-password AUTH_PASSWORD]

options:
  -h, --help                      Show this help message and exit
  --list-domains                  List all domains in the account
  --share-domains SHARE_DOMAINS   Comma-separated list of domains to share
  --share-file SHARE_FILE         Path to file containing domains to share (one per line)
  --verify-sharing VERIFY_SHARING Comma-separated list of domains to verify sharing
  --test-login                    Test login credentials only
  --email EMAIL                   Email address to share domains with
  --output-file OUTPUT_FILE       Output file for domain list
  --verbose                       Show detailed log information
  --auth-id AUTH_ID               ClouDNS Auth ID (overrides CLOUDNS_AUTH_ID env var)
  --auth-password AUTH_PASSWORD   ClouDNS Auth Password (overrides CLOUDNS_AUTH_PASSWORD env var)
```

### Helper Scripts

For convenience, the tool comes with helper scripts for both Windows and Unix/Linux/Mac systems:

#### Windows (.bat)

```
share_domains.bat list-domains [output_file]
share_domains.bat share-domains email@example.com domain1,domain2,domain3
share_domains.bat share-file email@example.com domains.txt
share_domains.bat verify domain1,domain2,domain3 [email@example.com]
share_domains.bat test-login
```

#### Unix/Linux/Mac (.sh)

```
./share_domains.sh list-domains [output_file]
./share_domains.sh share-domains email@example.com domain1,domain2,domain3
./share_domains.sh share-file email@example.com domains.txt
./share_domains.sh verify domain1,domain2,domain3 [email@example.com]
./share_domains.sh test-login
```

Both types of scripts support the `--verbose` option for detailed output:

```
./share_domains.sh share-file email@example.com domains.txt --verbose
share_domains.bat verify domain1.com,domain2.com email@example.com --verbose
```

### Examples

#### Testing Login Credentials

Test if your login credentials are valid:

```bash
./cloudns_domain_share.py --test-login
```

#### Listing Domains

List all domains in your account:

```bash
./cloudns_domain_share.py --list-domains
```

Save the domain list to a file:

```bash
./cloudns_domain_share.py --list-domains --output-file domains.txt
```

#### Sharing Domains

Share specific domains with another user:

```bash
./cloudns_domain_share.py --share-domains example.com,example.org --email user@example.com
```

Share domains from a file with detailed output:

```bash
./cloudns_domain_share.py --share-file domains.txt --email user@example.com --verbose
```

#### Verifying Sharing

Verify that domains are shared with a specific user:

```bash
./cloudns_domain_share.py --verify-sharing example.com,example.org --email user@example.com
```

Verify all sharing for specific domains:

```bash
./cloudns_domain_share.py --verify-sharing example.com,example.org
```

## License

MIT License

## Error Handling

The tool implements several error handling mechanisms:

- Network failures: Automatic retries with exponential backoff (up to 3 attempts)
- Already shared domains: Treated as success rather than error
- API errors: Clearly shown with descriptive messages
- Summary reports: Detailed breakdown of successful and failed operations

## Best Practices

- Use environment variables for authentication credentials
- For large batches, use the `--share-file` option with a text file
- Always verify sharing after bulk operations with `--verify-sharing`
- Use the `--verbose` flag to see detailed information about operations, including any failures
- Run `test-login` to quickly check if credentials are valid without other operations
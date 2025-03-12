# CLAUDE.md - Guide for Agentic Coding Assistants

## Common Commands
- Setup: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Set auth: `export CLOUDNS_AUTH_ID=your_auth_id && export CLOUDNS_AUTH_PASSWORD=your_auth_password`
- Run (list domains): `./share_domains.sh list-domains`
- Run (share domains): `./share_domains.sh share-domains email@example.com domain1,domain2`
- Run (verify domains): `./share_domains.sh verify domain1,domain2 [email@example.com]`
- Run (from file): `./share_domains.sh share-file email@example.com domains.txt`

## API Details
- API Base URL: `https://api.cloudns.net`
- Authentication: Via environment variables or command-line parameters
  - Environment variables: `CLOUDNS_AUTH_ID` and `CLOUDNS_AUTH_PASSWORD`
  - Command-line arguments: `--auth-id` and `--auth-password`

## Code Style Guidelines
- **Imports**: Organize imports alphabetically, group by standard library, third-party, and local
- **Formatting**: Use 4 spaces for indentation
- **Types**: Use type annotations for all function parameters and return values
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Handle expected exceptions with specific catch blocks, provide meaningful error messages
- **Documentation**: Use docstrings for all functions, describe parameters and return values

## Project Structure
- `cloudns_domain_share.py`: Main Python script with API interaction logic
- `share_domains.sh`: Bash script wrapper for Linux/Mac
- `share_domains.bat`: Batch script wrapper for Windows
- `requirements.txt`: Python dependencies (requests)
- `/venv`: Virtual environment directory (not committed to version control)

## API Endpoints
- Login: `/login/login.json`
- List domains: `/dns/list-zones.json`
- Get pages count: `/dns/get-pages-count.json`
- Share domain: `/dns/add-shared-account.json`
- List shared accounts: `/dns/list-shared-accounts.json`
@echo off
REM ClouDNS Domain Sharing Tool - Windows Batch Script
setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage:
    echo share_domains.bat list-domains [output_file]
    echo share_domains.bat share-domains email@example.com domain1,domain2,domain3
    echo share_domains.bat share-file email@example.com domains.txt
    echo share_domains.bat verify domain1,domain2,domain3 [email@example.com]
    echo share_domains.bat test-login
    echo.
    echo Options:
    echo   --verbose  Show detailed information about the operations
    echo.
    echo Authentication:
    echo   Set environment variables:
    echo     set CLOUDNS_AUTH_ID=your_auth_id
    echo     set CLOUDNS_AUTH_PASSWORD=your_auth_password
    echo.
    echo   Or use the auth parameters with any command:
    echo     --auth-id=your_auth_id --auth-password=your_auth_password
    exit /b
)

REM Check for auth parameters and options
set AUTH_PARAMS=
set VERBOSE=
for %%a in (%*) do (
    if "%%a"=="--auth-id" set AUTH_PARAMS=!AUTH_PARAMS! --auth-id
    if "%%a"=="--auth-password" set AUTH_PARAMS=!AUTH_PARAMS! --auth-password
    if "%%a"=="--verbose" set VERBOSE=--verbose
)

if "%1"=="list-domains" (
    if "%2"=="" (
        python cloudns_domain_share.py --list-domains %AUTH_PARAMS% %VERBOSE%
    ) else (
        python cloudns_domain_share.py --list-domains --output-file %2 %AUTH_PARAMS% %VERBOSE%
    )
) else if "%1"=="test-login" (
    python cloudns_domain_share.py --test-login %AUTH_PARAMS%
) else if "%1"=="share-domains" (
    if "%2"=="" (
        echo Error: Email is required
        exit /b 1
    )
    if "%3"=="" (
        echo Error: Domain list is required
        exit /b 1
    )
    python cloudns_domain_share.py --share-domains %3 --email %2 %AUTH_PARAMS% %VERBOSE%
) else if "%1"=="share-file" (
    if "%2"=="" (
        echo Error: Email is required
        exit /b 1
    )
    if "%3"=="" (
        echo Error: Domain file is required
        exit /b 1
    )
    python cloudns_domain_share.py --share-file %3 --email %2 %AUTH_PARAMS% %VERBOSE%
) else if "%1"=="verify" (
    if "%2"=="" (
        echo Error: Domain list is required
        exit /b 1
    )
    if "%3"=="" (
        python cloudns_domain_share.py --verify-sharing %2 %AUTH_PARAMS% %VERBOSE%
    ) else (
        python cloudns_domain_share.py --verify-sharing %2 --email %3 %AUTH_PARAMS% %VERBOSE%
    )
) else (
    echo Unknown command: %1
    echo.
    echo Usage:
    echo share_domains.bat list-domains [output_file]
    echo share_domains.bat share-domains email@example.com domain1,domain2,domain3
    echo share_domains.bat share-file email@example.com domains.txt
    echo share_domains.bat verify domain1,domain2,domain3 [email@example.com]
    echo share_domains.bat test-login
    echo.
    echo Options:
    echo   --verbose  Show detailed information about the operations
    echo.
    echo Authentication:
    echo   Set environment variables:
    echo     set CLOUDNS_AUTH_ID=your_auth_id
    echo     set CLOUDNS_AUTH_PASSWORD=your_auth_password
    echo.
    echo   Or use the auth parameters with any command:
    echo     --auth-id=your_auth_id --auth-password=your_auth_password
    exit /b 1
)
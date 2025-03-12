#!/bin/bash
# ClouDNS Domain Sharing Tool - Bash Script

if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "./share_domains.sh list-domains [output_file] [--auth-id=ID --auth-password=PASS]"
    echo "./share_domains.sh share-domains email@example.com domain1,domain2,domain3 [--auth-id=ID --auth-password=PASS]"
    echo "./share_domains.sh share-file email@example.com domains.txt [--auth-id=ID --auth-password=PASS]"
    echo "./share_domains.sh verify domain1,domain2,domain3 [email@example.com] [--auth-id=ID --auth-password=PASS]"
    echo "./share_domains.sh test-login [--auth-id=ID --auth-password=PASS]"
    echo ""
    echo "Options:"
    echo "  --verbose  Show detailed information about the operations"
    echo ""
    echo "Authentication:"
    echo "  Set environment variables:"
    echo "    export CLOUDNS_AUTH_ID=your_auth_id"
    echo "    export CLOUDNS_AUTH_PASSWORD=your_auth_password"
    echo ""
    echo "  Or use the auth parameters with any command as shown above."
    exit 1
fi

# Check for auth parameters and options
AUTH_PARAMS=""
VERBOSE=""
for arg in "$@"; do
    if [[ $arg == --auth-id=* || $arg == --auth-password=* ]]; then
        AUTH_PARAMS="$AUTH_PARAMS $arg"
    elif [[ $arg == --verbose ]]; then
        VERBOSE="--verbose"
    fi
done

case "$1" in
    list-domains)
        output_file=""
        # Check if a second argument exists that doesn't start with --
        if [ ! -z "$2" ] && [[ ! "$2" == --* ]]; then
            output_file="--output-file $2"
        fi
        echo "Running: python3 cloudns_domain_share.py --list-domains $output_file $AUTH_PARAMS $VERBOSE"
        python3 cloudns_domain_share.py --list-domains $output_file $AUTH_PARAMS $VERBOSE
        ;;
    
    test-login)
        echo "Running: python3 cloudns_domain_share.py --test-login $AUTH_PARAMS"
        python3 cloudns_domain_share.py --test-login $AUTH_PARAMS
        ;;
    
    share-domains)
        # Collect required parameters
        email=""
        domains=""
        
        # Process positional arguments (should be first)
        if [[ ! "$2" == --* ]]; then
            email="$2"
            if [[ ! "$3" == --* ]]; then
                domains="$3"
            fi
        fi
        
        if [ -z "$email" ]; then
            echo "Error: Email is required"
            exit 1
        fi
        if [ -z "$domains" ]; then
            echo "Error: Domain list is required"
            exit 1
        fi
        
        echo "Running: python3 cloudns_domain_share.py --share-domains \"$domains\" --email \"$email\" $AUTH_PARAMS $VERBOSE"
        python3 cloudns_domain_share.py --share-domains "$domains" --email "$email" $AUTH_PARAMS $VERBOSE
        ;;
    
    share-file)
        # Collect required parameters
        email=""
        file=""
        
        # Process positional arguments (should be first)
        if [[ ! "$2" == --* ]]; then
            email="$2"
            if [[ ! "$3" == --* ]]; then
                file="$3"
            fi
        fi
        
        if [ -z "$email" ]; then
            echo "Error: Email is required"
            exit 1
        fi
        if [ -z "$file" ]; then
            echo "Error: Domain file is required"
            exit 1
        fi
        
        echo "Running: python3 cloudns_domain_share.py --share-file \"$file\" --email \"$email\" $AUTH_PARAMS $VERBOSE"
        python3 cloudns_domain_share.py --share-file "$file" --email "$email" $AUTH_PARAMS $VERBOSE
        ;;
    
    verify)
        # Collect required parameters
        domains=""
        email=""
        
        # Process positional arguments (should be first)
        if [[ ! "$2" == --* ]]; then
            domains="$2"
            if [[ ! "$3" == --* ]]; then
                email="$3"
            fi
        fi
        
        if [ -z "$domains" ]; then
            echo "Error: Domain list is required"
            exit 1
        fi
        
        if [ -z "$email" ]; then
            echo "Running: python3 cloudns_domain_share.py --verify-sharing \"$domains\" $AUTH_PARAMS $VERBOSE"
            python3 cloudns_domain_share.py --verify-sharing "$domains" $AUTH_PARAMS $VERBOSE
        else
            echo "Running: python3 cloudns_domain_share.py --verify-sharing \"$domains\" --email \"$email\" $AUTH_PARAMS $VERBOSE"
            python3 cloudns_domain_share.py --verify-sharing "$domains" --email "$email" $AUTH_PARAMS $VERBOSE
        fi
        ;;
    
    *)
        echo "Unknown command: $1"
        echo
        echo "Usage:"
        echo "./share_domains.sh list-domains [output_file] [--auth-id=ID --auth-password=PASS]"
        echo "./share_domains.sh share-domains email@example.com domain1,domain2,domain3 [--auth-id=ID --auth-password=PASS]"
        echo "./share_domains.sh share-file email@example.com domains.txt [--auth-id=ID --auth-password=PASS]"
        echo "./share_domains.sh verify domain1,domain2,domain3 [email@example.com] [--auth-id=ID --auth-password=PASS]"
        echo "./share_domains.sh test-login [--auth-id=ID --auth-password=PASS]"
        echo ""
        echo "Options:"
        echo "  --verbose  Show detailed information about the operations"
        echo ""
        echo "Authentication:"
        echo "  Set environment variables:"
        echo "    export CLOUDNS_AUTH_ID=your_auth_id"
        echo "    export CLOUDNS_AUTH_PASSWORD=your_auth_password"
        echo ""
        echo "  Or use the auth parameters with any command as shown above."
        exit 1
        ;;
esac
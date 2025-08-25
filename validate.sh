#!/bin/bash

# Bitwarden Export Validation Script Wrapper
# This script provides a convenient way to validate Bitwarden exports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Bitwarden Export Validation Script"
    echo ""
    echo "Usage: $0 <input_file> <output_file> [options]"
    echo ""
    echo "Arguments:"
    echo "  input_file   Path to the original Bitwarden export JSON file"
    echo "  output_file  Path to the organized Bitwarden export JSON file"
    echo ""
    echo "Options:"
    echo "  --verbose, -v    Enable verbose output"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 bw.json bw_organized.json"
    echo "  $0 bw.json bw_organized.json --verbose"
    echo ""
    echo "Exit codes:"
    echo "  0 - Validation passed (export is safe to import)"
    echo "  1 - Validation failed (review issues before importing)"
}

# Function to check if file exists
check_file() {
    local file=$1
    local description=$2

    if [[ ! -f "$file" ]]; then
        print_color $RED "❌ Error: $description file not found: $file"
        exit 1
    fi

    if [[ ! -r "$file" ]]; then
        print_color $RED "❌ Error: $description file is not readable: $file"
        exit 1
    fi
}

# Function to validate JSON format
validate_json() {
    local file=$1
    local description=$2

    if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
        print_color $RED "❌ Error: $description file is not valid JSON: $file"
        exit 1
    fi
}

# Function to run validation
run_validation() {
    local input_file=$1
    local output_file=$2
    local verbose_flag=$3

    print_color $BLUE "🔍 Starting Bitwarden export validation..."
    print_color $BLUE "Input:  $input_file"
    print_color $BLUE "Output: $output_file"
    echo ""

    # Run the Python validation script
    if python3 validate_bitwarden_export.py "$input_file" "$output_file" $verbose_flag; then
        echo ""
        print_color $GREEN "✅ Validation completed successfully!"
        return 0
    else
        echo ""
        print_color $RED "❌ Validation failed!"
        return 1
    fi
}

# Main script logic
main() {
    local input_file=""
    local output_file=""
    local verbose_flag=""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --verbose|-v)
                verbose_flag="--verbose"
                shift
                ;;
            -*)
                print_color $RED "❌ Error: Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$input_file" ]]; then
                    input_file="$1"
                elif [[ -z "$output_file" ]]; then
                    output_file="$1"
                else
                    print_color $RED "❌ Error: Too many arguments"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Check if required arguments are provided
    if [[ -z "$input_file" ]] || [[ -z "$output_file" ]]; then
        print_color $RED "❌ Error: Both input and output files are required"
        show_usage
        exit 1
    fi

    # Check if Python script exists
    if [[ ! -f "validate_bitwarden_export.py" ]]; then
        print_color $RED "❌ Error: Validation script not found: validate_bitwarden_export.py"
        print_color $YELLOW "Make sure you're running this script from the correct directory"
        exit 1
    fi

    # Validate input files
    print_color $BLUE "🔍 Validating input files..."
    check_file "$input_file" "Input"
    check_file "$output_file" "Output"

    # Validate JSON format
    print_color $BLUE "🔍 Validating JSON format..."
    validate_json "$input_file" "Input"
    validate_json "$output_file" "Output"

    print_color $GREEN "✓ Input files validated successfully"
    echo ""

    # Run validation
    if run_validation "$input_file" "$output_file" "$verbose_flag"; then
        exit 0
    else
        exit 1
    fi
}

# Run main function with all arguments
main "$@"

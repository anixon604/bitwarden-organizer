# Bitwarden Export Validation Script

This script validates the integrity and quality of Bitwarden exports by comparing the original input file with the organized output file. It performs comprehensive checks to ensure data preservation and quality improvements.

## Features

The validation script performs the following checks:

### 🔍 **Data Integrity Checks**
- **Item Count Preservation**: Ensures the same number of items in both files
- **Credentials Preservation**: Verifies all username/password pairs are maintained
- **Core Data Integrity**: Checks that critical fields (type, login data, URIs) are preserved
- **Metadata Preservation**: Ensures notes, creation dates, and revision dates are maintained

### 📁 **Organization Quality Checks**
- **Folder Creation**: Counts folders created and items assigned to folders
- **Collection Creation**: Counts collections created and items assigned to collections
- **Tag Assignment**: Counts items with tags
- **Name Improvements**: Tracks any name modifications made

### 🏗️ **Structure Validation**
- **JSON Structure**: Validates required fields and data types
- **Vault Type Detection**: Identifies personal vault vs organization vault
- **Field Consistency**: Ensures structural integrity

## Usage

### Basic Usage

```bash
python validate_bitwarden_export.py input.json output.json
```

### With Verbose Output

```bash
python validate_bitwarden_export.py input.json output.json --verbose
```

### Examples

```bash
# Validate your actual Bitwarden exports
python validate_bitwarden_export.py bw.json bw_organized.json

# Test with sample data
python test_validation.py
```

## Output

The script generates a comprehensive report showing:

- ✅ **Validation Results**: Pass/fail status for each check
- 📊 **Statistics**: Counts of items, folders, collections, tags
- ⚠️ **Warnings**: Non-critical issues that should be reviewed
- ❌ **Errors**: Critical issues that prevent safe import
- 🎯 **Overall Assessment**: Final recommendation for import

### Sample Output

```
============================================================
BITWARDEN EXPORT VALIDATION REPORT
============================================================
Input file: bw.json
Output file: bw_organized.json

📋 BASIC STRUCTURE VALIDATION
------------------------------
✓ Basic structure is valid

🔢 ITEM COUNT VALIDATION
------------------------------
✓ Item count preserved: 865 → 865

🔐 CREDENTIALS VALIDATION
------------------------------
✓ All credentials preserved: 865 pairs

🔍 ITEM INTEGRITY VALIDATION
------------------------------
✓ All items maintain their core data

📁 ORGANIZATION IMPROVEMENTS
------------------------------
Folders created: 28
Collections created: 0
Items with folders: 865
Items with collections: 0
Items with tags: 865

📝 METADATA PRESERVATION
------------------------------
Items with notes: 865
Items with URIs: 865
Items with creation date: 865
Items with revision date: 865

🎯 OVERALL ASSESSMENT
------------------------------
✅ VALIDATION PASSED - Export is ready for import
============================================================
```

## What Gets Checked

### 1. **Item Count Validation**
- Compares total number of items between input and output
- Ensures no items were lost during organization

### 2. **Credentials Preservation**
- Extracts all username/password pairs from both files
- Verifies every credential pair from input exists in output
- Reports any missing credentials with item names

### 3. **Item Integrity**
- Compares individual items using username/password as unique identifiers
- Checks that critical fields remain unchanged
- Reports any modifications made to items

### 4. **Organization Improvements**
- Counts folders and collections created
- Tracks items assigned to organizational structures
- Counts items with tags
- Validates that organization actually occurred

### 5. **Metadata Preservation**
- Counts items with notes, URIs, dates
- Verifies important metadata wasn't lost
- Reports any data loss issues

## Exit Codes

- **0**: Validation passed - export is safe to import
- **1**: Validation failed - review issues before importing

## Testing

Run the test script to see the validation in action:

```bash
python test_validation.py
```

This creates sample input/output files and runs the validation to demonstrate functionality.

## Integration with Bitwarden Organizer

This validation script is designed to work with the output from your Bitwarden organizer:

1. **Run the organizer**: `poetry run bitwarden-organize input.json --ai`
2. **Validate the output**: `python validate_bitwarden_export.py input.json input_organized.json`
3. **Review the report** and ensure all checks pass
4. **Import to Bitwarden** if validation passes

## Troubleshooting

### Common Issues

- **File not found**: Ensure both input and output files exist
- **Invalid JSON**: Check that both files contain valid JSON
- **Missing fields**: Verify files have the expected Bitwarden export structure

### Validation Failures

If validation fails:

1. **Review the detailed report** to identify specific issues
2. **Check the organizer logs** for any processing errors
3. **Verify file permissions** and file integrity
4. **Re-run the organization** if needed

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)
- Valid Bitwarden export JSON files

## File Structure

```
bitwarden/
├── validate_bitwarden_export.py    # Main validation script
├── test_validation.py              # Test script with sample data
├── VALIDATION_README.md            # This documentation
└── bitwarden_organizer/           # Your organizer code
```

## Contributing

To add new validation checks:

1. Add a new validation method to the `BitwardenValidator` class
2. Include it in the `run_validation()` method
3. Update the summary report generation
4. Add appropriate tests

The script is designed to be extensible for additional validation needs.

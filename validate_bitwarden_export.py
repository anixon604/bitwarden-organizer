#!/usr/bin/env python3
"""
Bitwarden Export Validation Script

This script validates the integrity and quality of Bitwarden exports by comparing
the original input file with the organized output file. It performs various checks
to ensure data preservation and quality improvements.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, Counter
import hashlib


class BitwardenValidator:
    """Validates Bitwarden export files for integrity and quality."""

    def __init__(self, input_file: str, output_file: str, verbose: bool = False):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.verbose = verbose
        self.input_data = None
        self.output_data = None
        self.validation_results = {}

    def load_files(self) -> bool:
        """Load and parse both JSON files."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.input_data = json.load(f)
            print(f"✓ Loaded input file: {self.input_file}")

            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.output_data = json.load(f)
            print(f"✓ Loaded output file: {self.output_file}")

            return True

        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False

    def validate_basic_structure(self) -> Dict[str, Any]:
        """Validate basic JSON structure and required fields."""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check required top-level fields
        required_fields = ['items']
        for field in required_fields:
            if field not in self.input_data:
                results['errors'].append(f"Missing required field in input: {field}")
                results['valid'] = False
            if field not in self.output_data:
                results['errors'].append(f"Missing required field in output: {field}")
                results['valid'] = False

        # Check if items is a list
        if 'items' in self.input_data and not isinstance(self.input_data['items'], list):
            results['errors'].append("Input 'items' field is not a list")
            results['valid'] = False
        if 'items' in self.output_data and not isinstance(self.output_data['items'], list):
            results['errors'].append("Output 'items' field is not a list")
            results['valid'] = False

        # Check for organization vs personal vault
        if 'collections' in self.input_data:
            if 'collections' not in self.output_data:
                results['warnings'].append("Input has collections but output is missing them")
        elif 'folders' in self.input_data:
            if 'folders' not in self.output_data:
                results['warnings'].append("Input has folders but output is missing them")

        return results

    def validate_item_count(self) -> Dict[str, Any]:
        """Validate that the number of items is preserved."""
        results = {
            'valid': True,
            'input_count': 0,
            'output_count': 0,
            'errors': []
        }

        input_count = len(self.input_data.get('items', []))
        output_count = len(self.output_data.get('items', []))

        results['input_count'] = input_count
        results['output_count'] = output_count

        if input_count != output_count:
            results['errors'].append(
                f"Item count mismatch: input has {input_count}, output has {output_count}"
            )
            results['valid'] = False

        return results

    def extract_credentials(self, items: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        """Extract username/password pairs from items."""
        credentials = []

        for item in items:
            if item.get('type') == 1:  # Login type
                login = item.get('login', {})
                username = login.get('username', '')
                password = login.get('password', '')
                name = item.get('name', 'Unknown')

                if username and password:  # Only include items with both username and password
                    credentials.append((username, password, name))

        return credentials

    def validate_credentials_preservation(self) -> Dict[str, Any]:
        """Validate that all username/password pairs are preserved."""
        results = {
            'valid': True,
            'input_credentials': 0,
            'output_credentials': 0,
            'missing_credentials': [],
            'errors': []
        }

        input_creds = self.extract_credentials(self.input_data.get('items', []))
        output_creds = self.extract_credentials(self.output_data.get('items', []))

        results['input_credentials'] = len(input_creds)
        results['output_credentials'] = len(output_creds)

        # Create sets for comparison (username, password) pairs
        input_set = {(u, p) for u, p, n in input_creds}
        output_set = {(u, p) for u, p, n in output_creds}

        # Find missing credentials
        missing = input_set - output_set
        if missing:
            results['valid'] = False
            for username, password in missing:
                # Find the item name for this credential
                item_name = next((n for u, p, n in input_creds if u == username and p == password), 'Unknown')
                results['missing_credentials'].append({
                    'username': username,
                    'password': password[:8] + '...' if len(password) > 8 else password,
                    'item_name': item_name
                })
            results['errors'].append(f"Missing {len(missing)} credential pairs")

        return results

    def validate_item_integrity(self) -> Dict[str, Any]:
        """Validate that individual items maintain their core data."""
        results = {
            'valid': True,
            'input_items': 0,
            'output_items': 0,
            'modified_items': [],
            'errors': []
        }

        input_items = self.input_data.get('items', [])
        output_items = self.output_data.get('items', [])

        results['input_items'] = len(input_items)
        results['output_items'] = len(output_items)

        # Create lookup dictionaries for comparison
        input_lookup = {}
        for item in input_items:
            if item.get('type') == 1:  # Login type
                login = item.get('login', {})
                username = login.get('username', '')
                password = login.get('password', '')
                if username and password:
                    key = (username, password)
                    input_lookup[key] = item

        output_lookup = {}
        for item in output_items:
            if item.get('type') == 1:  # Login type
                login = item.get('login', {})
                username = login.get('username', '')
                password = login.get('password', '')
                if username and password:
                    key = (username, password)
                    output_lookup[key] = item

        # Compare items with the same credentials
        for key in input_lookup:
            if key in output_lookup:
                input_item = input_lookup[key]
                output_item = output_lookup[key]

                # Check if critical fields are preserved
                critical_fields = ['type', 'login.username', 'login.password', 'login.uris']
                modifications = []

                for field in critical_fields:
                    if '.' in field:
                        # Handle nested fields
                        parts = field.split('.')
                        input_val = input_item
                        output_val = output_item

                        for part in parts:
                            input_val = input_val.get(part, {}) if isinstance(input_val, dict) else None
                            output_val = output_val.get(part, {}) if isinstance(output_val, dict) else None

                        if input_val != output_val:
                            modifications.append(f"{field}: {input_val} → {output_val}")
                    else:
                        if input_item.get(field) != output_item.get(field):
                            modifications.append(f"{field}: {input_item.get(field)} → {output_item.get(field)}")

                if modifications:
                    results['modified_items'].append({
                        'item_name': input_item.get('name', 'Unknown'),
                        'modifications': modifications
                    })

        return results

    def validate_organization_improvements(self) -> Dict[str, Any]:
        """Validate that organization improvements were made."""
        results = {
            'valid': True,
            'folders_created': 0,
            'collections_created': 0,
            'items_with_folders': 0,
            'items_with_collections': 0,
            'items_with_tags': 0,
            'warnings': []
        }

        # Check folders
        if 'folders' in self.output_data:
            results['folders_created'] = len(self.output_data['folders'])

            # Count items assigned to folders
            for item in self.output_data.get('items', []):
                if item.get('folderId'):
                    results['items_with_folders'] += 1

        # Check collections
        if 'collections' in self.output_data:
            results['collections_created'] = len(self.output_data['collections'])

            # Count items assigned to collections
            for item in self.output_data.get('items', []):
                if item.get('collectionIds'):
                    results['items_with_collections'] += len(item['collectionIds'])

        # Check tags
        for item in self.output_data.get('items', []):
            if item.get('tags'):
                results['items_with_tags'] += 1

        # Validate that organization actually happened
        if results['folders_created'] == 0 and results['collections_created'] == 0:
            results['warnings'].append("No folders or collections were created")

        return results

    def validate_metadata_preservation(self) -> Dict[str, Any]:
        """Validate that important metadata is preserved."""
        results = {
            'valid': True,
            'items_with_notes': 0,
            'items_with_uris': 0,
            'items_with_creation_date': 0,
            'items_with_revision_date': 0,
            'errors': []
        }

        input_items = self.input_data.get('items', [])
        output_items = self.output_data.get('items', [])

        # Count metadata in input
        for item in input_items:
            if item.get('notes'):
                results['items_with_notes'] += 1
            if item.get('login', {}).get('uris'):
                results['items_with_uris'] += 1
            if item.get('creationDate'):
                results['items_with_creation_date'] += 1
            if item.get('revisionDate'):
                results['items_with_revision_date'] += 1

        # Verify metadata is preserved in output
        for item in output_items:
            if not item.get('notes') and item.get('login', {}).get('uris'):
                # Check if this item had notes in input
                input_item = self._find_matching_input_item(item)
                if input_item and input_item.get('notes'):
                    results['errors'].append(f"Notes lost for item: {item.get('name', 'Unknown')}")
                    results['valid'] = False

        return results

    def _find_matching_input_item(self, output_item: Dict[str, Any]) -> Dict[str, Any]:
        """Find the corresponding input item for an output item."""
        output_login = output_item.get('login', {})
        output_username = output_login.get('username', '')
        output_password = output_login.get('password', '')

        for input_item in self.input_data.get('items', []):
            input_login = input_item.get('login', {})
            input_username = input_login.get('username', '')
            input_password = input_login.get('password', '')

            if (input_username == output_username and
                input_password == output_password):
                return input_item

        return None

    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report."""
        report = []
        report.append("=" * 60)
        report.append("BITWARDEN EXPORT VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Input file: {self.input_file}")
        report.append(f"Output file: {self.output_file}")
        report.append("")

        # Basic validation
        basic = self.validation_results.get('basic_structure', {})
        report.append("📋 BASIC STRUCTURE VALIDATION")
        report.append("-" * 30)
        if basic.get('valid'):
            report.append("✓ Basic structure is valid")
        else:
            report.append("❌ Basic structure has errors:")
            for error in basic.get('errors', []):
                report.append(f"  - {error}")

        for warning in basic.get('warnings', []):
            report.append(f"⚠️  {warning}")
        report.append("")

        # Item count validation
        count = self.validation_results.get('item_count', {})
        report.append("🔢 ITEM COUNT VALIDATION")
        report.append("-" * 30)
        if count.get('valid'):
            report.append(f"✓ Item count preserved: {count['input_count']} → {count['output_count']}")
        else:
            report.append("❌ Item count mismatch:")
            for error in count.get('errors', []):
                report.append(f"  - {error}")
        report.append("")

        # Credentials validation
        creds = self.validation_results.get('credentials_preservation', {})
        report.append("🔐 CREDENTIALS VALIDATION")
        report.append("-" * 30)
        if creds.get('valid'):
            report.append(f"✓ All credentials preserved: {creds['input_credentials']} pairs")
        else:
            report.append("❌ Missing credentials:")
            for missing in creds.get('missing_credentials', []):
                report.append(f"  - {missing['item_name']}: {missing['username']}")
        report.append("")

        # Item integrity validation
        integrity = self.validation_results.get('item_integrity', {})
        report.append("🔍 ITEM INTEGRITY VALIDATION")
        report.append("-" * 30)
        if not integrity.get('modified_items'):
            report.append("✓ All items maintain their core data")
        else:
            report.append(f"⚠️  {len(integrity['modified_items'])} items have modifications:")
            for item in integrity['modified_items'][:5]:  # Show first 5
                report.append(f"  - {item['item_name']}: {', '.join(item['modifications'][:3])}")
            if len(integrity['modified_items']) > 5:
                report.append(f"  ... and {len(integrity['modified_items']) - 5} more")
        report.append("")

        # Organization improvements
        org = self.validation_results.get('organization_improvements', {})
        report.append("📁 ORGANIZATION IMPROVEMENTS")
        report.append("-" * 30)
        report.append(f"Folders created: {org.get('folders_created', 0)}")
        report.append(f"Collections created: {org.get('collections_created', 0)}")
        report.append(f"Items with folders: {org.get('items_with_folders', 0)}")
        report.append(f"Items with collections: {org.get('items_with_collections', 0)}")
        report.append(f"Items with tags: {org.get('items_with_tags', 0)}")

        for warning in org.get('warnings', []):
            report.append(f"⚠️  {warning}")
        report.append("")

        # Metadata preservation
        metadata = self.validation_results.get('metadata_preservation', {})
        report.append("📝 METADATA PRESERVATION")
        report.append("-" * 30)
        report.append(f"Items with notes: {metadata.get('items_with_notes', 0)}")
        report.append(f"Items with URIs: {metadata.get('items_with_uris', 0)}")
        report.append(f"Items with creation date: {metadata.get('items_with_creation_date', 0)}")
        report.append(f"Items with revision date: {metadata.get('items_with_revision_date', 0)}")

        if not metadata.get('valid'):
            report.append("❌ Some metadata was lost:")
            for error in metadata.get('errors', []):
                report.append(f"  - {error}")
        report.append("")

        # Overall assessment
        report.append("🎯 OVERALL ASSESSMENT")
        report.append("-" * 30)

        all_valid = all(
            result.get('valid', False)
            for result in self.validation_results.values()
            if isinstance(result, dict) and 'valid' in result
        )

        if all_valid:
            report.append("✅ VALIDATION PASSED - Export is ready for import")
        else:
            report.append("❌ VALIDATION FAILED - Review issues before importing")

        report.append("=" * 60)

        return "\n".join(report)

    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting Bitwarden export validation...")
        print(f"Input: {self.input_file}")
        print(f"Output: {self.output_file}")
        print()

        # Load files
        if not self.load_files():
            return False

        # Run all validation checks
        self.validation_results = {
            'basic_structure': self.validate_basic_structure(),
            'item_count': self.validate_item_count(),
            'credentials_preservation': self.validate_credentials_preservation(),
            'item_integrity': self.validate_item_integrity(),
            'organization_improvements': self.validate_organization_improvements(),
            'metadata_preservation': self.validate_metadata_preservation()
        }

        # Generate and display report
        report = self.generate_summary_report()
        print(report)

        # Return overall validation status
        all_valid = all(
            result.get('valid', False)
            for result in self.validation_results.values()
            if isinstance(result, dict) and 'valid' in result
        )

        return all_valid


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate Bitwarden export files for integrity and quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_bitwarden_export.py input.json output.json
  python validate_bitwarden_export.py bw.json bw_organized.json --verbose
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to the original Bitwarden export JSON file'
    )

    parser.add_argument(
        'output_file',
        help='Path to the organized Bitwarden export JSON file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate input files exist
    if not Path(args.input_file).exists():
        print(f"❌ Input file not found: {args.input_file}")
        sys.exit(1)

    if not Path(args.output_file).exists():
        print(f"❌ Output file not found: {args.output_file}")
        sys.exit(1)

    # Run validation
    validator = BitwardenValidator(args.input_file, args.output_file, args.verbose)
    success = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

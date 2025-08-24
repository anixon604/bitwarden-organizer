"""
Command-line interface for the Bitwarden Organizer.

This module provides a CLI for organizing Bitwarden exports from the command line.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .core import OrganizerConfig, organize_bitwarden_export


def load_json_file(file_path: str) -> dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def save_json_file(data: dict, file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Organized data saved to: {file_path}")
    except Exception as e:
        print(f"Error saving to '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def validate_input_file(file_path: str) -> None:
    """Validate that the input file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Input file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"Error: '{file_path}' is not a file.", file=sys.stderr)
        sys.exit(1)
    if not path.stat().st_size > 0:
        print(f"Error: Input file '{file_path}' is empty.", file=sys.stderr)
        sys.exit(1)


def create_output_filename(input_path: str, output_path: Optional[str] = None) -> str:
    """Create output filename if not specified."""
    if output_path:
        return output_path

    input_path_obj = Path(input_path)
    stem = input_path_obj.stem
    suffix = input_path_obj.suffix

    # Create organized filename
    if stem.endswith('_organized'):
        return str(input_path_obj)
    else:
        return str(input_path_obj.parent / f"{stem}_organized{suffix}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Organize Bitwarden JSON exports with automatic categorization and tagging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s export.json                    # Organize and save as export_organized.json
  %(prog)s export.json -o clean.json      # Organize and save as clean.json
  %(prog)s export.json --dry-run          # Preview changes without saving

Safety Notes:
  - Always test on a COPY of your export first
  - The tool never modifies usernames, passwords, or TOTP secrets
  - Only processes: names, notes, folders, collections, and custom fields
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to the Bitwarden JSON export file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: input_organized.json)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing output file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Skip adding metadata headers to notes'
    )

    parser.add_argument(
        '--no-suggest-names',
        action='store_true',
        help='Skip suggesting cleaner item names'
    )

    parser.add_argument(
        '--no-folders',
        action='store_true',
        help='Skip creating and assigning folders/collections'
    )

    parser.add_argument(
        '--no-tags',
        action='store_true',
        help='Skip adding tags as custom fields'
    )

    args = parser.parse_args()

    # Validate input file
    validate_input_file(args.input_file)

    # Create configuration
    config = OrganizerConfig(
        dry_run=args.dry_run,
        verbose=args.verbose,
        add_metadata=not args.no_metadata,
        suggest_names=not args.no_suggest_names,
        create_folders=not args.no_folders,
        add_tags=not args.no_tags
    )

    # Load input data
    print(f"Loading Bitwarden export from: {args.input_file}")
    data = load_json_file(args.input_file)

    # Validate data structure
    if not isinstance(data, dict):
        print("Error: Input file must contain a JSON object.", file=sys.stderr)
        sys.exit(1)

    if "items" not in data:
        print("Error: Input file must contain 'items' array.", file=sys.stderr)
        sys.exit(1)

    items_count = len(data.get("items", []))
    print(f"Found {items_count} items to process")

    # Check if this is an organization export
    if "collections" in data:
        print("Detected organization export (has collections)")
    else:
        print("Detected personal vault export (has folders)")

    # Process the data
    print("Organizing items...")
    try:
        organized_data = organize_bitwarden_export(data, config)
        print("✓ Organization completed successfully")
    except Exception as e:
        print(f"Error during organization: {e}", file=sys.stderr)
        sys.exit(1)

    # Show summary
    folders_count = len(organized_data.get("folders", []))
    collections_count = len(organized_data.get("collections", []))

    print(f"\nSummary:")
    print(f"  - Items processed: {items_count}")
    print(f"  - Folders created: {folders_count}")
    print(f"  - Collections created: {collections_count}")

    if args.dry_run:
        print("\nDRY RUN MODE - No files were written")
        print("Use without --dry-run to save the organized data")
    else:
        # Determine output file
        output_file = create_output_filename(args.input_file, args.output)

        # Save organized data
        print(f"\nSaving organized data...")
        save_json_file(organized_data, output_file)

        print(f"\n✓ Organization complete!")
        print(f"  - Original file: {args.input_file}")
        print(f"  - Organized file: {output_file}")
        print(f"\nYou can now import '{output_file}' back into Bitwarden")


if __name__ == "__main__":
    main()

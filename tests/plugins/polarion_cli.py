#!/usr/bin/env python
"""
Polarion xUnit Generator CLI

This script generates Polarion-compatible xUnit XML files from Robot Framework
test results. It can be used in CI/CD pipelines or run manually after test execution.

Usage:
    python polarion_cli.py output.xml --project MYPROJ --testrun RUN-001
    
Examples:
    # Basic usage
    python polarion_cli.py output.xml
    
    # With Polarion project and test run IDs
    python polarion_cli.py output.xml --project SYSBOT --testrun SPRINT-42
    
    # With custom output file
    python polarion_cli.py output.xml -o polarion_results.xml
    
    # With custom properties
    python polarion_cli.py output.xml --project SYSBOT --property environment=prod --property version=2.0
"""

import argparse
import sys
import os
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Import polarion module
try:
    from sysbot.plugins.polarion import Polarion
except ImportError:
    # Fallback for running script directly from tests directory
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from sysbot.plugins.polarion import Polarion


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate Polarion-compatible xUnit XML from Robot Framework output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s output.xml
  %(prog)s output.xml --project MYPROJ --testrun RUN-001
  %(prog)s output.xml -o polarion.xml --property env=prod
  
Robot Framework Tag Format:
  Use tags in your test cases to link to Polarion:
    [Tags]  polarion-id:TEST-123  polarion-title:My Test
    [Tags]  polarion-testEnvironment:prod  polarion-priority:high
        """
    )
    
    parser.add_argument(
        'output_xml',
        help='Path to Robot Framework output.xml file'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='xunit_file',
        default='polarion_results.xml',
        help='Path for generated xUnit XML file (default: polarion_results.xml)'
    )
    
    parser.add_argument(
        '--project',
        dest='project_id',
        help='Polarion project ID'
    )
    
    parser.add_argument(
        '--testrun',
        dest='test_run_id',
        help='Polarion test run ID'
    )
    
    parser.add_argument(
        '--property',
        dest='properties',
        action='append',
        metavar='KEY=VALUE',
        help='Add custom property (can be used multiple times)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def parse_properties(property_list):
    """Parse property list from command line format."""
    if not property_list:
        return {}
    
    properties = {}
    for prop in property_list:
        if '=' not in prop:
            print(f"Warning: Invalid property format '{prop}', expected KEY=VALUE", file=sys.stderr)
            continue
        key, value = prop.split('=', 1)
        properties[key.strip()] = value.strip()
    
    return properties


def main():
    """Main entry point."""
    args = parse_args()
    
    # Check input file exists
    if not os.path.exists(args.output_xml):
        print(f"Error: Input file not found: {args.output_xml}", file=sys.stderr)
        return EXIT_FAILURE
    
    # Parse custom properties
    custom_properties = parse_properties(args.properties)
    
    if args.verbose:
        print(f"Input file: {args.output_xml}")
        print(f"Output file: {args.xunit_file}")
        if args.project_id:
            print(f"Project ID: {args.project_id}")
        if args.test_run_id:
            print(f"Test Run ID: {args.test_run_id}")
        if custom_properties:
            print(f"Custom properties: {custom_properties}")
    
    try:
        # Generate Polarion xUnit
        polarion = Polarion()
        result = polarion.generate_xunit(
            output_xml=args.output_xml,
            xunit_file=args.xunit_file,
            project_id=args.project_id,
            test_run_id=args.test_run_id,
            custom_properties=custom_properties
        )
        
        print(f"✓ Generated Polarion xUnit file: {result}")
        
        # Show file size
        file_size = os.path.getsize(result)
        print(f"  File size: {file_size} bytes")
        
        return EXIT_SUCCESS
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_FAILURE
    except Exception as e:
        print(f"Error: Failed to generate xUnit file: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return EXIT_FAILURE


if __name__ == '__main__':
    sys.exit(main())

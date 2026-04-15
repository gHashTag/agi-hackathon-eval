#!/usr/bin/env python3
"""
Fix issues with Kaggle datasets for Data Explorer compatibility
Fixes:
1. Multiline choices in TTM and TSCP (replace 
 with |)
2. Update About descriptions for TTM and TEFB
"""

import pandas as pd
import subprocess
import sys
from pathlib import Path


def fix_ttm_tscp(csv_path: str, output_path: str):
    """Fix multiline choices in CSV"""
    print(f"Fixing {csv_path}...")

    df = pd.read_csv(csv_path)

    # Fix multiline choices by replacing 
 with |
    df['choices'] = df['choices'].str.replace('
', ' | ')

    # Save to output
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")


def print_about_update_instructions():
    """Update Kaggle About descriptions for tracks"""
    print("
Note: These descriptions must be updated manually on Kaggle:")
    print("Go to: https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-<track>/edit")
    print("
TTM: Change '733 multiple-choice questions' to actual row count")
    print("TEFB: Change '1805 multiple-choice questions' to actual row count")
    print("TSCP: Remove 'License: MIT' from About/README
")


def main():
    """Main function"""
    # No arguments required for basic usage
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python fix_kaggle_datasets.py [--upload]")
        print("
Fixes issues and optionally uploads to Kaggle")
        sys.exit(0)

    base_dir = Path(__file__).parent.parent / "data"

    # Fix TTM
    ttm_csv = base_dir / "ttm" / "tmp_mc.csv"
    ttm_fixed = base_dir / "ttm" / "tmp_mc_v2.csv"

    if ttm_csv.exists():
        fix_ttm_tscp(ttm_csv, ttm_fixed)
        print(f"✅ TTM fixed: {ttm_fixed.name}")

        # Upload if requested
        if "--upload" in sys.argv:
            print("
⚠️  Upload not implemented yet")
            print("Please upload manually via Kaggle Data Explorer")
    else:
        print(f"TTM file not found: {ttm_csv}")

    # Fix TSCP
    tscp_csv = base_dir / "tscp" / "tmp_mc.csv"
    tscp_fixed = base_dir / "tscp" / "tmp_mc_v2.csv"

    if tscp_csv.exists():
        fix_ttm_tscp(tscp_csv, tscp_fixed)
        print(f"✅ TSCP fixed: {tscp_fixed.name}")

        # Upload if requested
        if "--upload" in sys.argv:
            print("
⚠️  Upload not implemented yet")
            print("Please upload manually via Kaggle Data Explorer")
    else:
        print(f"TSCP file not found: {tscp_csv}")

    # Print about update instructions
    print_about_update_instructions()


if __name__ == "__main__":
    main()

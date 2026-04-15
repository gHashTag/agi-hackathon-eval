#!/usr/bin/env python3
"""
Download Trinity Cognitive Probes datasets from Kaggle

Prerequisites:
1. Install kaggle: pip install kaggle
2. Set up Kaggle API credentials:
   - Get API token from https://www.kaggle.com/account
   - Place kaggle.json in ~/.kaggle/kaggle.json
   - chmod 600 ~/.kaggle/kaggle.json

Usage:
    python scripts/download_data.py
    python scripts/download_data.py --track thlp
    python scripts/download_data.py --check-only
"""

import subprocess
import sys
import zipfile
from pathlib import Path
import argparse


# Dataset slugs on Kaggle
DATASETS = {
    'thlp': 'playra/trinity-cognitive-probes-thlp-mc',
    'ttm': 'playra/trinity-cognitive-probes-ttm-mc',
    'tagp': 'playra/trinity-cognitive-probes-tagp-mc',
    'tefb': 'playra/trinity-cognitive-probes-tefb-mc',
    'tscp': 'playra/trinity-cognitive-probes-tscp-mc',
}


def download_track(track: str, data_dir: Path) -> bool:
    """Download and extract a single track"""
    if track not in DATASETS:
        print(f"❌ Unknown track: {track}")
        return False
    
    slug = DATASETS[track]
    track_dir = data_dir / track
    track_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"
📥 Downloading {track.upper()}...")
    print(f"   Kaggle: {slug}")
    print(f"   Target: {track_dir}")
    
    try:
        # Download
        result = subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', slug, '-p', str(track_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ Download failed: {result.stderr}")
            return False
        
        # Find and extract zip file
        zip_files = list(track_dir.glob('*.zip'))
        if zip_files:
            zip_path = zip_files[0]
            print(f"   Extracting {zip_path.name}...")
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(track_dir)
            
            # Remove zip file after extraction
            zip_path.unlink()
            print(f"   ✅ Extracted and cleaned up")
        
        # Check what files we have
        csv_files = list(track_dir.glob('*.csv'))
        if csv_files:
            print(f"   📊 Found {len(csv_files)} CSV file(s):")
            for f in csv_files:
                print(f"      - {f.name}")
            return True
        else:
            print(f"   ⚠️  No CSV files found")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Download timeout")
        return False
    except FileNotFoundError:
        print(f"❌ Kaggle CLI not found. Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_data_status(data_dir: Path) -> dict:
    """Check which tracks have been downloaded"""
    status = {}
    expected_counts = {
        'thlp': 19681,
        'ttm': 4931,
        'tagp': 17601,
        'tefb': 21081,
        'tscp': 2839,
    }
    
    print("
📊 DATA STATUS CHECK")
    print("="*60)
    
    for track in DATASETS.keys():
        track_dir = data_dir / track
        
        if not track_dir.exists():
            status[track] = {'exists': False, 'files': 0, 'rows': 0}
            print(f"  {track.upper():6}: ❌ Not downloaded")
            continue
        
        csv_files = list(track_dir.glob('*.csv'))
        
        if not csv_files:
            status[track] = {'exists': True, 'files': 0, 'rows': 0}
            print(f"  {track.upper():6}: ⚠️  No CSV files")
            continue
        
        # Count rows in first CSV
        try:
            import csv
            with open(csv_files[0], 'r') as f:
                row_count = sum(1 for _ in csv.reader(f)) - 1  # Exclude header
        except:
            row_count = 0
        
        status[track] = {'exists': True, 'files': len(csv_files), 'rows': row_count}
        expected = expected_counts.get(track, '?')
        match = "✅" if row_count == expected else "⚠️"
        print(f"  {track.upper():6}: {match} {row_count:,} rows ({len(csv_files)} files)")
    
    total_rows = sum(s['rows'] for s in status.values())
    print(f"
  TOTAL: {total_rows:,} / 65,133 expected rows")
    print("="*60)
    
    return status


def main():
    parser = argparse.ArgumentParser(
        description="Download Trinity Cognitive Probes datasets from Kaggle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all tracks
  python scripts/download_data.py
  
  # Download specific track
  python scripts/download_data.py --track thlp
  
  # Check what data is already downloaded
  python scripts/download_data.py --check-only
  
  # Download multiple tracks
  python scripts/download_data.py --tracks thlp ttm tscp
        """
    )
    
    parser.add_argument('--track', '--tracks', nargs='+',
                       choices=list(DATASETS.keys()) + ['all'],
                       default=['all'],
                       help='Track(s) to download')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check current data status')
    
    args = parser.parse_args()
    
    # Determine which tracks to process
    if 'all' in args.track:
        tracks_to_download = list(DATASETS.keys())
    else:
        tracks_to_download = args.track
    
    # Setup paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    
    # Check status only
    if args.check_only:
        check_data_status(data_dir)
        return
    
    # Full download workflow
    print("="*60)
    print("📥 TRINITY COGNITIVE PROBES - DATA DOWNLOAD")
    print("="*60)
    print(f"Tracks to download: {', '.join(tracks_to_download)}")
    print(f"Data directory: {data_dir}")
    
    # Check kaggle CLI
    try:
        result = subprocess.run(['kaggle', '--version'], capture_output=True, text=True)
        print(f"Kaggle CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("
❌ ERROR: Kaggle CLI not found")
        print("   Install with: pip install kaggle")
        print("   Get API key: https://www.kaggle.com/account")
        sys.exit(1)
    
    # Download each track
    success_count = 0
    for track in tracks_to_download:
        if download_track(track, data_dir):
            success_count += 1
    
    # Final status
    print("
" + "="*60)
    print(f"DOWNLOAD COMPLETE: {success_count}/{len(tracks_to_download)} tracks")
    print("="*60)
    
    check_data_status(data_dir)
    
    if success_count == len(tracks_to_download):
        print("
✅ All datasets downloaded successfully!")
        print("
Next steps:")
        print("  python scripts/evaluate.py --model claude --track thlp --sample 100")
    else:
        print("
⚠️  Some downloads failed. Check errors above.")


if __name__ == "__main__":
    main()

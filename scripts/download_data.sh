#!/bin/bash

# Download Trinity Cognitive Probes datasets from Kaggle

set -e

TRACKS=(
    "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc"
    "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc"
    "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc"
    "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tefb-mc"
    "https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc"
)

TRACK_NAMES=("thlp" "ttm" "tagp" "tefb" "tscp")

echo "Downloading Trinity Cognitive Probes datasets..."

for i in "${!TRACKS[@]}"; do
    TRACK="${TRACK_NAMES[$i]}"
    echo "Downloading $TRACK..."

    # Navigate to track page
    ~/.browseros/bin/browseros-cli nav "${TRACKS[$i]}"
    sleep 2

    # Find and click download button
    # This needs to be done interactively with BrowserOS
    # Alternative: use curl to download directly from Kaggle

    # Try to find download button in interactive elements
    # Element with text "Download" or containing "Download" in selector
    download_button=$(~/.browseros/bin/browseros-cli snap | grep -i "Download" | grep -o "clickable\]" | head -1 | sed 's/.*clickable.*/s|.*/p')

    if [ -n "$download_button" ]; then
        echo "Found download button: $download_button"
        ~/.browseros/bin/browseros-cli click "$download_button"
        sleep 3
    fi

    echo ""
    echo "Data structure:"
    echo "data/"
    echo "├── thlp/   # Pattern learning (19,681 questions)"
    echo "├── ttm/     # Metacognitive calibration (4,931 questions)"
    echo "├── tagp/    # Attention tasks (17,601 questions)"
    echo "├── tefb/    # Executive functions (21,081 questions)"
    echo "└── tscp/    # Social cognition (2,839 questions)"

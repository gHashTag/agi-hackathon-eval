#!/usr/bin/env python3
"""
Quick test script - evaluate a single question on a real model
For testing evaluation pipeline before hackathon
"""

import csv
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Question:
    id: str
    question_type: str
    question: str
    choices: list[str]
    answer: str


def load_sample_question(track: str) -> Question:
    """Load a sample question from data directory"""
    data_dir = Path(__file__).parent.parent / "data" / track
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"Error: No CSV files found in {data_dir}")
        return None

    # Use first CSV file
    csv_file = csv_files[0]

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        # Skip header, read first question
        next(reader)
        row = next(reader)

        return Question(
            id=row.get('id', ''),
            question_type=row.get('question_type', ''),
            question=row.get('question', ''),
            choices=[row.get('A', ''), row.get('B', ''), row.get('C', ''), row.get('D', '')],
            answer=row.get('answer', '')
        )


def print_test_prompt(question: Question, model: str):
    """Print formatted test prompt"""
    print(f"\n{'='*60}")
    print(f"Testing {model.upper()} on AGI Hackathon Question")
    print(f"{'='*60}")
    print(f"\nTrack: {question.question_type}")
    print(f"Question: {question.question}")
    print(f"\nChoices:")
    for i, choice in enumerate(question.choices):
        if choice:  # Only show non-empty choices
            print(f"  {['A', 'B', 'C', 'D'][i]}) {choice}")
    print(f"\nGround Truth: {question.answer} (do not share with model!)")
    print(f"{'='*60}\n")


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python3 test_single.py --track <thlp|ttm|tagp|tefb|tscp> --model <claude|gpt-4|gemini|glm-5>")
        print("\nExample:")
        print("  python3 test_single.py --track thlp --model claude")
        sys.exit(1)

    track = None
    model = None
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "--track":
            track = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--model":
            model = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not track:
        print("Error: --track is required")
        print("Valid tracks: thlp, ttm, tagp, tefb, tscp")
        sys.exit(1)

    if not model:
        print("Error: --model is required")
        print("Valid models: claude, gpt-4, gemini, glm-5")
        sys.exit(1)

    # Load sample question
    question = load_sample_question(track)

    if not question:
        print("Error: Could not load sample question")
        sys.exit(1)

    # Print test prompt
    print_test_prompt(question, model)

    print("Sample question loaded successfully!")
    print(f"To test with {model.upper()}, ensure API key is set:")
    if model == "claude":
        print("  export ANTHROPIC_API_KEY='your-key'")
    elif model == "gpt-4":
        print("  export OPENAI_API_KEY='your-key'")
    elif model == "gemini":
        print("  export GOOGLE_API_KEY='your-key'")
    elif model == "glm-5":
        print("  export ZHIPU_API_KEY='your-key'")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Analyze evaluation results from Trinity Cognitive Probes

Usage:
    python scripts/analyze_results.py runs/claude/claude_results.json
    python scripts/analyze_results.py runs/*/ --compare
    python scripts/analyze_results.py runs/ --generate-report
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


def load_results(result_path: Path) -> Dict:
    """Load results from JSON file"""
    with open(result_path, 'r') as f:
        return json.load(f)


def analyze_single(result_file: Path):
    """Analyze a single result file"""
    data = load_results(result_file)
    
    print(f"
{'='*70}")
    print(f"ANALYSIS: {result_file.name}")
    print(f"{'='*70}")
    
    summary = data.get('summary', {})
    
    # Overall stats
    total = summary.get('total_questions', 0)
    correct = summary.get('correct', 0)
    accuracy = summary.get('accuracy', 0)
    
    print(f"
📊 Overall Performance")
    print(f"   Questions: {total}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {accuracy:.2%}")
    
    # By track
    by_track = summary.get('by_track', {})
    if by_track:
        print(f"
📈 By Track")
        for track, stats in sorted(by_track.items()):
            acc = stats.get('accuracy', 0)
            count = stats.get('count', 0)
            print(f"   {track.upper():6}: {acc:.1%} ({count} questions)")
    
    # Calibration
    calibration = summary.get('calibration', {})
    if calibration:
        print(f"
🎯 Calibration Analysis")
        print(f"   Conf Range  | Accuracy | Expected | Calibration")
        print(f"   {'─'*50}")
        for conf_range, stats in sorted(calibration.items()):
            acc = stats.get('accuracy', 0)
            avg_conf = stats.get('avg_confidence', 0)
            expected = (int(conf_range.split('-')[0]) + int(conf_range.split('-')[1].rstrip('%'))) / 2
            cal_error = abs(acc - (expected / 100))
            status = "✅" if cal_error < 0.1 else "⚠️" if cal_error < 0.2 else "❌"
            print(f"   {conf_range:12} | {acc:7.1%} | {expected/100:7.1%} | {status}")
    
    # Detailed results
    results = data.get('results', [])
    if results:
        print(f"
🔍 Sample Results (first 3)")
        for r in results[:3]:
            status = "✅" if r.get('correct') else "❌"
            print(f"
   {status} {r.get('question_id')}")
            print(f"      Predicted: {r.get('predicted')} (conf: {r.get('confidence')}%)")
            print(f"      Reasoning: {r.get('reasoning', 'N/A')[:80]}...")


def compare_models(result_dir: Path):
    """Compare multiple model results"""
    print(f"
{'='*70}")
    print(f"MODEL COMPARISON")
    print(f"{'='*70}")
    
    all_results = {}
    
    # Find all result files
    for result_file in result_dir.rglob("*_results.json"):
        data = load_results(result_file)
        model = data.get('model', 'unknown')
        summary = data.get('summary', {})
        all_results[model] = summary
    
    if not all_results:
        print("❌ No results found")
        return
    
    # Print comparison table
    print(f"
{'Model':<15} {'Accuracy':<10} {'Questions':<10} {'Response Time'}")
    print(f"{'─'*70}")
    
    for model, summary in sorted(all_results.items()):
        acc = summary.get('accuracy', 0)
        total = summary.get('total_questions', 0)
        avg_time = summary.get('avg_response_time_ms', 0)
        print(f"{model:<15} {acc:>9.1%} {total:>9} {avg_time:>10.0f}ms")
    
    # Track-by-track comparison
    print(f"
{'─'*70}")
    print("By Track:")
    
    all_tracks = set()
    for summary in all_results.values():
        all_tracks.update(summary.get('by_track', {}).keys())
    
    for track in sorted(all_tracks):
        print(f"
  {track.upper()}:")
        for model, summary in sorted(all_results.items()):
            track_stats = summary.get('by_track', {}).get(track, {})
            acc = track_stats.get('accuracy', 0)
            count = track_stats.get('count', 0)
            if count > 0:
                print(f"    {model:<12}: {acc:>6.1%} ({count} questions)")


def generate_report(output_dir: Path):
    """Generate comprehensive evaluation report"""
    print(f"
{'='*70}")
    print(f"GENERATING EVALUATION REPORT")
    print(f"{'='*70}")
    
    report_lines = []
    report_lines.append("# Trinity Cognitive Probes - Evaluation Report
")
    report_lines.append(f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}

")
    
    # Load all results
    all_results = {}
    for result_file in output_dir.rglob("*_results.json"):
        data = load_results(result_file)
        model = data.get('model', 'unknown')
        summary = data.get('summary', {})
        all_results[model] = summary
    
    if not all_results:
        report_lines.append("❌ No evaluation results found.
")
        return
    
    # Executive summary
    report_lines.append("## Executive Summary
")
    report_lines.append(f"- **Models evaluated:** {len(all_results)}
")
    
    total_questions = sum(s.get('total_questions', 0) for s in all_results.values())
    report_lines.append(f"- **Total questions evaluated:** {total_questions:,}
")
    
    best_model = max(all_results.items(), key=lambda x: x[1].get('accuracy', 0))
    report_lines.append(f"- **Best performing model:** {best_model[0]} ({best_model[1].get('accuracy', 0):.1%})

")
    
    # Overall results
    report_lines.append("## Overall Results

")
    report_lines.append("| Model | Accuracy | Questions | Avg Response Time |
")
    report_lines.append("|-------|----------|-----------|-------------------|
")
    
    for model, summary in sorted(all_results.items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
        acc = summary.get('accuracy', 0)
        total = summary.get('total_questions', 0)
        avg_time = summary.get('avg_response_time_ms', 0)
        report_lines.append(f"| {model} | {acc:.1%} | {total:,} | {avg_time:.0f}ms |
")
    
    report_lines.append("
")
    
    # Track breakdown
    report_lines.append("## Results by Track

")
    
    all_tracks = set()
    for summary in all_results.values():
        all_tracks.update(summary.get('by_track', {}).keys())
    
    for track in ['thlp', 'ttm', 'tagp', 'tefb', 'tscp']:
        if track in all_tracks:
            report_lines.append(f"### {track.upper()}

")
            report_lines.append("| Model | Accuracy | Questions |
")
            report_lines.append("|-------|----------|-----------|
")
            
            for model, summary in sorted(all_results.items()):
                track_stats = summary.get('by_track', {}).get(track, {})
                acc = track_stats.get('accuracy', 0)
                count = track_stats.get('count', 0)
                if count > 0:
                    report_lines.append(f"| {model} | {acc:.1%} | {count} |
")
            
            report_lines.append("
")
    
    # Save report
    report_path = output_dir / "EVALUATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.writelines(report_lines)
    
    print(f"✅ Report saved to: {report_path}")
    print(f"
Preview:")
    print(f"{'─'*70}")
    print(''.join(report_lines[:30]))  # Show first 30 lines


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/analyze_results.py <result_file.json>")
        print("  python scripts/analyze_results.py <result_dir>/ --compare")
        print("  python scripts/analyze_results.py <result_dir>/ --generate-report")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if '--compare' in sys.argv:
        compare_models(path)
    elif '--generate-report' in sys.argv:
        generate_report(path)
    else:
        # Single file analysis
        if path.is_file():
            analyze_single(path)
        else:
            print(f"❌ File not found: {path}")


if __name__ == "__main__":
    main()

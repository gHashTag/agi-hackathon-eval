#!/usr/bin/env python3
"""
Evaluate Trinity Cognitive Probes on real LLMs
Measuring Progress Toward AGI Hackathon 2026

Usage:
    python3 scripts/evaluate.py --model claude --track thlp --sample 100
    python3 scripts/evaluate.py --model gpt-4 --track all
    python3 scripts/evaluate.py --model gemini --track ttm --sample 50
    python3 scripts/evaluate.py --model glm-5 --track tagp
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class Question:
    """Single MC question from Trinity Cognitive Probes"""
    id: str
    question_type: str
    question: str
    choices: List[str]
    answer: str


@dataclass
class EvaluationResult:
    """Result of evaluating a single question"""
    question_id: str
    track: str
    question_type: str
    predicted: str
    correct: bool
    confidence: float
    reasoning: str
    response_time_ms: float


class ModelEvaluator:
    """Base class for evaluating models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.results: List[EvaluationResult] = []
        self.system_prompt = self.load_system_prompt()

    def load_system_prompt(self) -> str:
        """Load system prompt from prompts directory"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompts.md"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                content = f.read()
                # Extract base system prompt
                match = re.search(r'## Base System Prompt.*?```(.*?)```',
                                content, re.DOTALL)
                if match:
                    return match.group(1).strip()

        # Fallback prompt
        return """You are an AI assistant participating in the "Measuring Progress Toward AGI" hackathon.
Answer multiple-choice questions with confidence and reasoning.

Format your response as:
---
Answer: [A|B|C|D]
Confidence: [0-100]
Reasoning: [Brief explanation]
---"""

    def format_prompt(self, question: Question, track: str) -> str:
        """Format question into prompt for model"""
        # Load track-specific prompt
        track_prompt = self.get_track_prompt(track)

        # Build choices text
        choices_text = "\n".join([
            f"{letter}) {choice}"
            for letter, choice in zip(['A', 'B', 'C', 'D'], question.choices)
            if choice  # Only include non-empty choices
        ])

        prompt = f"""{self.system_prompt}

{track_prompt}

Question Type: {question.question_type}

Question: {question.question}

Choices:
{choices_text}

Provide your answer in the exact format specified above."""

        return prompt

    def get_track_prompt(self, track: str) -> str:
        """Get track-specific prompt"""
        track_prompts = {
            'thlp': "This is a Pattern Learning question (THLP). Focus on identifying patterns, learning from examples, and inducing rules.",
            'ttm': "This is a Metacognitive Calibration question (TTM). Focus on confidence calibration, error detection, and meta-learning.",
            'tagp': "This is an Attention question (TAGP). Focus on selective filtering, sustained attention, and attention shifting.",
            'tefb': "This is an Executive Function question (TEFB). Focus on multi-step planning, working memory, and cognitive flexibility.",
            'tscp': "This is a Social Cognition question (TSCP). Focus on Theory of Mind, pragmatic inference, and social norms."
        }
        return track_prompts.get(track.lower(), "")

    def parse_response(self, text: str, question: Question, track: str, response_time_ms: float) -> EvaluationResult:
        """Parse model response to extract answer, confidence, reasoning"""
        # Extract answer (A, B, C, D)
        answer_match = re.search(r'Answer:\s*([A-D])', text, re.IGNORECASE)
        predicted = answer_match.group(1).upper() if answer_match else "A"

        # Extract confidence (0-100)
        conf_match = re.search(r'Confidence:\s*(\d+)', text)
        confidence = int(conf_match.group(1)) if conf_match else 50
        confidence = max(0, min(100, confidence))  # Clamp to 0-100

        # Extract reasoning
        reasoning_match = re.search(r'Reasoning:\s*(.+?)(?=\n\n|---|$)', text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"

        return EvaluationResult(
            question_id=question.id,
            track=track,
            question_type=question.question_type,
            predicted=predicted,
            correct=(predicted == question.answer),
            confidence=confidence,
            reasoning=reasoning[:500],  # Limit reasoning length
            response_time_ms=response_time_ms
        )

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate a list of questions - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement evaluate()")

    def save_results(self, output_dir: str, track: str = "all"):
        """Save evaluation results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) / f"{self.model_name}_{track}_{timestamp}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save detailed results
        with open(output_path, 'w') as f:
            json.dump({
                'model': self.model_name,
                'track': track,
                'timestamp': timestamp,
                'total_questions': len(self.results),
                'summary': self.get_summary(),
                'results': [asdict(r) for r in self.results]
            }, f, indent=2)

        print(f"\n✅ Results saved to {output_path}")
        self.print_summary()

    def get_summary(self) -> Dict:
        """Get evaluation summary statistics"""
        total = len(self.results)
        if total == 0:
            return {}

        correct = sum(1 for r in self.results if r.correct)

        # Per-track accuracy
        track_stats = {}
        for t in set(r.track for r in self.results):
            track_results = [r for r in self.results if r.track == t]
            track_correct = sum(1 for r in track_results if r.correct)
            track_stats[t] = {
                'accuracy': track_correct / len(track_results),
                'count': len(track_results)
            }

        # Per-question-type accuracy
        type_stats = {}
        for qtype in set(r.question_type for r in self.results):
            type_results = [r for r in self.results if r.question_type == qtype]
            type_correct = sum(1 for r in type_results if r.correct)
            type_stats[qtype] = {
                'accuracy': type_correct / len(type_results),
                'count': len(type_results)
            }

        # Calibration analysis
        confidence_bins = [(0, 30), (30, 50), (50, 70), (70, 90), (90, 100)]
        calibration = {}
        for low, high in confidence_bins:
            bin_results = [r for r in self.results if low <= r.confidence < high]
            if bin_results:
                bin_correct = sum(1 for r in bin_results if r.correct)
                calibration[f"{low}-{high}"] = {
                    'accuracy': bin_correct / len(bin_results),
                    'count': len(bin_results)
                }

        return {
            'accuracy': correct / total,
            'correct': correct,
            'total': total,
            'track_stats': track_stats,
            'type_stats': type_stats,
            'calibration': calibration
        }

    def print_summary(self):
        """Print evaluation summary"""
        summary = self.get_summary()

        print(f"\n{'='*60}")
        print(f"EVALUATION SUMMARY: {self.model_name.upper()}")
        print(f"{'='*60}")
        print(f"Total Questions: {summary['total']}")
        print(f"Correct: {summary['correct']}")
        print(f"Accuracy: {summary['accuracy']:.2%}")

        if 'track_stats' in summary:
            print(f"\n---BY TRACK---")
            for track, stats in summary['track_stats'].items():
                print(f"  {track.upper()}  : {stats['accuracy']:.2%} ({stats['count']} questions)")

        if 'calibration' in summary:
            print(f"\n---CALIBRATION---")
            for bin_name, stats in summary['calibration'].items():
                print(f"  {bin_name}%  : {stats['accuracy']:.2%} ({stats['count']} questions)")

        print(f"{'='*60}")


class ClaudeEvaluator(ModelEvaluator):
    """Evaluate using Claude via API"""

    def __init__(self, model_name: str = "claude"):
        super().__init__(model_name)

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using Claude API"""
        try:
            import anthropic
        except ImportError:
            print("Error: anthropic package not installed. Run: pip install anthropic")
            return []

        # Check for API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Error: ANTHROPIC_API_KEY not set")
            print("Set it with: export ANTHROPIC_API_KEY='your-key'")
            return []

        # Limit sample size
        if sample_size:
            questions = questions[:sample_size]

        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        iterator = HAS_TQDM and tqdm(questions, desc=f"Claude {track}") or questions

        for q in iterator:
            prompt = self.format_prompt(q, track)
            start_time = time.time()

            try:
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    temperature=0.0,
                    messages=[{"role": "user", "content": prompt}]
                )

                response_time = (time.time() - start_time) * 1000
                response_text = response.content[0].text

                result = self.parse_response(response_text, q, track, response_time)
                self.results.append(result)

            except Exception as e:
                print(f"Error evaluating question {q.id}: {e}")
                continue

        return self.results


class OpenAIEvaluator(ModelEvaluator):
    """Evaluate using OpenAI models (GPT-4, GPT-4o, etc.)"""

    def __init__(self, model_name: str = "openai"):
        super().__init__(model_name)

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using OpenAI API"""
        try:
            import openai
        except ImportError:
            print("Error: openai package not installed. Run: pip install openai")
            return []

        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not set")
            print("Set it with: export OPENAI_API_KEY='your-key'")
            return []

        # Limit sample size
        if sample_size:
            questions = questions[:sample_size]

        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        iterator = HAS_TQDM and tqdm(questions, desc=f"OpenAI {track}") or questions

        for q in iterator:
            prompt = self.format_prompt(q, track)
            start_time = time.time()

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=1024
                )

                response_time = (time.time() - start_time) * 1000
                response_text = response.choices[0].message.content

                result = self.parse_response(response_text, q, track, response_time)
                self.results.append(result)

            except Exception as e:
                print(f"Error evaluating question {q.id}: {e}")
                continue

        return self.results


class GeminiEvaluator(ModelEvaluator):
    """Evaluate using Google Gemini"""

    def __init__(self, model_name: str = "gemini"):
        super().__init__(model_name)

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using Gemini API"""
        try:
            import google.generativeai as genai
        except ImportError:
            print("Error: google-generativeai package not installed. Run: pip install google-generativeai")
            return []

        # Check for API key
        if not os.environ.get("GOOGLE_API_KEY"):
            print("Error: GOOGLE_API_KEY not set")
            print("Set it with: export GOOGLE_API_KEY='your-key'")
            return []

        # Limit sample size
        if sample_size:
            questions = questions[:sample_size]

        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')

        iterator = HAS_TQDM and tqdm(questions, desc=f"Gemini {track}") or questions

        for q in iterator:
            prompt = self.format_prompt(q, track)
            start_time = time.time()

            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.0,
                        max_output_tokens=1024,
                    )
                )

                response_time = (time.time() - start_time) * 1000
                response_text = response.text

                result = self.parse_response(response_text, q, track, response_time)
                self.results.append(result)

            except Exception as e:
                print(f"Error evaluating question {q.id}: {e}")
                continue

        return self.results


class GLM5Evaluator(ModelEvaluator):
    """Evaluate using Zhipu GLM-5 (experimental)"""

    def __init__(self, model_name: str = "glm-5"):
        super().__init__(model_name)

    def evaluate(self, questions: List[Question], track: str, sample_size: Optional[int] = None) -> List[EvaluationResult]:
        """Evaluate questions using GLM-5 API"""
        # Check for API key
        if not os.environ.get("ZHIPU_API_KEY"):
            print("Error: ZHIPU_API_KEY not set")
            print("Set it with: export ZHIPU_API_KEY='your-key'")
            print("\nGet API key from: https://open.bigmodel.cn/usercenter/apikeys")
            return []

        # Limit sample size
        if sample_size:
            questions = questions[:sample_size]

        # For GLM-5, we need to use Zhipu's API
        try:
            import requests
        except ImportError:
            print("Error: requests package not installed. Run: pip install requests")
            return []

        api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        headers = {
            "Authorization": f"Bearer {os.environ['ZHIPU_API_KEY']}",
            "Content-Type": "application/json"
        }

        iterator = HAS_TQDM and tqdm(questions, desc=f"GLM-5 {track}") or questions

        for q in iterator:
            prompt = self.format_prompt(q, track)
            start_time = time.time()

            try:
                payload = {
                    "model": "glm-5",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 1024
                }

                response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()

                response_time = (time.time() - start_time) * 1000
                response_data = response.json()

                if "choices" in response_data and len(response_data["choices"]) > 0:
                    response_text = response_data["choices"][0]["message"]["content"]
                else:
                    print(f"Error: Unexpected response from GLM-5 API")
                    continue

                result = self.parse_response(response_text, q, track, response_time)
                self.results.append(result)

            except Exception as e:
                print(f"Error evaluating question {q.id}: {e}")
                continue

        return self.results


def load_questions(track_dir: str) -> List[Question]:
    """Load MC questions from CSV file"""
    import csv

    questions = []
    path = Path(track_dir)

    # Find CSV file in directory
    csv_files = list(path.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {path}")
        return []

    csv_file = csv_files[0]

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append(Question(
                id=row.get('id', ''),
                question_type=row.get('question_type', ''),
                question=row.get('question', ''),
                choices=[row.get('A', ''), row.get('B', ''), row.get('C', ''), row.get('D', '')],
                answer=row.get('answer', '')
            ))

    print(f"Loaded {len(questions)} questions from {csv_file}")
    return questions


def main():
    """Main evaluation script"""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/evaluate.py --model <claude|openai|gemini|glm-5> --track <all|thlp|ttm|tagp|tefb|tscp> [--sample N]")
        print("\nExamples:")
        print("  python3 evaluate.py --model claude --track all --sample 100")
        print("  python3 evaluate.py --model openai --track ttm --sample 50")
        print("  python3 evaluate.py --model gemini --track tagp")
        print("  python3 evaluate.py --model glm-5 --track thlp")
        sys.exit(1)

    model = None
    track = None
    sample_size = None
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "--model":
            model = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--track":
            track = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--sample":
            sample_size = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    if not model:
        print("Error: --model is required")
        print("Options: claude, openai, gemini, glm-5")
        sys.exit(1)

    if not track:
        print("Error: --track is required")
        print("Options: all, thlp, ttm, tagp, tefb, tscp")
        sys.exit(1)

    # Create evaluator based on model
    evaluators = {
        'claude': ClaudeEvaluator,
        'openai': OpenAIEvaluator,
        'gemini': GeminiEvaluator,
        'glm-5': GLM5Evaluator
    }

    if model not in evaluators:
        print(f"Error: Unknown model '{model}'")
        print(f"Valid models: {', '.join(evaluators.keys())}")
        sys.exit(1)

    evaluator = evaluators[model]()

    # Load questions
    base_dir = Path(__file__).parent.parent / "data"

    tracks_to_run = []
    if track == "all":
        tracks_to_run = ["thlp", "ttm", "tagp", "tefb", "tscp"]
    else:
        tracks_to_run = [track]

    print(f"\n{'='*60}")
    print(f"Running evaluations for: {evaluator.model_name}")
    print(f"Tracks: {', '.join(tracks_to_run)}")
    print(f"{'='*60}\n")

    for t in tracks_to_run:
        track_dir = base_dir / t
        if not track_dir.exists():
            print(f"Warning: Track directory {track_dir} not found, skipping...")
            continue

        print(f"\nEvaluating track: {t}")
        questions = load_questions(str(track_dir))

        if questions:
            results = evaluator.evaluate(questions, t, sample_size)
            evaluator.results.extend(results)

    # Save results
    if evaluator.results:
        evaluator.save_results("runs", track)


if __name__ == "__main__":
    main()

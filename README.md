# AGI Hackathon Evaluation Framework

Google DeepMind x Kaggle "Measuring Progress Toward AGI: A Cognitive Framework" Hackathon 2026

## 📊 Overview

Evaluation scripts for the AGI Hackathon with support for:
- **Claude** (Anthropic)
- **GPT-4/GPT-4o** (OpenAI)
- **Gemini** (Google DeepMind)
- **glm-5** (Zhipu AI) - experimental

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/gHashTag/agi-hackathon-eval.git
cd agi-hackathon-eval

# Install dependencies
pip install -r requirements.txt

# Set API keys (choose one or all)
export ANTHROPIC_API_KEY="your-claude-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
export ZHIPU_API_KEY="your-zhipu-api-key"  # For glm-5

# Run evaluation
python3 scripts/evaluate.py --model claude --track all --sample 100
```

## 📁 Project Structure

```
agi-hackathon-eval/
├── README.md                      # This file
├── requirements.txt                 # Python dependencies
├── scripts/                          # Evaluation scripts
│   ├── evaluate.py               # Main evaluation runner
│   ├── test_single.py           # Single question tester
│   ├── analyze_results.py        # Results analysis
│   └── glm5_evaluator.py        # GLM-5 integration (experimental)
└── prompts/                         # Evaluation prompts
    ├── system_prompts.md         # Base system prompts
    └── track_prompts.md           # Track-specific prompts
```

## 🎯 Supported Models

| Model | Provider | API Key | Cost per 1K Questions |
|-------|----------|----------------------|
| **Claude 3.5 Sonnet** | Anthropic | `ANTHROPIC_API_KEY` | ~$3.00 |
| **GPT-4o** | OpenAI | `OPENAI_API_KEY` | ~$0.15 |
| **Gemini 1.5 Flash** | Google | `GOOGLE_API_KEY` | ~$0.08 |
| **glm-5** | Zhipu AI | `ZHIPU_API_KEY` | ~? (RMB pricing) |

## 📊 Kaggle Datasets

| Track | Dataset | Questions | Status |
|-------|---------|-----------|--------|
| THLP | [trinity-cognitive-probes-thlp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc) | 19,681 | ✅ Ready |
| TTM | [trinity-cognitive-probes-ttm-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-ttm-mc) | 4,931 | ✅ Ready |
| TAGP | [trinity-cognitive-probes-tagp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tagp-mc) | 17,601 | ✅ Ready |
| TEFB | [trinity-cognitive-probes-tefb-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-thlp-mc) | 21,081 | ✅ Ready |
| TSCP | [trinity-cognitive-probes-tscp-mc](https://www.kaggle.com/datasets/playra/trinity-cognitive-probes-tscp-mc) | 2,839 | ✅ Ready |

**Total:** 65,133 MC questions

## 🧪 Test Locally

```bash
# Test single question
python3 scripts/test_single.py --track thlp --model claude

# Test with sample (100 questions)
python3 scripts/evaluate.py --model claude --track thlp --sample 100

# Test all models on single track
python3 scripts/evaluate.py --model all --track ttm --sample 50
```

## 📈 Results

Results are saved in `runs/` directory:
- `runs/claude/` — Claude evaluation results
- `runs/openai/` — GPT-4 results
- `runs/gemini/` — Gemini results
- `runs/glm5/` — GLM-5 results (experimental)

## 🔬 Citation

```bibtex
@online{AGI Hackathon 2026},
  title={Measuring Progress Toward AGI: A Cognitive Framework Benchmark},
  author={{Vasilev, Dmitrii} and {Zhuang, Jiaming}},
  booktitle={Kaggle: The World's AI Proving Ground},
  year={2026},
  publisher={Google DeepMind},
  url={https://github.com/gHashTag/agi-hackathon-eval}
}
```

## 📄 License

MIT License

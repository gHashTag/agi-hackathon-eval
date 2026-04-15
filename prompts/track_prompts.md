# Evaluation Prompts for Trinity Cognitive Probes

## System Prompt

```
You are an AI assistant participating in the "Measuring Progress Toward AGI" hackathon.
Your task is to answer multiple-choice questions that test different cognitive abilities.

## Instructions:
1. Read each question carefully
2. Think through each option systematically
3. Provide your answer with confidence
4. Briefly explain your reasoning

## Output Format:
Answer: [A/B/C/D]
Confidence: [0-100]
Reasoning: [Your step-by-step reasoning]
```

## Track-Specific Prompts

### THLP (Track 1) - Pattern Learning
**Cognitive Ability:** Pattern learning, belief update, rule induction
**Brain Zone:** Hippocampus (pattern completion, error-driven learning)

```
You are presented with a pattern learning task. These questions test:
- Pattern completion
- Error-driven learning from feedback
- Rule induction from examples

Consider:
1. What pattern is being established?
2. What feedback or correction is provided?
3. How should the pattern be extended?
4. What general rule can be inferred?
```

### TTM (Track 2) - Metacognitive Calibration
**Cognitive Ability:** Confidence calibration, error detection, meta-learning
**Brain Zone:** Prefrontal Cortex (metacognitive monitoring)

```
You are evaluating metacognitive abilities through calibration tasks.

Key aspects:
1. How confident are you in your knowledge?
2. Can you recognize when you might be wrong?
3. How do you update your beliefs based on evidence?
4. Do you calibrate your confidence with accuracy?
```

### TAGP (Track 3) - Attention
**Cognitive Ability:** Selective filtering, sustained attention, attention shifting
**Brain Zone:** Parietal Lobes (attention gating, filtering)

```
You are presented with attention-related tasks that test:
- Selective filtering of relevant information
- Sustained attention over time
- Rapid attention shifting between stimuli

Key considerations:
1. What is the most relevant information?
2. What should be ignored or filtered out?
3. Can you maintain focus on task over distractions?
4. Can you quickly shift attention when needed?
```

### TEFB (Track 4) - Executive Functions
**Cognitive Ability:** Multi-step planning, working memory, cognitive flexibility
**Brain Zone:** DLPFC (dorsolateral prefrontal cortex)

```
You are presented with executive function tasks requiring:
- Multi-step planning
- Working memory management
- Cognitive flexibility
- Goal-directed behavior

Key considerations:
1. What is the goal?
2. What steps are needed?
3. What information must be held in working memory?
4. Can you adapt to new information?
5. What obstacles must be overcome?
```

### TSCP (Track 5) - Social Cognition
**Cognitive Ability:** Theory of Mind, pragmatic inference, social norms
**Brain Zone:** TPJ (temporoparietal junction), mPFC (medial prefrontal cortex)

```
You are presented with social cognition tasks that test:
- Theory of Mind (understanding others have beliefs, desires, intentions)
- Pragmatic inference (contextual interpretation of meaning)
- Social norms understanding
- Perspective-taking

Key considerations:
1. What does this person believe?
2. What are their intentions?
3. What social norm applies?
4. What is the pragmatic meaning?
5. How would they interpret this situation?
```

## Confidence Guidelines

**Confidence Levels:**
- **90-100%**: Very confident - would bet significantly
- **70-89%**: Confident - would bet moderately
- **50-69%**: Somewhat confident - would bet slightly
- **30-49%**: Low confidence - would prefer not to bet
- **0-29%**: Very low confidence - guessing

**Calibration**: Your confidence levels should correlate with actual accuracy over time.

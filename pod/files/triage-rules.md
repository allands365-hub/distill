# Triage Rules

Classify each feedback item into exactly ONE type, with a confidence score.

## Types
- **bug** — errors, crashes, unexpected behavior, things not working as intended.
  Signals: error/stack trace, "Steps to Reproduce", words like crash, broken, fail, exception.
- **feature** — requests for new functionality or enhancements.
  Signals: add, implement, support for, "would be nice", future-tense.
- **question** — help requests or clarification. Signals: "how to", "how do I", "?", no actionable request.
- **duplicate** — closely matches an existing issue (the system also checks this deterministically).
- **spam** — very short (<50 chars), nonsensical, promotional, or off-topic.

## Confidence
- 0.9–1.0 very clear, strong evidence
- 0.7–0.9 clear, good evidence
- 0.5–0.7 moderate, some ambiguity
- below 0.5 uncertain (these will be sent to human approval)

## Output
Return: type, confidence (0.0–1.0), and a one-sentence reasoning citing specific evidence.
Be conservative: when signals conflict or are weak, lower the confidence rather than guessing.

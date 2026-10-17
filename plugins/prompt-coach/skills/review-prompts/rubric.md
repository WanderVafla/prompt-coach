# Rubric v1

Source: Jobtrek course "Utiliser une IA, 3. Levier ou béquille". Everyone is
graded by this same text, so scores stay comparable. Bump `rubric_version` in
`rules/patterns.json` whenever this file changes meaning.

## The one question

Does the user want to **learn** or to **get a result**? Both are fine.
The only real fault is *cognitive surrender*: taking the AI's answer as one's own
without examining it.

Grade each prompt by the mode of its project (`mode` in the data), never by one
standard for all.

## 🎓 Learning mode: the AI makes the user work

| ID | Rule | Good sign | Bad sign |
|---|---|---|---|
| R1 | Try first | own code, draft or hypothesis before asking | "how do I fix it?" with nothing of one's own |
| R2 | Hint, not solution | "tell me where to look, don't fix it" | "give me the full code" |
| R3 | Explain in own words | "did I get it right that… where am I wrong?" | reading an explanation and moving on |
| R4 | Hypothesis before check | "I changed X because I think Y, check only that" | "I fixed it, check again" in a loop |
| R5 | Check it myself | "give me the command to test it" | the AI as the only test runner |
| R6 | Texts for people are mine | own draft of PR / commit / mail / speech, AI critiques | "write the PR body" |
| R7 | Understand the critique first | "explain this review comment, I think the fix is…" | pasting a reviewer's comment + "how to fix?" |

Also count as strong: asking *why*, asking for sources, quizzes, "explain each word".

## 🛠️ Tool mode: the AI does the work, the user keeps control

Delegating is fine. Grade the user as architect and client.

| ID | Rule | Good sign | Bad sign |
|---|---|---|---|
| T1 | Value before completeness | the roughest version that is used this week | building stage after stage with no output in use |
| T2 | What is mine, how is the agent's | goals and decisions given, plan asked for and validated | guesses about the code written into the prompt |
| T3 | Done criteria | "done = tests pass + run on real examples" | no way to tell a stage is finished |
| T4 | Reproducible bug reports | did → got → expected → already checked | "doesn't work, check" |
| T5 | Understand the architecture | asks for the data flow, can explain modules | no idea what each part does |
| T6 | Automate repetition | repeated requests moved to CLAUDE.md, commands, skills | the same instruction typed again and again |
| T7 | Control over actions | branches, no push / merge / spending without a yes | the agent acts outside what was asked |
| T8 | Measure usefulness | checks whether the tool saves time | never checks |

## Scale 1–12

Score the share and weight of good versus bad prompts, not their count. Short
replies ("yes", "go on", "ok") are neutral.

| Score | Meaning |
|:-:|---|
| 11–12 | Rules are habits. Bad prompts are rare and minor. |
| 9–10 | Mostly lever. A few repeated slips (for example an R4 loop). |
| 7–8 | Mixed. Good in some projects, crutch in others. |
| 5–6 | Mostly crutch in learning, or no control in tool mode. |
| 3–4 | Work handed over almost entirely, little own thinking. |
| 1–2 | Cognitive surrender: answers passed on unexamined. |

- `score_learning`: learning-mode prompts only. `score_tool`: tool-mode prompts only.
  Leave a mode at `null` if it has fewer than 5 prompts.
- `score`: the overall grade, weighted by how many prompts each mode has.

## Deterministic signals

`signals`, `signal_rate` and `rule_hits` come from regex patterns, not from
judgement. They over-match (a prompt with a real hypothesis may still contain
"check again"). Use them to find prompts to read, never as the grade itself.
`overrides` counts prompts starting with `#tool` in learning projects: many of
them mean the learning label does not fit, or deadlines are eating the learning.

# Ideate Skill

Capture a lightning idea through interactive dialogue and generate IDEA.md.

## Arguments

- `$ARGUMENTS` - One of the following:
  - (empty) - Start fresh ideation dialogue
  - `refine` - Refine existing IDEA.md
  - `"your idea here"` - Start with an initial idea

## Objective

Help users transform a vague concept into a structured IDEA.md through Socratic dialogue. Extract the core vision without overwhelming with details. Keep it to 5-6 exchanges maximum.

---

## Execution Steps

### Step 1: Check Existing State

1. **Check for IDEA.md**:
   - If exists and `$ARGUMENTS` is empty: Ask if user wants to refine or start fresh
   - If exists and `$ARGUMENTS` is `refine`: Load and proceed to Refinement Mode
   - If not found: Proceed to Step 2

2. **Check for initial idea in arguments**:
   - If `$ARGUMENTS` contains text (not `refine`): Use as starting point for Step 3

### Step 2: Opening Dialogue

Present the opening prompt:

```
## Let's Capture Your Idea

I'll help you turn a rough concept into a clear project idea.

Tell me about your idea in whatever way feels natural:
- A single sentence is fine
- Or describe the problem you want to solve
- Or share who would use this and why

Don't worry about structure or completeness - just share what's in your head.
```

**Wait for user response before continuing.**

### Step 3: Core Extraction (The Why)

Based on user's response, acknowledge their idea and ask clarifying questions.

**Round 1 Questions** (ask 1-2 based on what's missing):

| If Missing | Ask |
|------------|-----|
| Problem clarity | "What specific problem does this solve?" |
| Target user | "Who would use this? Can you describe them?" |
| Motivation | "What happens today without this? What's painful about it?" |

Present as natural conversation, not interrogation:

```
## I Think I Understand

[Restate what you understood in 1-2 sentences]

To make sure I've got it right:
- [Question 1]
- [Question 2 if needed]
```

**Wait for user response.**

### Step 4: Core Extraction (The What)

**Round 2 Questions** (ask 1-2 based on what's missing):

| If Missing | Ask |
|------------|-----|
| Core features | "What are the 2-3 things this absolutely must do?" |
| Scope limits | "What should this NOT do? Any boundaries?" |
| Tech preferences | "Any technology preferences or constraints I should know about?" |

```
## Getting Clearer

[Acknowledge new information]

A couple more questions:
- [Question 1]
- [Question 2 if needed]

Or if you feel we have enough, just say "that's enough" and I'll draft the idea.
```

**Wait for user response.**

### Step 5: Handle User Responses

| User Response | Action |
|---------------|--------|
| Detailed answer | Extract info, move to next step or Step 6 |
| Brief/vague answer | Accept it, fill gaps with reasonable defaults |
| "I don't know" | Skip that aspect, note as "To be determined" |
| "that's enough" / "done" | Move directly to Step 6 |
| Asks question back | Answer helpfully, then continue extraction |
| Goes off-topic | Gently redirect to the idea |

### Step 6: Present Draft IDEA.md

Synthesize everything into a draft:

```markdown
## Here's What I've Captured

Based on our conversation, here's your idea:

---

# [Project Name - inferred from conversation]

## One-Liner
[Synthesized summary - one sentence]

## The Problem
[Problem statement from dialogue]

## Core Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Tech Preferences
[From dialogue, or "Not specified - to be decided during /init-project"]

## Notes
[Any constraints or context mentioned]

---

### How does this look?

- **save** - Create IDEA.md with this content
- **adjust [section]** - Modify a specific section (e.g., "adjust features")
- **add [detail]** - Add something I missed
- **restart** - Start over from scratch
```

### Step 7: Handle Feedback Loop

| User Response | Action |
|---------------|--------|
| "save" / "looks good" / "yes" | Proceed to Step 8 |
| "adjust [section]" | Ask what to change, update draft, re-present |
| "add [detail]" | Incorporate, re-present draft |
| "restart" | Go back to Step 2 |
| Provides corrections | Update draft, re-present |

### Step 8: Save and Guide Next Steps

1. **Write IDEA.md** to project root

2. **Present completion message**:

```
## IDEA.md Created!

Your idea has been saved to IDEA.md at the project root.

### What's Next?

**Ready to elaborate?**
Run `/init-project` to:
- Analyze and enhance your requirements
- Identify gaps and edge cases
- Generate AI-DLC specification documents
- Create project development skills

**Want to refine more?**
Run `/ideate refine` to adjust or expand your idea.

**Just exploring?**
That's fine too - IDEA.md is ready whenever you are.
```

---

## Refinement Mode

When `$ARGUMENTS` is `refine`:

### Step R1: Load and Analyze

1. Read existing IDEA.md
2. Identify what's well-defined vs vague

### Step R2: Present Analysis

```
## Current IDEA.md Analysis

**What's Clear:**
- [Well-defined aspects]

**Could Be Stronger:**
- [Vague or missing aspects]

**What would you like to refine?**
- **one-liner** - Sharpen the summary
- **problem** - Clarify the problem statement
- **features** - Adjust the feature list
- **tech** - Update technology preferences
- **all** - Full review of everything
- **done** - Keep as is
```

### Step R3: Guided Refinement

Based on user's choice, ask targeted questions for that section only.

After refinement, update IDEA.md and confirm.

---

## Dialogue Guidelines

### Principles

1. **Accept vagueness** - Don't force precision too early
2. **One question at a time** - For complex topics
3. **Extract, don't suggest** - Pull ideas from user, don't impose
4. **Keep it short** - 5-6 exchanges maximum
5. **Allow early exit** - "done" or "enough" always works

### Tone

- Curious, not interrogating
- Supportive, not judgmental
- Concise, not verbose

### When to Fill Gaps

If user can't answer something, use reasonable defaults:
- Tech preferences → "To be decided"
- Specific features → Keep it high-level
- Constraints → Note as "None specified"

---

## Error Handling

| Situation | Response |
|-----------|----------|
| User provides nothing | Re-prompt with examples of what they could share |
| IDEA.md exists, user says "save" | Confirm before overwriting |
| User seems confused | Offer to restart or explain the process |
| Very complex idea | Suggest focusing on MVP, note rest as "future" |

---

## Example Invocations

Start fresh ideation:
```
/ideate
```

Start with an initial idea:
```
/ideate I want to build a habit tracking app
```

Refine existing idea:
```
/ideate refine
```

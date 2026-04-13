# Refinement Questions: Reel-Mind

**Date**: 2026-04-13

## Target User & Monetization
Q1: Who is this for — solo operator with a channel portfolio, or a product others will use?
[Answer]: Portfolio of monetized channels (solo operator).

Q2: What is the success metric?
[Answer]: Ad/affiliate earnings, ~$1,000/month.

Q3: Is the content niche locked or trend-chosen?
[Answer]: Anything the trend-scout picks, BUT an account is fixed to a subject.

Q4: Is the approval gate required from day one?
[Answer]: Required initially; configurable off per channel later.

## Tech Stack
Q5: Video generation strategy — asset-assembly, generative, or hybrid?
[Answer]: C — hybrid.

## Architecture
Q6: Pipeline topology?
[Answer]: User proposed decoupling style-study from content-production; Claude expanded to three pipelines — A (style study), B (content production incl. trend-scout), C (measure & learn).

Q7: Is a Web UI needed?
[Answer]: Yes, required for observability and approval actions; complements Telegram.

## MVP Scoping
Q8: MVP platform?
[Answer]: YouTube Shorts only.

Q9: Channels at launch?
[Answer]: 1 channel.

Q10: Generative-video monthly budget cap per channel?
[Answer]: $20/channel/month.

Q11: Timezone and language?
[Answer]: KST; Korean-language shorts first.

Q12: Affiliate strategy?
[Answer]: C — decide per-channel later.

## Extension Opt-Ins
Q13: Security extension?
[Answer]: A — Yes, enforce as blocking constraints.

Q14: Property-based testing extension?
[Answer]: A — Yes, full enforcement.

## Ambiguity Resolutions
- User's "Yes" in Round 3 was ambiguous about whether it applied to the MVP scoping suggestion. Follow-up in Round 4 resolved each of the 5 scoping questions + 2 extensions explicitly. No remaining vague answers.

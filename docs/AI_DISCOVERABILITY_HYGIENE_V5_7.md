# AIVisibilityAuditor v5.7 — AI Discoverability Hygiene

The report builder consumes `site_ai_hygiene` from the Evidence Service compact bundle.

## Signals
- robots.txt status
- llms.txt status
- JSON-LD / schema coverage across audited owned pages
- Pages missing structured data signals

## Outputs
- `executive.ai_discoverability_hygiene`
- top-level `ai_discoverability_hygiene` and `site_ai_hygiene`
- technical hygiene actions in `action_checklist`
- mapped owned URL `technical_signals`

## Policy
LLMs.txt is treated as an emerging AI-crawler guidance layer, not as a mandatory ranking requirement. Robots.txt and structured data coverage are treated as core discoverability and extractability controls.

# Journey taxonomy propagation

v5.3 preserves synthetic portfolio taxonomy from the Railway evidence bundle into the canonical frontend report.

The builder now indexes query metadata from `query_portfolio`, `audit_context`, `evidence_scope`, `visibility`, `ai_visibility_scores`, and `google_ai_mode_compact`, then merges it back into the row used to build `query_workbench`.

Canonical fields carried through:

- `topic_id`
- `topic`
- `brand_topic`
- `journey_stage`
- `journey_category`
- `intent`
- `priority`
- `recommended_page_type`
- `brand_relevance`
- `reason_selected`
- `expected_ai_answer_source_types`
- `market_localisation_notes`

This prevents compact Google AI Mode rows from overwriting richer synthetic portfolio metadata and producing `Unclassified` journey categories.

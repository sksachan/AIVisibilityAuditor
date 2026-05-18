# SerpAPI citation contract v5.4

This version consumes Evidence Service v3.4.7 citation fields from `google_ai_mode_compact`, `evidence_scope.ai_citations`, `evidence_scope.external_sources`, and `source_classification.sources`. It expands source-level `queries[]` back into query-level citations so Query Workbench, Visibility & Sources, and grouped PR views can populate when SerpAPI returns references.

CMS/report language defaults to English. Japan-market terms may be preserved as local evidence labels, but generated dashboard copy should not switch to Japanese unless explicitly requested.

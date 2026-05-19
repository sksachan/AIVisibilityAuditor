from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_hygiene import attach_ai_discoverability_hygiene, build_ai_discoverability_hygiene


class AiDiscoverabilityHygieneTests(unittest.TestCase):
    def test_existing_explicit_hygiene_is_preserved_and_mirrored(self):
        explicit = {
            "priority": "medium",
            "summary": "Explicit hygiene from evidence.",
            "robots_txt": {"status": "available", "url": "https://example.com/robots.txt", "sitemap_entries_count": 2},
            "llms_txt": {"status": "available", "url": "https://example.com/llms.txt", "chars": 123},
            "structured_data": {
                "owned_pages_total": 3,
                "pages_with_schema": 2,
                "pages_with_json_ld": 2,
                "coverage_pct": 66.7,
                "schema_types_detected": [["Product", 2]],
            },
        }
        bundle = {"ai_discoverability_hygiene": explicit}

        attach_ai_discoverability_hygiene(bundle)

        self.assertEqual(bundle["ai_discoverability_hygiene"], explicit)
        self.assertEqual(bundle["site_ai_hygiene"], explicit)

    def test_no_explicit_crawl_signals_is_not_checked_not_fake_zero(self):
        bundle = {
            "owned_url_readiness": [
                {
                    "url": "https://example.com/a",
                    "title": "A",
                    "geo_dimensions": {"structured_data": 20},
                }
            ]
        }

        hygiene, source = build_ai_discoverability_hygiene(bundle)

        self.assertEqual(source, "not_checked_fallback")
        self.assertEqual(hygiene["robots_txt"]["status"], "not checked")
        self.assertEqual(hygiene["llms_txt"]["status"], "not checked")
        self.assertIn("not fully checked", hygiene["summary"])
        self.assertEqual(hygiene["structured_data"]["owned_pages_total"], 1)
        self.assertEqual(hygiene["structured_data"]["pages_with_json_ld"], 0)
        self.assertEqual(hygiene["structured_data"]["coverage_pct"], 0)

    def test_geo_dimensions_structured_data_does_not_affect_json_ld_counts(self):
        bundle = {
            "owned_url_readiness": [
                {
                    "url": "https://example.com/a",
                    "geo_dimensions": {"structured_data": 20},
                },
                {
                    "url": "https://example.com/b",
                    "json_ld_present": True,
                    "schema_types": ["Product"],
                    "geo_dimensions": {"structured_data": 0},
                },
            ]
        }

        hygiene, source = build_ai_discoverability_hygiene(bundle)

        self.assertEqual(source, "derived_from_explicit_crawl_signals")
        self.assertEqual(hygiene["structured_data"]["owned_pages_total"], 2)
        self.assertEqual(hygiene["structured_data"]["pages_with_json_ld"], 1)
        self.assertEqual(hygiene["structured_data"]["pages_with_schema"], 1)
        self.assertEqual(hygiene["structured_data"]["coverage_pct"], 50.0)
        self.assertEqual(hygiene["structured_data"]["schema_types_detected"], [["Product", 1]])

    def test_checked_pages_with_no_json_ld_are_real_zero_coverage(self):
        bundle = {
            "owned_url_readiness": [
                {"url": "https://example.com/a", "json_ld_present": False},
                {"url": "https://example.com/b", "json_ld_block_count": 0},
            ]
        }

        hygiene, source = build_ai_discoverability_hygiene(bundle)

        self.assertEqual(source, "derived_from_explicit_crawl_signals")
        self.assertEqual(hygiene["structured_data"]["owned_pages_total"], 2)
        self.assertEqual(hygiene["structured_data"]["pages_with_json_ld"], 0)
        self.assertEqual(hygiene["structured_data"]["coverage_pct"], 0.0)
        self.assertEqual(len(hygiene["structured_data"]["pages_missing_json_ld"]), 2)

    def test_builder_writes_both_top_level_hygiene_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            input_path = project / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "schema_version": "query_workbench.v1",
                        "contract_version": "page_level_cms_grouped_pr.v2",
                        "brand": "Example",
                        "market": "US",
                        "domain": "https://example.com",
                        "query_workbench": [
                            {
                                "query_id": "q001",
                                "query": "example ev range",
                                "current_ai_visibility": {
                                    "score": 0,
                                    "status": "not_observed",
                                    "top_citations": [],
                                },
                                "mapped_owned_urls": [],
                            }
                        ],
                        "owned_url_readiness": [
                            {
                                "url": "https://example.com/a",
                                "title": "A",
                                "json_ld_present": False,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_query_workbench_bundle.py"),
                    "--project-root",
                    str(project),
                    "--input-json",
                    str(input_path),
                    "--brand",
                    "Example",
                    "--market",
                    "US",
                    "--domain",
                    "https://example.com",
                ],
                cwd=str(ROOT),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            bundle = json.loads((project / "outputs" / "frontend_report_bundle.json").read_text(encoding="utf-8"))
            self.assertIn("ai_discoverability_hygiene", bundle)
            self.assertIn("site_ai_hygiene", bundle)
            self.assertEqual(bundle["site_ai_hygiene"], bundle["ai_discoverability_hygiene"])


if __name__ == "__main__":
    unittest.main()

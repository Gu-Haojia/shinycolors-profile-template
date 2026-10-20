"""Template onboarding and deployment boundaries; all tests are offline."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build


class IdentityTests(unittest.TestCase):
    def test_each_template_owner_gets_their_own_identity(self):
        for owner in ("Alice", "another-developer"):
            with self.subTest(owner=owner), patch.dict(os.environ, {"GITHUB_REPOSITORY_OWNER": owner}, clear=True):
                self.assertEqual(build.resolve_identity({"github": "auto"})["github"], owner)
                self.assertEqual(build.resolve_identity({"github": "fixed"})["github"], "fixed")
                self.assertEqual(build.resolve_identity({"github": "fixed"}, username=owner)["github"], owner)

    def test_local_auto_identity_requires_username(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "--username"):
                build.resolve_identity({"github": "auto"})
            self.assertEqual(build.resolve_identity({}, demo=True)["github"], "demo-producer")
        with self.assertRaises(ValueError):
            build.resolve_identity({"github": 'bad") {query}'})

    def test_wrong_owner_cache_cannot_leak_into_an_offline_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "stats.json"
            cache.write_text(json.dumps({"github": "Alice", "stars": 999}))
            with patch.object(build, "CACHE", cache):
                with self.assertRaisesRegex(ValueError, "当前账号"):
                    build.load_stats({"github": "Bob"}, True)
                self.assertEqual(build.load_stats({"github": "alice"}, True)["stars"], 999)

    def test_first_live_failure_never_generates_a_fake_zero_profile(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"GITHUB_TOKEN": "test"}):
            with patch.object(build, "CACHE", Path(tmp) / "stats.json"), \
                 patch.object(build, "fetch", side_effect=RuntimeError("unavailable")):
                with self.assertRaises(RuntimeError):
                    build.load_stats({"github": "Alice"}, False)

    def test_refresh_replaces_old_optional_values(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"GITHUB_TOKEN": "test"}):
            cache = Path(tmp) / "stats.json"
            cache.write_text(json.dumps({"github": "Alice", "last_commit": {"repo": "Deleted"}}))
            with patch.object(build, "CACHE", cache), \
                 patch.object(build, "fetch", return_value={"github": "Alice", "stars": 3}):
                result = build.load_stats({"github": "Alice"}, False)
                self.assertNotIn("last_commit", result)
                self.assertEqual(json.loads(cache.read_text()), result)


class ReadmeTests(unittest.TestCase):
    def test_preserve_keeps_docs_and_replaces_only_preview(self):
        original = "# Guide\nIntro\n<!-- SHINY:START -->old<!-- SHINY:END -->\nSetup"
        updated = build.update_readme(original, "<img>new</img>\n", "preserve")
        self.assertEqual(updated, "# Guide\nIntro\n<!-- SHINY:START -->\n<img>new</img>\n<!-- SHINY:END -->\nSetup")

    def test_profile_and_ordinary_repositories_choose_the_right_mode(self):
        original = "# Guide\n<!-- SHINY:START -->old<!-- SHINY:END -->"
        for repository, preserves in [("Alice/alice", False), ("Alice/portfolio", True),
                                      ("Gu-Haojia/shinycolors-profile-template", True)]:
            with self.subTest(repository=repository), patch.dict(os.environ, {"GITHUB_REPOSITORY": repository}):
                result = build.update_readme(original, "new")
                self.assertEqual("# Guide" in result, preserves)
                self.assertIn("new", result)

    def test_bad_markers_are_rejected_without_dropping_documentation(self):
        for md in ("<!-- SHINY:START -->", "<!-- SHINY:END --><!-- SHINY:START -->"):
            with self.assertRaises(ValueError):
                build.update_readme(md, "new", "preserve")


class AutoProjectTests(unittest.TestCase):
    def test_auto_selection_and_home_exclude_both_profile_and_build_repo(self):
        stats = {
            "repo_meta": {
                "Alice": [1, "Python", "", "2026-10-20T00:00:00Z"],
                "portfolio": [2, "Python", "", "2026-10-20T00:00:00Z"],
                "Recent": [3, "Python", "", "2026-10-19T00:00:00Z"],
                "Older": [4, "Python", "", "2026-09-01T00:00:00Z"],
            },
        }
        stats["repo_commits"] = {k: {"at": v[3], "sha": "abc"} for k, v in stats["repo_meta"].items()}
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "Alice/portfolio"}):
            result = build.derive({"github": "Alice", "projects": {"items": None, "limit": 1}}, stats)
        self.assertEqual([x["repo"] for x in result["featured"]], ["Recent"])
        self.assertEqual(result["latest_project"]["repo"], "Recent")
        self.assertEqual(result["active"]["name"], "Recent")

    def test_empty_account_has_no_negative_progress_or_fake_latest_project(self):
        result = build.derive({"github": "new-account", "projects": {"items": None}}, {})
        self.assertEqual(result["lv_prog"], 0)
        self.assertEqual(result["featured"], [])
        self.assertIsNone(result["latest_project"])


class DemoTests(unittest.TestCase):
    def test_demo_build_is_offline_does_not_write_cache_and_retains_template_docs(self):
        cfg = copy.deepcopy(build.load_config())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Guide\n<!-- SHINY:START -->old<!-- SHINY:END -->")
            with patch.object(build, "ROOT", root), patch.object(build, "ASSETS", root / "assets"), \
                 patch.object(build, "OUT", root / "assets/shinycolors.svg"), \
                 patch.object(build, "CACHE", root / "data/stats.json"), \
                 patch.object(build, "load_config", return_value=cfg), \
                 patch.object(build, "load_stats", side_effect=AssertionError("demo fetched data")), \
                 patch.object(build, "render", return_value="<svg/>"), patch("builtins.print"):
                build.build_once(demo=True, readme_mode="preserve")
            self.assertFalse((root / "data/stats.json").exists())
            self.assertIn("# Guide", (root / "README.md").read_text())
            self.assertIn("Your Name", (root / "PROFILE.md").read_text())


if __name__ == "__main__":
    unittest.main()

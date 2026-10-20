"""Character selection, random-mode persistence, and shipped asset integrity."""
import base64
import io
import json
import re
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from PIL import Image

import build


class CharacterTests(unittest.TestCase):
    def test_roster_assets_and_aliases_are_complete(self):
        rows = build.character_catalog()
        self.assertEqual(len(rows), 28)
        self.assertEqual(len({row["id"] for row in rows}), 28)
        self.assertEqual(len({row["file"] for row in rows}), 28)
        self.assertEqual(len({row["unit"] for row in rows}), 8)
        for row in rows:
            with self.subTest(character=row["id"]):
                for alias in [row["id"].upper(), row["name"], *row["aliases"]]:
                    self.assertEqual(build.selected_character(alias)["id"], row["id"])
                with Image.open(build.ROOT / row["file"]) as im:
                    self.assertEqual(im.size, (1024, 1536))
                    self.assertEqual(im.mode, "RGBA")
                    alpha = im.getchannel("A")
                    self.assertEqual(alpha.getextrema()[0], 0)
                    self.assertGreaterEqual(alpha.getextrema()[1], 250)
                    self.assertGreater(alpha.histogram()[0], im.width * im.height * .1)

    def test_unknown_selection_fails_instead_of_silently_using_hana(self):
        for value in ("not-a-character", "", None, 5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build.config_with_character({}, value)

    def test_explicit_selection_overrides_custom_path_without_mutating_input(self):
        cfg = {"character": "hana", "illustration": None, "nickname": "Alice"}
        selected = build.config_with_character(cfg, "樋口 円香")
        self.assertEqual(selected, {"character": "madoka", "nickname": "Alice"})
        self.assertIn("illustration", cfg)
        self.assertEqual(build.illustration_path(selected).name, "madoka-coding.webp")

    def test_custom_and_hidden_options_remain_available(self):
        self.assertIsNone(build.illustration_path({"character": "madoka", "illustration": None}))
        self.assertEqual(build.illustration_path({"character": "hana"}).name, "hana-coding.webp")
        self.assertEqual(build.illustration_path({
            "character": "hana", "illustration": "assets/illustrations/madoka-coding.webp"
        }).name, "madoka-coding.webp")
        with self.assertRaisesRegex(ValueError, "立绘不存在"):
            build.illustration_path({"illustration": "missing.png"})

    def test_random_draws_again_each_render_without_changing_saved_mode(self):
        cfg = build.config_with_character({"illustration": None}, "RANDOM")
        stats = build.demo_stats()
        cfg["nickname"] = "Demo"
        picked = [build.selected_character("hana"), build.selected_character("madoka")]
        # Observe the actual render entry point without rendering unrelated UI.
        with patch.object(build.random, "choice", side_effect=picked) as choose, \
             patch.object(build, "compose", return_value=("", "", "", 100)) as compose:
            for expected in ("hana", "madoka"):
                build.render(cfg, stats, {"level": 1, "streak": 0})
                self.assertEqual(compose.call_args.args[0]["character"], expected)
                self.assertEqual(cfg["character"], "random")
            self.assertEqual(choose.call_count, 2)
            self.assertEqual(len(choose.call_args.args[0]), 28)

    def test_fixed_and_custom_paths_never_draw_randomly(self):
        with patch.object(build.random, "choice", side_effect=AssertionError("unexpected random draw")):
            for cfg in ({"character": "hana"}, {"character": "random", "illustration": None}):
                self.assertEqual(build.resolve_character_choice(cfg), cfg)

    def test_watch_random_is_stable_and_tracks_all_candidates(self):
        with patch.object(build.random, "choice", side_effect=AssertionError("watch rerolled")):
            first = build.watch_signature("random")
            self.assertEqual(first, build.watch_signature("random"))
        paths = {p for p, _ in first}
        self.assertTrue({str(build.ROOT / row["file"]) for row in build.character_catalog()} <= paths)
        fixed_paths = {p for p, _ in build.watch_signature("madoka")}
        self.assertIn(str(build.ROOT / "assets/illustrations/madoka-coding.webp"), fixed_paths)

    def test_each_character_can_be_embedded_with_translation_animation(self):
        for row in build.character_catalog():
            with self.subTest(character=row["id"]), patch.object(build, "DEFS", {}):
                markup = build.character_artwork(0, {"character": row["id"]})
                fragment = ET.fromstring("<svg>" + build.DEFS["characterArtwork"] + markup + "</svg>")
                source = fragment.find("image").get("href")
                data = base64.b64decode(source.split(",", 1)[1])
                with Image.open(io.BytesIO(data)) as embedded, Image.open(build.ROOT / row["file"]) as original:
                    self.assertEqual(embedded.size, original.size)
                    self.assertEqual(embedded.getchannel("A").tobytes(), original.getchannel("A").tobytes())
                animation = fragment.find(".//animateTransform")
                self.assertEqual(animation.get("type"), "translate")
                self.assertEqual(animation.get("values"), "0 0;0 5;0 0")

    def test_workflow_and_gallery_offer_every_character_and_random(self):
        workflow = (build.ROOT / ".github/workflows/shiny-refresh.yml").read_text()
        options_block = workflow.split("options:\n", 1)[1].split("  push:", 1)[0]
        choices = re.findall(r"^\s+- (.+)$", options_block, re.M)
        self.assertEqual(set(choices), {"from-config", "random", *[x["name"] for x in build.character_catalog()]})
        gallery = (build.ROOT / "docs/gallery.html").read_text()
        embedded = json.loads(gallery.split("const roster=", 1)[1].split(";\nconst $", 1)[0])
        self.assertEqual(embedded, build.character_catalog())

    def test_readme_thumbnails_match_exactly_the_shipped_roster(self):
        rows = build.character_catalog()
        expected = {row["file"] for row in rows}
        shipped = {str(path.relative_to(build.ROOT)) for path in
                   (build.ROOT / "assets/illustrations").glob("*.webp")}
        self.assertEqual(shipped, expected)
        readme = (build.ROOT / "README.md").read_text()
        grid = readme.split("<!-- CHARACTERS:START -->", 1)[1].split("<!-- CHARACTERS:END -->", 1)[0]
        sources = re.findall(r'<img src="([^"?]+)(?:\?[^"]+)?"', grid)
        self.assertEqual(len(sources), 28)
        self.assertEqual(set(sources), expected)


if __name__ == "__main__":
    unittest.main()

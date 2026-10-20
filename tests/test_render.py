"""python -m unittest discover -s tests -v"""
import json
import re
import unittest
import xml.etree.ElementTree as ET

import build


class ProjectionTests(unittest.TestCase):
    def test_all_four_corners_match_the_same_screen(self):
        q = [(31, 9), (237, 61), (188, 207), (8, 138)]
        project = build.project_quad(q, 200, 150)
        for local, expected in zip([(0, 0), (200, 0), (200, 150), (0, 150)], q):
            actual = project(*local)
            self.assertAlmostEqual(actual[0], expected[0])
            self.assertAlmostEqual(actual[1], expected[1])

    def test_screen_diagonals_remain_straight(self):
        # A visibly trapezoidal screen distinguishes projective mapping from
        # independently fitted rows or bilinear interpolation.
        project = build.project_quad([(0, 0), (240, 40), (155, 180), (30, 150)], 200, 150)
        for start, end in [((0, 0), (200, 150)), ((200, 0), (0, 150))]:
            ax, ay = project(*start)
            bx, by = project(*end)
            for t in [.2, .4, .6, .8]:
                px, py = project(start[0]+(end[0]-start[0])*t, start[1]+(end[1]-start[1])*t)
                self.assertAlmostEqual((bx-ax)*(py-ay)-(by-ay)*(px-ax), 0, places=7)

    def test_degenerate_screen_is_rejected(self):
        with self.assertRaises(ValueError):
            build.project_quad([(0, 0), (1, 1), (2, 2), (3, 3)], 200, 150)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = build.resolve_identity(build.load_config(), demo=True)
        stats = build.demo_stats()
        cfg["nickname"] = stats["profile_name"]
        cls.svg = build.render(cfg, stats, build.derive(cfg, stats))
        cls.root = ET.fromstring(cls.svg)

    def test_complete_readme_image_has_only_resolved_local_references(self):
        svg, root = self.svg, self.root
        ids = [element.attrib['id'] for element in root.iter() if 'id' in element.attrib]
        self.assertEqual(len(ids), len(set(ids)), 'duplicate SVG ids')
        targets = re.findall(r'(?:url\(#|href="#)([\w-]+)', svg)
        self.assertTrue(set(targets).issubset(ids), set(targets)-set(ids))
        for element in root.iter():
            self.assertFalse(element.tag.endswith('}script'))
            href = element.attrib.get('href', '')
            self.assertFalse(href.startswith(('http:', 'https:', 'file:')))
        self.assertNotIn('id="prAv"', svg)
        self.assertNotIn('id="avFade"', svg)

    def test_smil_timelines_have_valid_segments(self):
        for element in self.root.iter():
            a = element.attrib
            if 'keyTimes' not in a:
                continue
            times = [float(t) for t in a['keyTimes'].split(';')]
            self.assertEqual(times[0], 0)
            self.assertEqual(times[-1], 1)
            self.assertTrue(all(left < right for left, right in zip(times, times[1:])), a)
            values = a.get('values', a.get('keyPoints'))
            self.assertEqual(len(times), len(values.split(';')), a)
            if a.get('calcMode') == 'spline':
                self.assertEqual(len(times)-1, len(a['keySplines'].split(';')), a)

    def test_reading_content_does_not_reset_in_a_loop(self):
        # Text stays visible after its initial reveal.
        for element in self.root.iter():
            a = element.attrib
            if a.get('attributeName') == 'width':
                self.assertNotEqual(a.get('repeatCount'), 'indefinite', a)
                self.assertEqual(a.get('fill'), 'freeze', a)

    def test_chart_replays_over_a_complete_static_series(self):
        # A visitor arriving after the first cycle must still see a drawing
        # animation, while the same complete data remains readable underneath.
        ns = {'s': 'http://www.w3.org/2000/svg'}
        paths = self.root.findall('.//s:path', ns)
        replay = [path for path in paths if any(
            child.get('attributeName') == 'stroke-dashoffset'
            and child.get('repeatCount') == 'indefinite' for child in path)]
        self.assertTrue(replay, 'chart reveal stops before a late visitor reaches it')
        for path in replay:
            base = [candidate for candidate in paths
                    if candidate is not path and candidate.get('d') == path.get('d')
                    and candidate.get('stroke') not in (None, 'none')
                    and candidate.get('opacity', '1') != '0'
                    and not candidate.get('stroke-dasharray') and len(candidate) == 0]
            self.assertTrue(base, 'replaying the chart must not erase the only data series')


if __name__ == '__main__':
    unittest.main()

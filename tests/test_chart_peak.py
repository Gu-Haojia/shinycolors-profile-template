import re
import unittest
import xml.etree.ElementTree as ET

import build


class ChartPeakTests(unittest.TestCase):
    def test_peak_callout_points_to_latest_maximum_even_at_chart_edges(self):
        for counts in ([8, 1, 0], [0, 8, 1], [0, 1, 8], [8, 1, 8]):
            with self.subTest(counts=counts):
                days = [[f'2026-10-{i+1:02}', count] for i, count in enumerate(counts)]
                root = ET.fromstring('<svg>' + build.contrib_chart(
                    {'d30': days, 'max30': max(counts)}, 206, 70, 904, 218) + '</svg>')
                # Read the actual plotted line and actual callout path, rather than reimplementing layout.
                line = root.find(".//*[@id='contrib-line-base']")
                points = [(float(x), float(y)) for x, y in re.findall(r'[ML]([\d.]+) ([\d.]+)', line.get('d'))]
                index = max(range(len(counts)), key=lambda i: (counts[i], i))
                px, py = points[index]
                label = root.find(".//*[@id='contrib-peak-label']")
                self.assertIsNotNone(label)
                balloon = label.find("./g")
                bx, by = map(float, re.search(r'translate\(([\d.-]+) ([\d.-]+)\)', balloon.get('transform')).groups())
                shape = balloon.find(".//path[@stroke='#69616D']")
                motion = label.find('./animateTransform')
                self.assertIsNotNone(motion, 'keep the whole callout floating')
                self.assertFalse(shape.findall('./animate'), 'the tail should not stretch')
                tx, ty = map(float, re.search(r'L([\d.-]+) ([\d.-]+)L', shape.get('d')).groups())
                offsets = [tuple(map(float, xy.split())) for xy in motion.get('values').split(';')]
                self.assertLess(min(dy for dx, dy in offsets), 0)
                for dx, dy in offsets:
                    self.assertAlmostEqual(bx + dx + tx, px, delta=.15)
                self.assertAlmostEqual(by + ty, py - 6, delta=.15)
                self.assertGreaterEqual(bx, points[0][0])
                self.assertLessEqual(bx + 116, points[-1][0])


if __name__ == '__main__':
    unittest.main()

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build


class ProjectConfigTests(unittest.TestCase):
    def setUp(self):
        self.stats = {'repo_meta': {
            'Alpha': [7, 'Python', '来自 GitHub 的简介', '2026-10-18T10:00:00Z'],
            'Beta': [2, 'Java', '第二个项目', '2026-09-01T10:00:00Z'],
        }}
        self.settings = {'home_recommendation': 'Beta', 'items': [
            {'repo': 'Alpha', 'color': 'blue'}, {'repo': 'Beta', 'color': 'pink'}]}

    def derive(self, settings=None):
        return build.derive({'projects': settings if settings is not None else self.settings}, self.stats)

    def test_removing_old_recommendation_does_not_block_item_edits(self):
        self.settings['items'] = [{'repo': 'Alpha', 'title': '新标题'}]
        d = self.derive()
        self.assertEqual([x['repo'] for x in d['featured']], ['Alpha'])
        self.assertEqual(d['featured'][0]['name'], '新标题')
        svg, _ = build.projects(0, d)
        self.assertIn('新标题', svg)
        self.assertNotIn('Beta', svg)

    def test_metadata_is_automatic_and_only_explicit_fields_override(self):
        self.settings['items'][0].update(title='自定义标题', description='自己的介绍', language='Rust')
        self.settings['items'][1].update(description=None, language=None)
        d = self.derive()
        first, second = d['featured']
        self.assertEqual((first['name'], first['desc'], first['lang'], first['stars']),
                         ('自定义标题', '自己的介绍', 'Rust', 7))
        self.assertEqual((second['desc'], second['lang']), ('第二个项目', 'Java'))

    def test_empty_selection_does_not_fall_back_to_random_repos(self):
        d = self.derive({'home_recommendation': None, 'items': []})
        self.assertEqual(d['featured'], [])
        self.assertIsNone(d['latest_project'])

    def test_five_items_generate_a_third_row_without_mutating_data(self):
        self.stats['repo_meta'].update({f'Extra{i}': [0, 'Python', '说明', None] for i in range(3)})
        self.settings['items'] += [{'repo': f'Extra{i}'} for i in range(3)]
        d = self.derive()
        before = copy.deepcopy(d['featured'])
        svg, height = build.projects(0, d)
        shorter, shorter_height = build.projects(0, {**d, 'featured': d['featured'][:4]})
        self.assertIn('Extra2', svg)
        self.assertNotIn('Extra2', shorter)
        self.assertGreater(height, shorter_height)
        self.assertEqual(d['featured'], before)

    def test_unknown_repo_does_not_invent_a_zero_star_count(self):
        self.settings['items'].append({'repo': 'NewRepo', 'description': '手写简介'})
        with patch('builtins.print'):
            item = self.derive()['featured'][-1]
        self.assertIsNone(item['stars'])
        self.assertEqual(item['desc'], '手写简介')
        self.assertEqual(item['ago'], '—')

    def test_invalid_color_duplicate_and_boolean_are_rejected(self):
        cases = []
        bad = copy.deepcopy(self.settings); bad['items'][0]['color'] = 'nope'; cases.append(bad)
        bad = copy.deepcopy(self.settings); bad['items'][0]['color'] = []; cases.append(bad)
        bad = copy.deepcopy(self.settings); bad['items'].append({'repo': 'alpha'}); cases.append(bad)
        bad = copy.deepcopy(self.settings); bad['items'][0]['show_on_projects'] = 'false'; cases.append(bad)
        for bad in cases:
            with self.subTest(settings=bad), self.assertRaises(ValueError):
                self.derive(bad)

    def test_project_file_is_resolved_relative_to_main_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'config.json').write_text(json.dumps({'projects_file': 'curated.json'}))
            (root/'curated.json').write_text(json.dumps(self.settings))
            self.assertEqual(build.load_config(root/'config.json')['projects'], self.settings)

    def test_invalid_config_keeps_last_generated_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'config.json').write_text(json.dumps({'github': 'example', 'nickname': 'Example', 'projects': {'items': [{'repo': 'Alpha', 'color': 'invalid'}]}}))
            out = root/'assets'/'shinycolors.svg'
            out.parent.mkdir()
            out.write_text('previous output')
            with patch.object(build, 'ROOT', root), patch.object(build, 'OUT', out), \
                 patch.object(build, 'load_stats', return_value=self.stats), patch('builtins.print'):
                with self.assertRaises(ValueError):
                    build.build_once(True)
            self.assertEqual(out.read_text(), 'previous output')


if __name__ == '__main__':
    unittest.main()

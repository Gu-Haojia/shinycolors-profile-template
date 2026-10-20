import copy
import hashlib
import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import build


class LatestProjectTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {'github': 'Example', 'nickname': 'Producer',
                    'projects': {'items': [], 'home_recommendation': 'Gone'}}
        self.stats = {
            'repo_meta': {
                'Older': [1, 'Java', '旧项目', '2026-10-20T00:00:00Z'],
                'Newest': [2, 'Python', '最新项目', '2026-10-19T00:00:00Z'],
                'example': [100, 'Python', '主页', '2026-10-21T00:00:00Z'],
            },
            'repo_commits': {
                'Older': {'sha': 'a' * 40, 'at': '2026-10-18T00:00:00Z', 'message': '旧提交'},
                'Newest': {'sha': 'b' * 40, 'at': '2026-10-19T00:00:00Z', 'message': 'fix: 最新修改'},
                'example': {'sha': 'c' * 40, 'at': '2026-10-21T00:00:00Z', 'message': 'daily refresh'},
            },
        }

    def test_latest_commit_is_independent_of_items_and_excludes_this_repo(self):
        d = build.derive(self.cfg, self.stats)
        top = d['latest_project']
        self.assertEqual(d['featured'], [])
        self.assertEqual((top['repo'], top['commit_sha'], top['commit_message']),
                         ('Newest', 'b' * 40, 'fix: 最新修改'))
        self.cfg['projects']['items'] = [{'repo': 'Older', 'title': '手写展示名'}]
        self.assertEqual(build.derive(self.cfg, self.stats)['latest_project'], top)

    def test_next_fetch_replaces_previous_commit_and_missing_data_is_not_invented(self):
        updated = copy.deepcopy(self.stats)
        updated['repo_commits']['Older'] = {
            'sha': 'd' * 40, 'at': '2026-10-22T00:00:00Z', 'message': 'feat: new work'}
        self.assertEqual(build.derive(self.cfg, updated)['latest_project']['repo'], 'Older')
        updated['repo_commits'] = {}
        self.assertIsNone(build.derive(self.cfg, updated)['latest_project'])

    def test_home_shows_commit_time_without_summary_or_sha(self):
        d = build.derive(self.cfg, self.stats)
        d['latest_project']['fresh'] = True
        svg, _ = build.home(self.cfg, self.stats, d)
        card = ET.tostring(ET.fromstring('<svg>' + svg + '</svg>').find(".//*[@id='latest-project']"), encoding='unicode')
        self.assertIn('NEW!!', card)
        self.assertNotIn('Python', card)
        self.assertIn('最新项目', svg)
        self.assertIn(d['latest_project']['commit_time'], svg)
        self.assertNotIn('bbbbbbb', svg)
        self.assertNotIn('fix: 最新修改', svg)
        self.assertNotIn('daily refresh', svg)


class PublishedImageVersionTests(unittest.TestCase):
    def test_changed_items_publish_a_different_image_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'assets' / 'shinycolors.svg'
            cfg = {'github': 'Example', 'nickname': 'Producer', 'projects': {'items': [{'repo': 'Alpha'}]}}
            stats = {'repo_meta': {'Alpha': [1, 'Python', '介绍', None], 'Beta': [2, 'Java', '介绍', None]}}
            urls = []
            with patch.object(build, 'ROOT', root), patch.object(build, 'ASSETS', out.parent), \
                 patch.object(build, 'OUT', out), patch.object(build, 'load_config', side_effect=lambda: cfg), \
                 patch.object(build, 'load_stats', return_value=stats), patch.object(build, 'preview', return_value='preview'), \
                 patch.object(build, 'render', side_effect=lambda c, s, d: '<svg>' + d['featured'][0]['repo'] + '</svg>'), \
                 patch('builtins.print'):
                for name in ('Alpha', 'Beta'):
                    cfg['projects']['items'] = [{'repo': name}]
                    build.build_once(True)
                    md = (root / 'README.md').read_text()
                    version = hashlib.sha256(out.read_bytes()).hexdigest()[:12]
                    self.assertIn('shinycolors.svg?v=' + version, md)
                    urls.append(md.split('src="', 1)[1].split('"', 1)[0])
            self.assertNotEqual(*urls)


class CommitFetchTests(unittest.TestCase):
    def test_graphql_pagination_keeps_latest_commit_and_skips_profile_and_empty_repo(self):
        def node(name, date, empty=False):
            return {'name': name, 'languages': {'edges': []},
                    'defaultBranchRef': None if empty else {'name': 'main', 'target': {
                        'oid': name * 8, 'messageHeadline': name + ' commit', 'committedDate': date,
                        'url': 'https://github.com/Example/' + name + '/commit/123'}}}

        repos = [{'name': name, 'fork': False, 'pushed_at': '2026-10-20T00:00:00Z',
                  'stargazers_count': 0, 'language': 'Python', 'description': '', 'default_branch': 'main'}
                 for name in ('Alpha', 'Beta', 'Example', 'Empty')]
        user = {'followers': 0, 'public_repos': 4, 'created_at': '2020-01-01T00:00:00Z',
                'avatar_url': 'https://example.test/avatar'}

        def api(url, token):
            if '/repos?' in url:
                return repos
            if '/events/' in url:
                return []
            return user

        first = {'pullRequests': {'totalCount': 0}, 'issues': {'totalCount': 0},
                 'repositoriesContributedTo': {'totalCount': 0},
                 'contributionsCollection': {'contributionYears': [], 'totalCommitContributions': 0,
                                             'contributionCalendar': {'totalContributions': 0, 'weeks': []}},
                 'repositories': {'nodes': [node('Alpha', '2026-10-18T00:00:00Z'),
                                             node('Example', '2026-10-21T00:00:00Z'), node('Empty', None, True)],
                                  'pageInfo': {'hasNextPage': True, 'endCursor': 'next-page'}}}
        second = {'repositories': {'nodes': [node('Beta', '2026-10-20T00:00:00Z')],
                                   'pageInfo': {'hasNextPage': False, 'endCursor': None}}}
        year = build.dt.datetime.now(build.dt.timezone(build.dt.timedelta(hours=8))).year
        annual = {f'y{year}': {'contributionCalendar': {'totalContributions': 0}}}
        with patch.object(build, 'api', side_effect=api), patch.object(build, 'gql', side_effect=[first, annual, second]) as gql, \
             patch.object(build.urllib.request, 'urlopen', return_value=io.BytesIO(b'\x89PNG\r\n\x1a\n')):
            stats = build.fetch('Example', 'test-token')
        self.assertEqual(set(stats['repo_commits']), {'Alpha', 'Beta'})
        self.assertIn('after:"next-page"', gql.call_args_list[2].args[0])
        self.assertEqual(build.derive({'github': 'Example', 'projects': {'items': []}}, stats)['latest_project']['repo'], 'Beta')

    def test_rest_reads_default_branch_commit_without_requesting_profile_repo(self):
        repos = [{'name': 'Example', 'default_branch': 'main'}, {'name': 'Alpha', 'default_branch': 'feature/main'}]
        rows = [{'sha': 'a' * 40, 'html_url': 'https://github.com/Example/Alpha/commit/123',
                 'commit': {'committer': {'date': '2026-10-20T00:00:00Z'}, 'message': 'First line\n\nBody'}}]
        with patch.object(build, 'api', return_value=rows) as api:
            commits = build.fetch_repo_commits_rest('Example', repos, None)
        api.assert_called_once()
        self.assertIn('sha=feature%2Fmain', api.call_args.args[0])
        self.assertEqual(commits['Alpha']['message'], 'First line')
        self.assertNotIn('Example', commits)


if __name__ == '__main__':
    unittest.main()

import datetime as dt
import io
import unittest
from unittest.mock import patch

import build


class FixedDateTime(dt.datetime):
    @classmethod
    def now(cls, tz=None):
        # 北京时间已进入 2026 年，UTC 仍在 2025 年。
        instant = cls(2025, 12, 31, 18, tzinfo=dt.timezone.utc)
        return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)


class StatisticsPeriodTests(unittest.TestCase):
    def test_rolling_commits_and_calendar_year_totals_are_separate_at_new_year(self):
        user = {'followers': 0, 'public_repos': 0, 'created_at': '2020-01-01T00:00:00Z',
                'avatar_url': 'https://example.test/avatar'}
        first = {
            'pullRequests': {'totalCount': 0}, 'issues': {'totalCount': 0},
            'repositoriesContributedTo': {'totalCount': 0},
            'contributionsCollection': {
                'contributionYears': [2025], 'totalCommitContributions': 31,
                'contributionCalendar': {'totalContributions': 100, 'weeks': []}},
            'repositories': {'nodes': [], 'pageInfo': {'hasNextPage': False, 'endCursor': None}},
        }
        annual = {f'y{year}': {'contributionCalendar': {'totalContributions': total}}
                  for year, total in [(2025, 50), (2026, 7)]}

        def api(url, token):
            return [] if '/repos?' in url or '/events/' in url else user

        with patch.object(build.dt, 'datetime', FixedDateTime), \
             patch.object(build, 'api', side_effect=api), \
             patch.object(build, 'gql', side_effect=[first, annual]) as gql, \
             patch.object(build.urllib.request, 'urlopen', return_value=io.BytesIO(b'\x89PNG\r\n\x1a\n')):
            stats = build.fetch('Example', 'test-token')
        self.assertEqual(stats['commits'], 31)
        self.assertEqual(stats['contrib_year'], 7)
        self.assertEqual(stats['contrib_all'], 57)
        self.assertEqual(stats['contribution_year'], 2026)
        query = gql.call_args_list[1].args[0]
        self.assertIn('y2026:contributionsCollection(from:"2026-01-01T00:00:00+08:00"', query)
        self.assertIn('to:"2026-01-01T02:00:00+08:00"', query)

    def test_this_week_starts_on_monday_and_excludes_previous_week_and_future_days(self):
        stats = {'days': [['2025-12-28', 90], ['2025-12-29', 2], ['2025-12-30', 3],
                          ['2025-12-31', 1], ['2026-01-01', 4], ['2026-01-02', 80]]}
        with patch.object(build.dt, 'datetime', FixedDateTime):
            d = build.derive({'timezone_offset': 8, 'projects': {'items': []}}, stats)
        self.assertEqual(d['week_total'], 10)

    def test_cached_calendar_year_keeps_its_actual_year_label(self):
        with patch.object(build.dt, 'datetime', FixedDateTime):
            d = build.derive({'projects': {'items': []}}, {'contribution_year': 2025, 'contrib_year': 50})
        self.assertEqual(d['year'], 2025)


if __name__ == '__main__':
    unittest.main()

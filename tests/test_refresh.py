import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build


class ScheduledRefreshTests(unittest.TestCase):
    def test_scheduled_failure_is_reported_without_replacing_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'stats.json'
            previous = '{"github": "example", "stars": 7}'
            cache.write_text(previous)
            with patch.dict(build.os.environ, {'GITHUB_TOKEN': 'test-token'}), \
                 patch.object(build, 'CACHE', cache), \
                 patch.object(build, 'fetch', side_effect=RuntimeError('API unavailable')), \
                 patch.object(build.sys, 'argv', ['build.py', '--strict-refresh']):
                with self.assertRaisesRegex(RuntimeError, 'GitHub 数据刷新失败'):
                    build.load_stats({'github': 'example'}, False)
            self.assertEqual(cache.read_text(), previous)

    def test_interactive_build_can_still_use_cached_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'stats.json'
            cache.write_text(json.dumps({'github': 'example', 'stars': 7}))
            with patch.dict(build.os.environ, {'GITHUB_TOKEN': 'test-token'}), \
                 patch.object(build, 'CACHE', cache), \
                 patch.object(build, 'fetch', side_effect=RuntimeError('API unavailable')), \
                 patch.object(build.sys, 'argv', ['build.py']), patch('builtins.print'):
                self.assertEqual(build.load_stats({'github': 'example'}, False), {'github': 'example', 'stars': 7})


if __name__ == '__main__':
    unittest.main()

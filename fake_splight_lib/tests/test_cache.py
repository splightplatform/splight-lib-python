from unittest import TestCase
from fake_splight_lib.cache import FakeCacheClient
from splight_abstract.cache import get_cache, flush_cache


CACHE_CLIENT = FakeCacheClient()


class TestCacheFunctions(TestCase):

    def setUp(self):
        CACHE_CLIENT.clear()
        self.called_count = 0

    @get_cache(CACHE_CLIENT, 'cached_dummy', 'param')
    def cached_dummy(self, param, key='p'):
        self.called_count += 1
        return {key: param}

    @flush_cache(CACHE_CLIENT, 'cached_dummy', 'param')
    def flush_dummy(self, param):
        pass

    @flush_cache(CACHE_CLIENT, 'cached_dummy', prefix_match=True)
    def flush_dummy_prefix(self):
        pass

    def test_get_cache_same_param(self):
        self.assertEqual(self.called_count, 0)
        self.cached_dummy(1)
        self.cached_dummy(1)
        self.assertEqual(self.called_count, 1)

    def test_get_cache_multiple_params(self):
        self.cached_dummy(1)
        self.cached_dummy(2)
        self.cached_dummy(2)
        self.assertEqual(self.called_count, 2)

    def test_flush_cache(self):
        self.cached_dummy(1)
        self.assertEqual(self.called_count, 1)
        self.flush_dummy(1)
        self.cached_dummy(1)
        self.assertEqual(self.called_count, 2)

    def test_cache_values(self):
        EXPECTED_RESULT = self.cached_dummy(1)
        res = self.cached_dummy(1)
        self.assertEqual(self.called_count, 1)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_flush_cache_multiple_values(self):
        self.cached_dummy(1, 'hola')
        self.cached_dummy(2, 'manola')
        self.flush_dummy_prefix()

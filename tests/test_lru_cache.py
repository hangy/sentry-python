import pytest
from copy import deepcopy

from sentry_sdk._lru_cache import LRUCache


@pytest.mark.parametrize("max_size", [-10, -1, 0])
def test_illegal_size(max_size):
    with pytest.raises(AssertionError):
        LRUCache(max_size=max_size)


def test_simple_set_get():
    cache = LRUCache(1)
    assert cache.get(1) is None
    cache.set(1, 1)
    assert cache.get(1) == 1


def test_overwrite():
    cache = LRUCache(1)
    assert cache.get(1) is None
    cache.set(1, 1)
    assert cache.get(1) == 1
    cache.set(1, 2)
    assert cache.get(1) == 2


def test_cache_eviction():
    cache = LRUCache(3)
    cache.set(1, 1)
    cache.set(2, 2)
    cache.set(3, 3)
    assert cache.get(1) == 1
    assert cache.get(2) == 2
    cache.set(4, 4)
    assert cache.get(3) is None
    assert cache.get(4) == 4


def test_cache_miss():
    cache = LRUCache(1)
    assert cache.get(0) is None


def test_cache_set_overwrite():
    cache = LRUCache(3)
    cache.set(0, 0)
    cache.set(0, 1)
    assert cache.get(0) == 1


def test_cache_get_all():
    cache = LRUCache(3)
    cache.set(0, 0)
    cache.set(1, 1)
    cache.set(2, 2)
    cache.set(3, 3)
    assert cache.get_all() == [(1, 1), (2, 2), (3, 3)]
    cache.get(1)
    assert cache.get_all() == [(2, 2), (3, 3), (1, 1)]


def test_cache_copy():
    cache = LRUCache(3)
    cache.set(0, 0)
    cache.set(1, 1)

    copied = deepcopy(cache)
    cache.set(2, 2)
    cache.set(3, 3)
    assert copied.get_all() == [(0, 0), (1, 1)]
    assert cache.get_all() == [(1, 1), (2, 2), (3, 3)]

    copied = deepcopy(cache)
    cache.get(1)
    assert copied.get_all() == [(1, 1), (2, 2), (3, 3)]
    assert cache.get_all() == [(2, 2), (3, 3), (1, 1)]


def test_cache_pollution():
    cache1 = LRUCache(max_size=2)
    cache1.set(1, True)
    cache2 = deepcopy(cache1)
    cache2.set(1, False)
    assert cache1.get(1) is True
    assert cache2.get(1) is False

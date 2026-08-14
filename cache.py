# -*- coding: utf-8 -*-
"""简单内存缓存装饰器。同一股票 1 小时内重复请求直接返回缓存。"""
import time

cache_store = {}


def cache_result(expire_seconds=3600):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            if key in cache_store:
                data, timestamp = cache_store[key]
                if time.time() - timestamp < expire_seconds:
                    return data
            result = func(*args, **kwargs)
            cache_store[key] = (result, time.time())
            return result
        return wrapper
    return decorator

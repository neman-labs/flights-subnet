import asyncio
import functools


def retry_async(count=1, delay=0, factor=1, exceptions=Exception):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            exc = None
            exp_delay = delay

            for i in range(count):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as e:
                    exc = e

                if i == count - 1:
                    break

                await asyncio.sleep(exp_delay)
                exp_delay *= factor

            if exc:
                raise exc

            return None

        return wrapper

    return decorator

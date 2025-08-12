from functools import wraps

from twisted.internet import reactor, defer


def coroutine_might_block(coro):
    # If you don't know know async/await is implemented in python, this will
    #   look very weird to you. Starting observation: `await coro` is not
    #   equivalent to `coro.__await__()`. That would only be the first step.
    # After __await__ is called, Python expects it to return an iterator.
    # That iterator is then used to check if the coroutine is done
    # That iterator yields values. And Python gets those values by calling
    # next(iterator) (or iterator.send(), I think). If, instead, StopIteration
    # is thrown, it means that the coroutine is done, and the result
    # is stored in the exception. Yes, it's a little weird: the ending
    # of a coroutine is represented by an exception.
    #
    # If an actual value is yielded, it means that the coroutine is not done.
    # At this point, Python could just do busy polling, and call
    # next(iterator) in an infinite loop, until it gets the result.
    # But then, we wouldn't have true concurrency. So, instead, Python says:
    # "Ok, I gave you one chance to finish, but you didn't. Then I'll assume
    # you might need more time. You might not be the only coroutine that's
    # running, so I will send you to the event loop, and it's its job to
    # decide when to call next(iterator) again, to check if you're ready."
    # When the iterator is passed back to the event loop, this gives the
    # chance of other coroutines to be checked if they're done.

    iterator = coro.__await__()
    try:
        # Get the next yield
        # These awated object would've been sent to the driving event loop,
        #   up on the stack
        awaited = next(iterator)
    except StopIteration as e:
        # Awaitable is done, so the coroutine didn't block
        return False, e.value
        return e.value

    return True, awaited


def timeoutDeferred(timeout=None):
    def decorator(func):
        def timeoutError(value, timeout):
            raise RuntimeError(f"Test timed out after: {timeout} secconds")

        @wraps(func)
        def wrapper(*args, **kwargs):
            d = defer.ensureDeferred(func(*args, **kwargs))
            d.addTimeout(timeout, reactor, timeoutError)
            return d

        return wrapper
    return decorator



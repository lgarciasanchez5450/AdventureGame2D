import typing

_funcs_to_call:list[typing.Callable[[],bool]] = []

def addInitialization(func:typing.Callable[[],bool]):
    _funcs_to_call.append(func)

def preinitialize() -> bool:
    a = 1
    while _funcs_to_call:
        func = _funcs_to_call.pop()
        a &= func()
    initialized = bool(a)
    return initialized

def preinitializeAsync() -> typing.Generator[float,None,bool]:
    yield 0.0
    i = 0
    if not _funcs_to_call:
        yield 1.0
        return True

    while _funcs_to_call:
        func = _funcs_to_call.pop()
        a &= func()
        i+=1
        yield (i) / len(_funcs_to_call)

    initialized = bool(a)
    return initialized

def isInitialized():
    return not _funcs_to_call
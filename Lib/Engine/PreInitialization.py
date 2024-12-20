import typing

_funcs_to_call:list[typing.Callable[[],bool]] = []

def addInitialization(func:typing.Callable[[],bool]):
    assert not initialized
    _funcs_to_call.append(func)

def preinitialize() -> bool:
    global initialized
    if initialized:
        return True
    a = 1
    while _funcs_to_call:
        func = _funcs_to_call.pop()
        a &= func()
    initialized = bool(a)
    return initialized

def preinitializeAsync() -> typing.Generator[float,None,bool]:
    global initialized
    yield 0.0
    if initialized:
        yield 1.0
        return True
    i = 0
    while _funcs_to_call:
        func = _funcs_to_call.pop()
        a &= func()
        i+=1
        yield (i) / len(_funcs_to_call)
    initialized = bool(a)
    return initialized

def isInitialized():
    return not _funcs_to_call
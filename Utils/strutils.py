import typing
def split(string:str,delimiters:typing.Collection[str]):
    assert list(map(len,delimiters)) == [1] * len(delimiters), 'delimiters can only have one character'
    word = ''
    out:list[str] = []
    for char in string:
        if char not in delimiters:
            word += char
        else:
            if word:
                out.append(word)
                word = ''
    if word:
        out.append(word)
    return out
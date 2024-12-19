import typing
def split(string:str,delimiters:typing.Collection[str]):
    assert all(len(c)==1 for c in delimiters), 'delimiters can only have one character'
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
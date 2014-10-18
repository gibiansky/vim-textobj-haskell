#!/usr/bin/python
import vim


def isTopBinding(text):
    return not (len(text) == 0 or text.startswith("--") or text[0].isspace())


def isStatement(text):
    return len(text) > 0 and text[0].isspace() and len(text.strip()) > 0


def isTypeSignature(text):
    words = text.strip().split(" ")
    return len(words) > 3 and words[1] == "::"


def find(content, index, cmpF, iterF):
    i = index
    while i >= 0 and i < len(content):
        if cmpF(content[i]):
            return (True, i)
        i = iterF(i)
    return (False, i)


def setRetValue(start, end,  lines):
    startPos = [0, start+1, 1, 0]
    endPos = [0, end+1, len(lines[end]), 0]
    vim.command("let g:haskell_textobj_ret="+str([startPos, endPos]))


def selectHaskellBinding(lines, cursor, includeType):
    """
    Extract function binding from index in content
    content: [String] list of haskell source lines
    cursor:  zero-based line index
    return:  [String] top level binding index resides in
    """
    backward = lambda x: x - 1
    forward = lambda x: x + 1
    index = cursor - 1

    found, bStart = find(lines, index, isTopBinding, backward)
    found, bNext = find(lines, index+1, isTopBinding, forward)
    if found:
        found, bEnd = find(lines, bNext, isStatement, backward)
    else:
        found = True
        bEnd = bNext - 1
    bEnd = bStart if bEnd < bStart else bEnd

    if includeType and bStart > 0 and isTypeSignature(lines[bStart-1]):
        bStart = bStart - 1

    setRetValue(bStart, bEnd, lines)

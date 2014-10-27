#!/usr/bin/python

VIM_RETURN_VAR = 'haskell_textobj_ret'

import sys

try:
    import vim
except ImportError:
    print "Warning: Not running inside Vim."


def vim_return(start_line, end_line, lines):
    """
    Return the selection extent to Vim by setting a flag variable.
    The format returned is described in the Vim documentation for getpos().
    """
    buf_num = 0
    offset = 0
    start_col = 1
    start_pos = [buf_num, start_line + 1, start_col, offset]

    end_col = len(lines[end_line])
    end_pos = [buf_num, end_line + 1, end_col, offset]

    cmd = "let g:%s=%s" % (VIM_RETURN_VAR, str([start_pos, end_pos]))
    vim.command(cmd)


def select_haskell_block(lines, cursor, around):
    """
    Find the start and end location of the current haskell text object.


    Arguments:
        - lines: list of haskell source lines
        - cursor: line index
        - around: include auxiliary blocks?

    When `around` is true, the return value will select more. Specifically,
    it will:
        - Select all import statements in a block.
        - Select all clauses of a function as well as the type signature.
    """
    start_line, end_line = find_block(lines, cursor)
    if around:
        # Take care of expanding imports.
        while is_import(start_line, end_line, lines):
            start_line, end_line = extend_imports(start_line, end_line, lines)

        # Take care of extending pattern matches.
        if is_decl(start_line, end_line, lines):
            start_line, end_line = extend_typesig(start_line, end_line, lines)
    vim_return(start_line, end_line, lines)


def extend_imports(start_line, end_line, lines):
    start2, end2 = find_block(lines, start_line - 1)
    if start2 != start_line and is_import(start2, end2, lines):
        return start2, end_line

    start3, end3 = find_block(lines, end_line + 1)
    if end3 != end_line and is_import(start3, end3, lines):
        return start_line, end3


def is_import(start, end, lines):
    return lines[start].strip().startswith("import")


def is_decl(start, end, lines):
    line = lines[start].strip()
    decl = "=" in line
    if not decl:
        return False

    if any(tok in line for tok in ["data", "newtype"]):
        return False

    return True


def extend_typesig(start_line, end_line, lines):
    start2, end2 = find_block(lines, start_line - 1)
    if "::" in lines[start2].split()[1]:
        return start2, end_line


def indent_level(line):
    """Return the indent level of the line (measured in spaces)"""
    # Make sure it has something on it.
    if not line.strip():
        raise ValueError("Empty line has no indent level")

    level = 0
    for i, char in enumerate(line):
        if char != ' ' and char != '\t':
            return level
        elif char == ' ':
            level += 1
        elif char == '\t':
            level += 8


def empty(line):
    return not line.strip()


def indented(line):
    return indent_level(line) > 0


def has_start_block(line):
    """Whether this line is the beginning of a block."""
    maybe_type = len(line.split("::")) == 2
    if maybe_type:
        before, after = line.split("::")
        if before.count(" ") <= 0:
            return True
    return any(line.startswith(start_token)
               for start_token in ["data", "newtype", "import"])


def is_comment(line):
    line = line.strip()
    return line.startswith("--") or line.startswith("{-")


def find_block(lines, index):
    """Find a block that the cursor is in.

    Arguments:
        - lines: all the lines in the file.
        - index: the line number of the cursor.
        - around: Whether to include surrounding blocks.
    """
    # Move the cursor until we find a non-empty line.
    while index < len(lines) and empty(lines[index]):
        index += 1

    # Start by only including the line we're on.
    start_index = index
    end_index = index

    # Expand the selection upwards.
    def expand_upwards():
        # Can't go past file start.
        if start_index == 0:
            return False

        current_line = lines[start_index]
        previous_line = lines[start_index - 1]

        if is_comment(previous_line):
            return True

        # If this is the start of a block, go no further.
        if not empty(current_line) and not indented(current_line):
            return False

        return True

    while expand_upwards():
        start_index -= 1

    def expand_downwards():
        # Can't go past file end.
        if end_index == len(lines) - 1:
            return False

        current_line = lines[end_index]
        next_line = lines[end_index + 1]

        if is_comment(current_line) and is_comment(next_line):
            return True

        # Can't encroach on the next start block.
        if has_start_block(next_line):
            return False

        return empty(next_line) or indented(next_line)

    while expand_downwards():
        end_index += 1

    # Trim the selection to avoid newlines.
    while empty(lines[start_index]):
        start_index += 1
    while empty(lines[end_index]):
        end_index -= 1

    return start_index, end_index

if __name__ == "__main__":
    lines = open(sys.argv[1]).readlines()
    for ind in xrange(len(lines)):
        start, end = find_block(lines, ind)
        for i in xrange(start, end + 1):
            print lines[i][:-1]
        print ind, find_block(lines, ind)
        raw_input()
        print '---'

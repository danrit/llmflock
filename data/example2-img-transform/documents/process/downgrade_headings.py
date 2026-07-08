#!/usr/bin/env python3
"""Downgrade all Markdown ATX headings in a file by one level (e.g. ## -> ###)."""
import re
import sys

HEADING_RE = re.compile(r'^(#{1,6})(\s+.*)$')
FENCE_RE = re.compile(r'^(```|~~~)')


def downgrade_headings(text):
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    for line in lines:
        stripped = line.rstrip('\n')
        if FENCE_RE.match(stripped.strip()):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            m = HEADING_RE.match(stripped)
            if m and len(m.group(1)) < 6:
                newline_suffix = line[len(stripped):]
                line = '#' + m.group(1) + m.group(2) + newline_suffix
        out.append(line)
    return ''.join(out)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <markdown-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = downgrade_headings(content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)


if __name__ == '__main__':
    main()

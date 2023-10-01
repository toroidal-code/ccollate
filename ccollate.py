#!/usr/bin/env python

import os
import sys
import re

HEADER_EXTS = ['.h', '.hh', '.hpp']

include_dirs = ['.']

visited = set()

def parse(file_name):
    if file_name in visited:
        return ''
    else:
        visited.add(file_name)

    with open(file_name, 'r') as file:
        contents = file.read()

    # Remove documentation comments
    contents = re.sub(r'/\*\*(?:.|[\r\n])*?\*/\s*', '', contents)

    contents = '\n'.join([line for line in contents.splitlines() if not line.strip().startswith('//')])

    lines = contents.splitlines()
    contents = []

    for lineno, line in enumerate(lines, start=1):
        if line.startswith('#include "'):
            include_file = None
            include_dirs.insert(0, os.path.dirname(file_name))
            for inc in include_dirs:
                include_path = os.path.abspath(os.path.join(inc, line.split('"')[1]))
                if os.path.exists(include_path):
                    include_file = include_path
                    break

            if include_file is None:
                name = line.split('"')[1]
                raise Exception(f"Fatal Error: The file {name} was not found in any of the include paths {include_dirs}")

            include = parse(include_file)
            include = f"#line {lineno + 1} \"{file_name}\"\n{include}"
            contents.append(include)
        else:
            contents.append(line)

    contents = '\n'.join(contents)
    if contents:
        contents = f"#line 1 \"{file_name}\"\n{contents}"
    return contents

if len(sys.argv) == 1:
    sys.exit(-1)
else:
    start_file = os.path.abspath(sys.argv[1])
    if not os.path.isfile(start_file) or os.path.splitext(start_file)[1] not in HEADER_EXTS:
        raise Exception(f"{sys.argv[1]} is not a valid header file.")
    include_dirs.append(os.path.dirname(start_file))
    print(parse(start_file))

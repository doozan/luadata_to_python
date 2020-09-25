#!/usr/bin/python3
#
# Copyright (c) 2020 Jeff Doozan
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Converts simple Lua data assignments to Python data, works just well enough to parse
very basic lua data structures used by en.wiktionary.org, particularly those used by
Template:es-conj and Module:labels/data

WARNING: This will take publicly modifiable text and turn it in to python code,
which is a major security risk. You must manually review all generated code before
passing it to a Python interpreter.
"""

# Forgive the terrible string handling, I was still leaning Python when I wrote this code

import re

# add a , after the final " } or ]
def add_comma_after_closer(line):

    line, delimiter, comment = line.partition("--")

    pattern = r"""(?x)      #
    ([}\]'"])(?!.*[}\]'"])      # the last } ] ' or " (using negative lookahead)
    """
    line = re.sub(pattern, r"\1,", line)
    return line + delimiter + comment


# This assumes the lua source consists of multiple assignments to a data structure named "data"
# In the resulting python code, all the data assignments are morphed into the declaration of the hash
# variable passed as "varname"
def convert(data, target, outvar=None, trim_newlines=False, no_warning=False, numeric_keys=False):
    """
    data = luadata to convert
    target = variable to extract from luadata
    outvar = name to give to pydata
    trim_newlines - if True, strip empty lines from resulting pydata
    no_warning - if True, don't add ValueError warning to pydata
    numeric_keys - if True, don't quote numeric keys in dictionary
    """

    if not outvar:
        outvar = target

    dicts = []
    idx = 0
    maxidx = len(data)

    # find all pairs of braces {} and flag those missing any = assignments as lists (unless they're empty)
    chunks = []
    while idx<maxidx:
        if data[idx] == "{":
            dicts.append({"start": idx, "is_list": True})
        elif data[idx] == "}":
            item = dicts.pop()
            item["end"] = idx
            chunks.append(item)
        elif data[idx] == "=" and len(dicts):
            dicts[-1]["is_list"] = False
        idx += 1


    # replace {} with [] in lists
    replacements = {}
    for item in chunks:

        if item['is_list']:
            # Empty sets of braces aren't considered lists
            if (data[item['start']+1:item['end']].strip()) == "":
                continue
            replacements[item['start']] = "["
            replacements[item['end']] = "]"

        else:
            inquote = False
            for idx in range(item['start'],item['end']):
                if data[idx] == '"':    # very simple quote handling, doesn't understand escapes or comments
                    inquote = not inquote
                if not inquote and data[idx] == "=":
                    replacements[idx] = chr(1) # Temporary placeholder, replaced with : when quoting the parameter

    replaced = ""
    strpos = 0
    for idx in sorted(replacements.keys()):
        replaced += data[strpos:idx] + replacements[idx]
        strpos = idx+1
    replaced += data[strpos:]

    data = replaced

    # strip [] from items being assigned values
    pattern = r"""(?x)     #
               \[          # opening bracket
               ([^\]]+)    # all chars until the closing bracket
               \]          # closing bracket
               \s*\x01     # whitespace and assignment placeholder (0x01)
    """
    data = re.sub(pattern, r'  \1:', data)

    datalines = []
    if not no_warning:
        datalines.append("""raise ValueError("WARNING: This code has been generated from publicly editable sources.  You must review the code (and remove this warning) before using it.")""")


    # Strip anything that isn't part of data, wrap the whole thing in a variable assignment,
    # and add commas after data items
    # "data" is defined as any line containing an = sign
    # and, if there's a brace on the opening line, all lines until a matching closing brace
    # plus the entirety of the line containing the closing brace
    datalines.append(outvar + " = {")
    in_data = False
    depth = 0
    for line in data.splitlines():
        line = line.replace("\t", "    ").rstrip()

        if trim_newlines and not line.strip():
            continue

        if in_data:

            depth += line.count("{") + line.count("[") - line.count("}") - line.count("]")

            # This is the end a data set, append a comma
            if depth == 0:
                in_data = False
                line = add_comma_after_closer(line)

            if depth < 0:
                raise ValueError("Too many closing brackets", line)

            else:
                datalines.append(line)

        elif "=" in line:
            pattern = fr"""(?x)
                \s*                   # whitespace
                {target}\[\s*         # variable[
                (['"][^\]]+['"])              # param
                \s*\]\s*=                # closing bracket ], whitespace, =
            """
            res = re.match(pattern, line)
            if not res:
                continue
            line = re.sub(pattern, r"\1:", line)

            depth = line.count("{") + line.count("[") - line.count("}") - line.count("]")
            if depth:  # If there are more opening than closing braces, assume we're in a multi-line assignment
                in_data = True
                datalines.append(line)
            else:
                # add a comma to the end of single line assignment items
                datalines.append(add_comma_after_closer(line))

        #  permit empty lines, but ignore everything else
        elif line.strip() == "":
            datalines.append("")
    datalines.append("}")

    pydata = "\n".join(datalines)
    # convert lua string escapes to python strings
    pydata = re.sub(r"'''", r"'", pydata)

    # convert lua comments to python comments
    pydata = re.sub(r"--", r"#", pydata)

    # convert lua true to python True
    pydata = re.sub(r"true", r"True", pydata)

    # convert lua false to python False
    pydata = re.sub(r"false", r"False", pydata)

    # add quotes to bare dictionary declarations
    pattern = r"(\s*)([^\s\x01]+)(\s*)\x01"
    res = re.search(pattern, pydata)
    if res:
        if numeric_keys:

            def _numeric_keys(match):
                if str(match.group(2)).isdigit():
                    return match.group(1) + match.group(2) + match.group(3) + ":"
                else:
                    return match.group(1) + '"' + match.group(2) + '"' + match.group(3) + ":"

            pydata = re.sub(pattern, _numeric_keys, pydata)
        else:
            # Quote dictionary keys
            pydata = re.sub(pattern, r'\1"\2"\3:', pydata)

    return pydata


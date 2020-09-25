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

import pytest

import luadata_to_python

def test_simple():
    luadata="""\
data['_'] = {
    display = '', -- comment
    omit_preComma = true,
    omit_postComma = true,
}"""

    pydata = """\
data = {
'_': {
    "display" : '', # comment
    "omit_preComma" : True,
    "omit_postComma" : True,
},
}"""

    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True) == pydata


def test_multi():
    luadata = """\
labels['_'] = {
	display = '',
	omit_preComma = true,
	omit_postComma = true,
}

labels['also'] = {
	omit_postComma = true,
}

labels['and'] = {
	omit_preComma = true,
	omit_postComma = true,
}
aliases['&'] = 'and'
"""
    label_data = """\
label = {
'_': {
    "display" : '',
    "omit_preComma" : True,
    "omit_postComma" : True,
},
'also': {
    "omit_postComma" : True,
},
'and': {
    "omit_preComma" : True,
    "omit_postComma" : True,
},
}"""

    alias_data = """\
alias = {
'&': 'and',
}"""

    assert luadata_to_python.convert(luadata, "labels", "label", trim_newlines=True, no_warning=True) == label_data
    assert luadata_to_python.convert(luadata, "aliases", "alias", trim_newlines=True, no_warning=True) == alias_data

def test_comments():
    luadata="""\
data['_'] = {
    display = '', -- comment
    omit_preComma = true,
    omit_postComma = true,
} -- comment"""

    pydata = """\
data = {
'_': {
    "display" : '', # comment
    "omit_preComma" : True,
    "omit_postComma" : True,
}, # comment
}"""

    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True) == pydata


def test_numeric():
    luadata="""\
data['_'] = {
    1 = '', -- comment
    omit_preComma = true,
    omit_postComma = true,
} -- comment"""

    pydata = """\
data = {
'_': {
    1 : '', # comment
    "omit_preComma" : True,
    "omit_postComma" : True,
}, # comment
}"""

    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True, numeric_keys=True) == pydata



def test_singleline():
    luadata="""\
data['test'] = {}
data['test2'] = {}
"""

    pydata = """\
data = {
'test': {},
'test2': {},
}"""

    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True, numeric_keys=True) == pydata

def test_skipunquoted():
    luadata="""\
data['test'] = {}
data[test2] = {}
"""

    pydata = """\
data = {
'test': {},
}"""

    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True, numeric_keys=True) == pydata


def test_luabrackets():
    luadata="""\
data["-ír"] = {
    ["embaír"] = "embaír",
    ["oír"] = "oír",
    ["reír"] = "-eír",
    ["-eír"] = "-eír",
    ["freír"] = "-eír",
    ["refreír"] = "-eír",
} """

    pydata = """\
data = {
"-ír": {
      "embaír": "embaír",
      "oír": "oír",
      "reír": "-eír",
      "-eír": "-eír",
      "freír": "-eír",
      "refreír": "-eír",
},
}"""
    assert luadata_to_python.convert(luadata, "data", "data", trim_newlines=True, no_warning=True, numeric_keys=True) == pydata

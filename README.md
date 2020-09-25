Converts simple Lua data assignments to Python data, works just well enough to parse
very basic lua data structures used by en.wiktionary.org, particularly those used by
Template:es-conj and Module:labels/data

WARNING: This will take publicly modifiable text and turn it in to Python code,
which is a major security risk. You must manually review all generated code before
passing it to a Python interpreter.

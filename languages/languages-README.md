# Language Data Storage
Localized identifiers, as well as keywords, are kept in language-code-named folders here.

## Python Modules:
Path          | Description
--------------|------------
`gen.py`      | Generate language files by importing a module from PyPI then indexing it into JSON (you must have `pip install`ed the module first)
`language.py` | Inner classes to act as a means for fetching, processing and saving language file data

## JSON Structure
> Inside a language-code-named folder:

### Files present
Path      |Description
----------|-----------
`.kw.json`|Keywords and their localized names
`.literals.json`|Literal datatype [lexer/parser](../compilers) names and their corresponding paths
`.pkgs.json`|Translated package names
`.json`|Built-in module localized names
`<module-name>.json`|Localized name mapping for external from PyPI/local-but-need-to-be-imported modules (including `os`, `turtle`... as well as `pygame`, `matplotlib`...)

### JSON Format
#### `.kw.json`
```json
{
  "translated_token": "ENGLISH_TOKEN_ID",
  "translated_token_2": "ENGLISH_TOKEN_ID_2",
  ...
}
```
#### `.pkgs.json`
```json
{
  "translated_pkg_name": "official_pkg_name",
  ...
}
```
#### `.literals.json`
```json
{
  "ENGLISH_TOKEN_ID": [["path", "in", "builtins", "(.json)"], ["another", "path"]],
  "STRING": [["str"]],
  "NUMBER": [["int"], ["float"]],
  "LIST": [["list"]],
  ...
}
```
#### Module Mappings (`.json`/`<module-name>.json`)
```json
// Each obj is structured like this, starting from the root:
<obj> = [
  "translated_name",
    {
      // Inner properties
      "english_name": <obj>,
      "english_name_2": <obj>,
      ...
    },
    [
      // Arguments if callable
      "a",
      ...
    ],
    [
      // Base class(es)/return type(s)
      ["str"],
      ["english", "path", "to", "class"],
      ...
    ]
]
```
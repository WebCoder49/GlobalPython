import json

import compilers.python
import languages.language
import time
from os import system


# Debug functions
def annotate_mappings(new_struct, translated: str):
    """Get compiled text annotated with translated mappings"""
    compiled_result = ""
    last_compiled_index = 0
    last_translated_index = 0
    for mapping in new_struct.mappings:
        # (translated, compiled)
        compiled_result += new_struct.compiled[last_compiled_index:mapping[1]].replace("\n",
                                                                                       "\\n") + " /=/ " + translated[
                                                                                                          last_translated_index:
                                                                                                          mapping[
                                                                                                              0]].replace(
            "\n", "\\n") + "\n"

        last_compiled_index = mapping[1]
        last_translated_index = mapping[0]
    compiled_result += new_struct.compiled[last_compiled_index:].replace("\n", "\\n") + " /=/ " + translated[
                                                                                                  last_translated_index:].replace(
        "\n", "\\n") + "\n"

    return compiled_result


def compile(lang_dir: str, source_file: str, dest_file: str, debug_file: str):
    """Compile the code from the language in source to English Python in dest, saving the mappings in debug_file in JSON format if it's not None."""
    # Get language files
    language = languages.language.LanguageEnv(lang_dir)
    # Build the lexer and parser
    lexer = compilers.python.PythonLexer(language)
    lexer.build()
    parser = compilers.python.PythonParser(language, lexer)
    parser.build()
    # Run lexer and parser on source file
    with open(source_file, "r", encoding='utf8') as reader:
        src = reader.read()
    result = parser.parse(src)
    # Write compiled code
    with open(dest_file, "w", encoding='utf8') as writer:
        writer.write(str(result))

    # Write debug code
    """Format:
    "mappings": [[translated_index,compiled_index],...]",
    "line_mappings: [translated_line,...] """  # For each compiled line, 1-indexed
    if (debug_file is not None):
        debug_data = {}

        # Encode mappings
        mappings = result.mappings

        # Get line mappings
        lines = [None] + result.compiled.split("\n")
        len_lines = len(lines)
        next_i = 0
        line = 1
        translated_lines = [None] + src.split("\n")
        len_translated_lines = len(translated_lines)
        translated_line = 1  # 1-indexed
        translated_i = 0
        line_mappings = [0]  # Line 0 > 0
        for mapping in result.mappings:
            if (mapping[1] >= next_i):
                # Update translated line
                while (translated_i < mapping[0] and translated_line < len_translated_lines):
                    translated_line += 1
                    translated_i += len(translated_lines[translated_line - 1])
                # Add mapping
                line_mappings.append(translated_line - 1)  # Look for previous line
                # Update next_i - only 1 for each compiled line
                if (line < len_lines):
                    next_i += len(lines[line])
                    line += 1
                else:
                    # End Of File
                    break

        debug_data["mappings"] = mappings
        debug_data["line_mappings"] = line_mappings
        # Imported modules
        if("imported" in result.attr):
            debug_data["imported"] = result.attr["imported"]  # [[translated_module_path, location_path]...]
        else:
            debug_data["imported"] = []

        with open(debug_file, "w", encoding='utf8') as writer:
            json.dump(debug_data, writer)
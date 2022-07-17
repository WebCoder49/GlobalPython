"""Debug running programs"""
import inspect
import json, os

import traceback

import importlib.machinery
import importlib.util

from _io import TextIOWrapper
import sys

from languages.language import LanguageEnv


# TODO: Add support for many files
class Debugger:
    def __init__(self, compiled_file: str, source_file:str, debug_file: str, language_path:str):
        self.language_code = language_path
        self._lang = None # Lazily-loaded LanguageEnv

        self.source_file = source_file
        self.compiled_file = compiled_file

        # Read debug file
        self.load_debug_file(debug_file)
        # print(self.get_translated_pos(100))  # on line: frase_para_escribir = nombre + ", Tienes un" - around 77
        # print(self.get_translated_pos(0))  # on line: frase_para_escribir = nombre + ", Tienes un" - around 77

        print(f"GlobalPython ({language_path})")

        # Import file by filename - https://csatlas.com/python-import-file-module/
        loader = importlib.machinery.SourceFileLoader(compiled_file.split("/")[-1].split(".")[0], compiled_file)
        spec = importlib.util.spec_from_loader(compiled_file.split("/")[-1].split(".")[0], loader)
        module = importlib.util.module_from_spec(spec)
        try:
            loader.exec_module(module)
        except:
            # Get error info (type, value, traceback) and handle
            err = sys.exc_info()
            self.process_error(err)

    def get_lang(self):
        """lazily load a LanguageEnv"""
        if(self._lang is None):
            self._lang = LanguageEnv(self.language_code)
        return self._lang

    def get_translated_pos(self, compiled_pos: int):
        """Get the next character-number position from a compiled-file position"""
        # BFS - find next (all at end of kws)
        # Choose when >=
        start = 0
        end = len(self.mappings)
        while (end - start > 1):
            mid = (start + end) // 2
            if (compiled_pos >= self.mappings[mid][1]):  # Compiled pos
                # >= mid
                start = mid
            else:
                end = mid

        return self.mappings[start][0]  # Translated pos

    def load_debug_file(self, debug_file):
        """Load a debug file by path into the debugger"""
        with open(debug_file, "r", encoding='utf8') as reader:
            self.debug_info = json.load(reader)
            self.mappings = self.debug_info["mappings"]

    def process_error(self, err):
        """Return the translated error from the error info (type, value, traceback)."""
        # Output phrase format
        message = ""
        lang = self.get_lang()

        # Error type
        path = [".PKG", err[0].__module__] + err[0].__qualname__.split(".")
        translated_data = lang.raw_path_to_data(path)
        translated_type = translated_data[0]
        if(translated_type == "<name>"): translated_type = f"!{err[0]}"

        # Translate message
        translated_msg = lang.translate_err(err[1], path, translated_data)

        # Get traceback + lineno
        tb = err[2].tb_next.tb_next.tb_next # Skip 3 levels of importing
        translated_tb = ""

        while tb is not None:
            # Get traceback info
            lineno = tb.tb_lineno
            frame_info = inspect.getframeinfo(tb.tb_frame)

            if (frame_info.filename == self.compiled_file):
                translated_lineno = int(self.debug_info["line_mappings"][lineno]) # 1-indexed
                filename = self.source_file
            else:
                filename = frame_info.filename

            if frame_info.function == "<module>":
                loc_name = f"{filename}, línea {translated_lineno}"  # Top-level
            else:
                loc_name = f"({frame_info.function}) {filename}, línea {translated_lineno}"
            loc_link = "file:///" + os.path.join(os.getcwd(), filename).replace("\\", "/") + ":" + str(translated_lineno)

            if (frame_info.filename == self.compiled_file):
                line = self.get_line(self.source_file, translated_lineno)
                translated_tb += f"\n\t{loc_name} | {line} [{loc_link}]"
            else:
                # From un-translated library
                translated_tb += f"\n\t{loc_name}"

            tb = tb.tb_next

        # Write as error
        sys.stderr.write(f"{translated_type}: {translated_msg} {translated_tb}\n")

    def get_line(self, filename:str, lineno:int):
        """Get the line in a Python file at the 1-indexed lineno"""
        with open(filename, "r", encoding="utf8") as reader:
            line = reader.readlines()[lineno-1].strip()  # Remove whitespace
        return line

debugger = Debugger('out.py', 'source.py', "debug.json", "languages/es")

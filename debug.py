"""Debug running programs"""

import json, os

from _io import TextIOWrapper
import sys


class Debugger:
    def __init__(self, compiled_file: str, debug_file: str):
        # Read debug file
        self.load_debug_file(debug_file)
        # print(self.get_translated_pos(100))  # on line: frase_para_escribir = nombre + ", Tienes un" - around 77
        # print(self.get_translated_pos(0))  # on line: frase_para_escribir = nombre + ", Tienes un" - around 77

        sys.stderr = ErrorWrapper(sys.stderr, self.process_error)

        print("Loading...")
        compiled_file_escaped = compiled_file.replace('"', '\\"')
        os.system(f'python "{compiled_file_escaped}"')  # TODO: Find better way of running python file

    def get_translated_pos(self, compiled_pos: int):
        """Get the previous character-number position from a compiled-file position"""
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
            self.mappings = list(map(
                lambda pair: tuple(map(int, pair.split("/"))),  # Translated pos, compiled pos
                self.debug_info["mappings"].split(",")  # Separate Pairs
            ))

    def process_error(self, text):
        # print("Error: ", text)

        message = "There's a " + text[-4] + " because " + text[-2] + "\n"

        for i in range(1, len(text) - 7, 4):
            message += text[i][0:-1] + " --> " + text[i + 2] + "\n"

        return message


class ErrorWrapper(TextIOWrapper):
    def __init__(self, stderr: TextIOWrapper, redirect):
        """Redirect all errors through the redirect function before outputting"""
        self.stderr = stderr  # Standard error output
        self.redirect = redirect

        self.msg = []

    def write(self, text):
        """Write an error to the console (redirected args)"""
        if (text != ""):
            self.msg.append(text)

    def flush(self):
        """Flush and write an error to the console (redirected args)"""
        if (self.msg != []):
            self.stderr.write(self.redirect(self.msg))
            self.stderr.flush()

            self.msg = []


debugger = Debugger('out.py', "debug.json")

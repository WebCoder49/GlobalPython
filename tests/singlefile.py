# Compile then debug a single file.
def run(lang_path="languages/es",
        src_path="source.py",
        dest_path="out.py",
        debug_path="debug.json"):
    print("TEST Single File")

    import compile
    compile.compile(lang_path, src_path, dest_path, debug_path)
    print("---")
    import debug
    debugger = debug.Debugger(dest_path, src_path, debug_path, lang_path)

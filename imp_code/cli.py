import argparse
import datetime
import os
# from .compiler import run_lexical, run_semantic
from .compiler import run_lexical
import time

from .components.hello import testMe

# def main():
#     testMe()
    
def main():
    parser = argparse.ArgumentParser(
        description="An object-oriented programming language inspired by Python and C++"
    )
    parser.add_argument(
        "file", nargs="?", type=str, help="The .ic file to run.", default=""
    )
    parser.add_argument(
        "--mode", "-m", choices=["lexical", "syntax"], help="Mode to run."
    )
    parser.add_argument(
        "--verbose", "-v", help="Run analysis in verbose mode.", action="store_true"
    )

    global args
    args = parser.parse_args()

    # if not args.file:
    #     cli()
    #     return

    with open(args.file, "r") as file:
        code = file.read()

    if args.mode == "lexical":
        _run_lexical(args.file, code)
    # elif args.mode == "syntax":
    #     _run_syntax(args.file, code)
    # else:
    #     _run_semantic(args.file, code)

def format_time(seconds):
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} nanoseconds"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} microseconds"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} milliseconds"
    else:
        return f"{seconds:.2f} seconds"

def log_runtime(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"\n--- Finished in {format_time(elapsed_time)} ---\n")
        return result
    return wrapper


@log_runtime
def _run_lexical(file_path, code):
    start_time = time.time()
    tokens, errors = run_lexical(file_path, code)

    if errors:
        if args.verbose: 
            print("Tokens:", tokens)
            print()
        if errors:
            for error in errors:
                print(error.as_string())
    elif args.verbose:
        print("Tokens:", tokens)

# @log_runtime
# def _run_syntax(file_path, code):
#     start_time = time.time()
#     tokens, ast, errors = run_syntax(file_path, code)

#     if errors:
#         for error in errors:
#             print(error.as_string())
#     else:
#         if args.verbose:
#             print("AST:", ast)

# @log_runtime
# def _run_semantic(file_path, code):
#     start_time = time.time()
#     tokens, ast, res, errors = run_semantic(file_path, code)
#     if errors:
#         for error in errors:
#             print(error.as_string())

# def cli():
#     now = datetime.datetime.now()
#     date = now.strftime("%a %b %d %Y %H:%M:%S")
#     python_version = os.popen("python --version").read()
#     os_ = os.popen("uname").read()
#     print(f"Imperial Code {date} [{python_version[:-1]}] on {os_[:-1].lower()}")

#     while True:
#         text = get_input()
#         if text:
#             tokens, ast, res, errors = run_semantic("<stdin>", text)

#             if errors:
#                 for error in errors:
#                     print(error.as_string())


# def get_input():
#     text = ""
#     tmp_text = ""
#     prompt = ">>> "
#     while True:
#         try:
#             tmp_text = input(prompt)
#             text += tmp_text + "\n"
#             if tmp_text == "":
#                 break
#             elif tmp_text == "exit":
#                 exit()
#             prompt = "... "
#         except KeyboardInterrupt:
#             print()
#             print("Type 'exit' or ctrl + D to exit")
#             text = ""
#             break
#     return text


if __name__ == "__main__":
    main()
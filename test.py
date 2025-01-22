from imp_code.compiler import run_lexical

filename = "sample.ic"

with open(filename, "r") as file:
    text = file.read()
    tokens, errors = run_lexical(filename, text)

    print(tokens)
    if errors:
        for error in errors:
            print(error)
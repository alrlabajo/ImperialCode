from imp_code.compiler import run_semantic

filename = "syn.ic"

with open(filename, "r") as file:
    text = file.read()
    tokens, ast, errors = run_semantic(filename, text)

    if errors:
        for error in errors:
            print(error.as_string())
    else:
        print(ast)


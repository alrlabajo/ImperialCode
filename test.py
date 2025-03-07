from imp_code.compiler import run_syntax

filename = "syn.ic"

with open(filename, "r") as file:
    text = file.read()
    tokens, ast, errors = run_syntax(filename, text)

    print(tokens)
    if errors:
        for error in errors:
            print(error.as_string())
    else:
        print("AST:", ast)
        print()
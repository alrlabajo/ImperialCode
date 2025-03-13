from imp_code.compiler import run_syntax

filename = "syn.ic"

with open(filename, "r") as file:
    text = file.read()
    tokens, ast, errors = run_syntax(filename, text)

    if errors:
        print("❌ Syntax Errors Found:\n")
        for error_list in errors:  # errors is a list of lists
            for error in error_list:  # error_list contains actual error objects
                print(error.as_string())  # Now this should work
                print("-" * 50)
    else:
        print("✅ No syntax errors found.")


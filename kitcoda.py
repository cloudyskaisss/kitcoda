import os
import sys
import shlex
import io
import contextlib

def run_and_capture(line, variables, functions):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        run_line(line, variables, functions)
    return buffer.getvalue().strip()

def resolve_value(word, variables):
    return variables[word][0] if word in variables else word

def strip_comment(line):
    in_quote = False
    result = ""
    for i, char in enumerate(line):
        if char == '"' and (i == 0 or line[i - 1] != "\\"):
            in_quote = not in_quote
        if char == "#" and not in_quote:
            break
        result += char
    return result.strip()



def import_functions_only(path, functions):
    with open(path, "r") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        try:
            line = strip_comment(line)
            words = shlex.split(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if len(words) == 3 and words[0] == "purr" and words[2] == "{":
            funcname = words[1]
            func_lines = []
            i += 1
            while i < len(lines):
                fline = lines[i].strip()
                if fline == "}":
                    break
                func_lines.append(fline)
                i += 1
            functions[funcname] = func_lines
        else:
            pass  # ignore anything else

        i += 1


def run_line(line, variables, functions):
    try:
        line = strip_comment(line)

        # ✨ check this early!
        is_inline_block = "{" in line and line.strip().endswith("}")

        words = shlex.split(line)
    except ValueError as e:
        print(f"[kitcoda error]: {e}")
        return

    if not line:
        return
    if not words:
        return
    
    cmd = words[0]
    if cmd == "meow":
        printstr = words[1:]
        output = [resolve_value(w, variables) for w in printstr]
        print(" ".join(output), flush=True)
    elif cmd == "sit":
        if len(words) >= 4 and words[2] == "is":
            varname = words[1]
            value_line = " ".join(words[3:])
            if value_line.startswith("add ") or value_line.startswith("pounce ") or (value_line.startswith("bap ") and (value_line.endswith("}"))):
                result = run_line(value_line, variables, functions)
                if result is None:
                    result = ""

                variables[varname] = [result]
            else:
                variables[varname] = [value_line]

    elif cmd == "eat":
        if len(words) >= 3 and words[2] == "is":
            varname = words[1]
            prompt = " ".join(words[3:]).strip()
            value = input(prompt)
            variables[varname] = [value.strip()]
    elif cmd == "bap":
        if len(words) >= 6 and words[2] in ["is", "isnt"] and words[3] == "like":
            val1 = resolve_value(words[1], variables)
            val2 = resolve_value(words[4], variables)
            baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

            if is_inline_block:
                line = strip_comment(line)  # 🆕 Fix here
                inner = line[line.index("{")+1:line.rindex("}")].strip()
                if baptruth:
                    if inner.startswith('"') and inner.endswith('"'):
                        return inner.strip('"')
                    return run_and_capture(inner, variables, functions)
                else:
                    return ""

            else:
                print("[kitcoda error] multiline bap blocks must be in a REPL or file.")
                return ""





    elif cmd == "pounce":
        funcname = words[1]
        if funcname in functions:
            for fline in functions[funcname]:
                run_line(fline, variables, functions)
    elif cmd == "sip":
        if len(words) >= 2:
            import_path = resolve_value(words[1], variables)
            if os.path.exists(import_path) and import_path.endswith(".kit"):
                import_functions_only(import_path, functions)
            else:
                print(f"[kitcoda error] could not sip file '{import_path}'")
    elif cmd in ["add", "subtract", "multiply", "divide"]:
        if words[1].isdigit() and words[2] == "with" and words[3].isdigit():
            num1 = int(words[1])
            num2 = int(words[3])
            if cmd == "add":
                result = num1+num2
            elif cmd == "subtract":
                result = num1-num2
            elif cmd == "multiply":
                result = num1*num2
            elif cmd == "divide":
                result = num1/num2
            else:
                print("Syntax error")
            return str(result)

    elif cmd == "nap":
        exit()
    else:
        print("Invalid command.")

def compile():
    i = 0
    variables = {}
    functions = {}
    lines = []
    while True:
        line = input(":3 ")
        lines.append(line)
        try:
            line = strip_comment(line)
            words = shlex.split(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if not words:
            i += 1
            continue

        cmd = words[0].lower()

        if cmd == "purr":
            if len(words) == 3 and words[2] == "{":
                funcname = words[1]
                func_lines = []
                while True:
                    fline = input("... ").strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                functions[funcname] = func_lines
        elif cmd == "bap":
            if len(words) >= 6 and (words[2] == "is" or words[2] == "isnt") and words[3] == "like" and words[5] == "{":
                var1 = words[1]
                var2 = words[4]

                val1 = resolve_value(var1, variables)
                val2 = resolve_value(var2, variables)

                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                block_lines = []
                while True:
                    block_line = input("... ").strip()
                    if block_line == "}":
                        break
                    block_lines.append(block_line)

                if baptruth:
                    for bl in block_lines:
                        run_line(bl, variables, functions)
        else:
            run_line(line, variables, functions)

        i += 1


def main():
    i = 0
    variables = {}
    functions = {}

    if len(sys.argv) > 1:
        file = sys.argv[1]
        if os.path.exists(file) and file.endswith(".kit"):
            dir = file
        else:
            print("Invalid directory.")
            exit()
    else:
        compile()

    with open(dir, "r") as d:
        filecontents = d.read()
    if not filecontents.strip():
        print("File is empty.")
        exit()

    lines = filecontents.splitlines()

    while i < len(lines):
        line = lines[i]
        try:
            line = strip_comment(line)
            words = shlex.split(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if not words:
            i += 1
            continue

        cmd = words[0]

        if cmd == "purr":
            if len(words) == 3 and words[2] == "{":
                funcname = words[1]
                func_lines = []
                i += 1
                while i < len(lines):
                    fline = lines[i].strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                    i += 1
                functions[funcname] = func_lines


        elif cmd == "bap":
            if len(words) >= 6 and words[2] in ["is", "isnt"] and words[3] == "like":
                val1 = resolve_value(words[1], variables)
                val2 = resolve_value(words[4], variables)
                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                if "{" in line and line.strip().endswith("}"):
                    # INLINE one-liner version
                    inner = line[line.index("{")+1:line.rindex("}")].strip()
                    if baptruth:
                        run_line(inner, variables, functions)
                else:
                    # MULTILINE block version
                    block_lines = []
                    i += 1
                    while i < len(lines):
                        block_line = lines[i].strip()
                        if block_line == "}":
                            break
                        block_lines.append(block_line)
                        i += 1

                    if baptruth:
                        for bl in block_lines:
                            run_line(bl, variables, functions)

        else:
            run_line(line, variables, functions)

        i += 1
        

main()

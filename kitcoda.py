import os
import sys
import shlex
import io
import contextlib
import re

def tokenize(line):
    """
    Custom tokenizer that splits like tokenize(),
    but handles nested quotes and escaped quotes.
    """
    pattern = r'''
        (                               # Start group
            "(?:\\.|[^"\\])*"           # Double-quoted string, support escapes
            | '(?:\\.|[^'\\])*'         # Single-quoted string, support escapes
            | [^\s"']+                  # Or bareword
        )
    '''
    return [tok.strip() for tok in re.findall(pattern, line, re.VERBOSE)]


def extract_block(lines, start_index):
    block_lines = []
    i = start_index + 1
    while i < len(lines):
        line = lines[i].strip()
        if line == "}":
            break
        block_lines.append(line)
        i += 1
    return block_lines, i

def run_and_capture(line, variables, functions, repl_mode=False):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        run_line(line, variables, functions)
    return buffer.getvalue().strip()

def resolve_value(word, variables):
    if word in variables:
        return variables[word][0]
    if (word.startswith('"') and word.endswith('"')) or (word.startswith("'") and word.endswith("'")):
        return word[1:-1]
    return word


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
            words = tokenize(line)
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


def run_line(line, variables, functions, repl_mode=False):
    if line in ["{", "}", "bop {"]:
        return  # quietly skip control flow markers
    try:
        line = strip_comment(line)

        # ✨ check this early!
        is_inline_block = "{" in line and line.strip().endswith("}")

        words = tokenize(line)
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
            elif value_line in variables:
                variables[varname] = [variables[value_line][0]]
            else:
                variables[varname] = [value_line]

    elif cmd == "eat":
        if len(words) >= 3 and words[2] == "is":
            varname = words[1]
            prompt = " ".join(words[3:]).strip()
            value = input(prompt)
            variables[varname] = [value.strip()]
    elif cmd == "bap":
        if len(words) >= 6 and words[2] in ["is", "isn't", "isnt"] and words[3] == "like":
            val1 = resolve_value(words[1], variables)
            val2 = resolve_value(words[4], variables)
            baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

            if is_inline_block:
                clean = strip_comment(line)
                # bop check (inline else)
                if "} bop {" in clean:
                    before_else, after_else = clean.split("} bop {", 1)
                    true_block = before_else.split("{", 1)[1].strip()
                    false_block = after_else.rsplit("}", 1)[0].strip()
                else:
                    true_block = clean.split("{", 1)[1].rsplit("}", 1)[0].strip()
                    false_block = None

                block = true_block if baptruth else false_block
                if block:
                    result = run_and_capture(block, variables, functions)
                    return result if result else ("true" if baptruth else "false")
                else:
                    return "true" if baptruth else "false"
            else:
                # Multiline block handler (used in compile()/main())
                return "true" if baptruth else "false"







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
    elif cmd == "spin":
        block = []

        if "{" in line and line.strip().endswith("}"):
            # inline block: spin 3 {meow "hi"}
            inner = line[line.index("{")+1:line.rindex("}")].strip()
            block = [inner]
        elif repl_mode:
            # multiline input in REPL
            while True:
                block_line = input("... ").strip()
                if block_line == "}":
                    break
                block.append(block_line)
        else:
            # in file mode, block should already be extracted
            print("[kitcoda error] Multiline spin blocks must be pre-parsed in file mode.")
            return

        if words[1].isdigit():
            count = int(words[1])
            for _ in range(count):
                for b in block:
                    run_line(b, variables, functions, repl_mode=repl_mode)

        elif words[1] == "while":
            brace_index = line.index("{")
            cond = line[line.index("while") + 5 : brace_index].strip()
            while True:
                result = run_and_capture(f"bap {cond} {{ \"true\" }}", variables, functions, repl_mode=repl_mode)
                if result.strip() != "true":
                    break
                for b in block:
                    run_line(b, variables, functions, repl_mode=repl_mode)




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
            words = tokenize(line)
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
            if "{" in line and line.strip().endswith("}"):
                result = run_line(line, variables, functions)
                if result is not None and result != "":
                    print(result)
                i += 1
                continue

            if len(words) >= 6 and words[2] in ["is", "isn't", "isnt"] and words[3] == "like" and words[5] == "{":
                val1 = resolve_value(words[1], variables)
                val2 = resolve_value(words[4], variables)
                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                block_lines = []
                else_lines = []
                collecting_else = False

                while True:
                    block_line = input("... ").strip()
                    if block_line == "}":
                        # check if next line is 'bop {'
                        next_line = input("... ").strip()
                        if next_line == "bop {":
                            collecting_else = True
                            continue
                        else:
                            break
                    elif block_line == "} bop {":
                        collecting_else = True
                        continue
                    elif collecting_else:
                        else_lines.append(block_line)
                    else:
                        block_lines.append(block_line)

                chosen_block = block_lines if baptruth else else_lines
                for bl in chosen_block:
                    result = run_line(bl, variables, functions)
                    if result is not None and result != "":
                        print(result)
            else:
                print(f"[kitcoda error] Invalid syntax: {line}")
        else:
            result = run_line(line, variables, functions, repl_mode=True)
            if result is not None and result != "":
                print(result)

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
            words = tokenize(line)
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
            if len(words) >= 6 and words[2] in ["is", "isn't", "isnt"] and words[3] == "like":
                val1 = resolve_value(words[1], variables)
                val2 = resolve_value(words[4], variables)
                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                if "{" in line and line.strip().endswith("}"):
                    # INLINE
                    inner = line[line.index("{")+1:line.rindex("}")].strip()
                    if baptruth:
                        run_line(inner, variables, functions)
                else:
                    # MULTILINE
                    i += 1
                    block_lines = []
                    else_lines = []
                    collecting_else = False

                    while i < len(lines):
                        block_line = lines[i].strip()
                        if block_line == "}":
                            # Check if next line is 'bop {'
                            if i + 1 < len(lines) and lines[i + 1].strip() == "bop {":
                                collecting_else = True
                                i += 2  # skip over the 'bop {' line
                                continue
                            else:
                                break
                        elif collecting_else:
                            else_lines.append(block_line)
                        else:
                            block_lines.append(block_line)
                        i += 1

                    chosen_block = block_lines if baptruth else else_lines

                    for bl in chosen_block:
                        run_line(bl, variables, functions)

                    continue  # skip extra i += 1

        else:
            run_line(line, variables, functions, repl_mode=False)

        i += 1
        

main()

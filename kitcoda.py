import os
import sys
import shlex

def resolve_value(word, variables):
    return variables[word][0] if word in variables else word

def process_kit_file(path, variables, functions):
    with open(path, "r") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        try:
            words = shlex.split(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if words[0] == "purr" and len(words) == 3 and words[2] == "{":
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
            run_line(line, variables, functions)

        i += 1

def run_line(line, variables, functions):
    try:
        words = shlex.split(line)
    except ValueError as e:
        print(f"[kitcoda error]: {e}")
        return

    if not words:
        return

    cmd = words[0]

    if cmd == "meow":
        printstr = words[1:]
        output = [resolve_value(w, variables) for w in printstr]
        print(" ".join(output))

    elif cmd == "sit":
        if len(words) >= 4 and words[2] == "is":
            varname = words[1]
            varvalue = " ".join(words[3:]).strip()
            variables[varname] = [varvalue]

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
                    for block_line in block_lines:
                        try:
                            eaten_words = shlex.split(block_line)
                        except ValueError as e:
                            print(f"[kitcoda error] line {i+1}: {e}")
                            i += 1
                            continue

                        if not eaten_words:
                            continue
                        eaten_cmd = eaten_words[0]
                        if eaten_cmd == "meow":
                            printstr = eaten_words[1:]
                            output = []
                            for str in printstr:
                                output.append(resolve_value(str, variables))

                            print(" ".join(output))

    elif cmd == "eat":
        if len(words) >= 3 and words[2] == "is":
            varname = words[1]
            varvalue = input(" ".join(words[3:]).strip())
            variables[varname] = [varvalue.strip()]

    elif cmd == "pounce":
        funcname = words[1]
        if funcname in functions:
            for fline in functions[funcname]:
                run_line(fline, variables, functions)
    
    elif cmd == "sip":
        if len(words) >= 2:
            import_path = resolve_value(words[1], variables)
            if os.path.exists(import_path) and import_path.endswith(".kit"):
                with open(import_path, "r") as f:
                    import_lines = f.read().splitlines()
                process_kit_file(import_path, variables, functions)
            else:
                print(f"[kitcoda error] could not sip file '{import_path}'")


    elif cmd == "nap":
        exit()


def compile():
    i = 0
    variables = {}
    functions = {}
    lines = []
    while True:
        line = input(":3 ")
        lines.append(line)
        try:
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
                while True:
                    fline = input("... ").strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                functions[funcname] = func_lines
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
                while True:
                    fline = input("... ").strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                functions[funcname] = func_lines
        else:
            run_line(line, variables, functions)

        i += 1

main()

import os
import sys
import shlex

def resolve_value(word, variables):
    return variables[word][0] if word in variables else word


def main():
    i = 0
    variables = {}

    if len(sys.argv) > 1:
        file = sys.argv[1]
        if os.path.exists(file) and file.endswith(".kit"):
            dir = file
        else:
            print("Invalid directory.")
            exit()
    else:
        print("No input file provided.")
        exit()

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

        if cmd == "meow":
            printstr = words[1:]
            output = []
            for str in printstr:
                output.append(resolve_value(str, variables))

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
                i += 1
                while i < len(lines):
                    block_line = lines[i].strip()
                    if block_line == "}":
                        break
                    block_lines.append(block_line)
                    i += 1

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
        elif cmd == "sleep":
            exit()

        i += 1

main()

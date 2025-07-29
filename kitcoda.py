import os
import sys

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
        words = line.split()
        if not words:
            i += 1
            continue

        cmd = words[0]

        if cmd == "meow":
            printstr = words[1:]
            output = []
            for str in printstr:
                if str in variables:
                    output.append(variables[str][0])
                else:
                    output.append(str)
            print(" ".join(output))

        elif cmd == "sit":
            if len(words) >= 4 and words[2] == "is":
                varname = words[1]
                varvalue = " ".join(words[3:]).strip()
                variables[varname] = [varvalue]

        elif cmd == "bap":
            if len(words) >= 6 and (words[2] == "is" or words[2] == "isn't") and words[3] == "like" and words[5] == "{":
                var1 = words[1]
                var2 = words[4]

                if var1 not in variables or var2 not in variables:
                    print("Invalid variables in bap.")
                    i += 1
                    continue

                val1 = variables[var1][0]
                val2 = variables[var2][0]

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
                        eaten_words = block_line.split()
                        if not eaten_words:
                            continue
                        eaten_cmd = eaten_words[0]
                        if eaten_cmd == "meow":
                            printstr = eaten_words[1:]
                            output = []
                            for str in printstr:
                                if str in variables:
                                    output.append(variables[str][0])
                                else:
                                    output.append(str)
                            print(" ".join(output))
        elif cmd == "sleep":
            exit()

        i += 1

main()

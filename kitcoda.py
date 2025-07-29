import os
import sys



def main():
    i = 0
    variables = {}
    if len(sys.argv) > 1:
        file = sys.argv[1]
        if os.path.exists(file) and file[-4:] == ".kit":
            dir = sys.argv[1]
        else:
            print("Invalid directory.")
            exit()

    with open(dir, "r") as d:
        filecontents = d.read()
    if filecontents != "":
        filecontents = filecontents
    else:
        print("File is empty.")
        exit()
    

    lines = filecontents.splitlines()
    for line in lines:
        words = line.split()
        cmd = words[0]
        if cmd == "meow":
            printstr = line.split()[1:]
            if printstr:
                for str in printstr:
                    for var in variables:
                        if str == var:
                            for v in variables[var]:
                                print(v)
                            return
                    print(str + " ")
            else:
                print("Invalid syntax.")
        elif cmd == "sit":
            if words[1] and words[2] == "is" and words[3]:
                varname = words[1]
                varvalue = words[3:]
                tempvarvalue = ""
                for f in varvalue:
                    tempvarvalue = tempvarvalue + f + " "
                varvalue = tempvarvalue
                varvalue = varvalue[:-1]
                variables[varname] = [varvalue]
        elif cmd == "sleep":
            exit()
        i += 1

main()

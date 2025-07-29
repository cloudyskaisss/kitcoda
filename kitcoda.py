import os
import sys

DIR = ""
FILECONTENTS = ""


def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
        if os.path.exists(file) and file[-4:] == ".kit":
            DIR = sys.argv[1]
        else:
            print("Invalid directory.")
            exit()

    with open(DIR, "r") as d:
        FILECONTENTS = d.read()
    if FILECONTENTS != "":
        FILECONTENTS = FILECONTENTS
    else:
        print("File is empty.")
        exit()
    

    lines = FILECONTENTS.splitlines()
    for line in lines:
        words = line.split()
        for word in words:
            if word == "meow":
                printstr = line.split()[1:]
                if printstr:
                    for str in printstr:
                        print(str + " ")

main()

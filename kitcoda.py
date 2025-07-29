import os
import sys

DIR = ""
FILECONTENTS = ""


def main():
    if len(sys.argv) > 1:
        FILE = sys.argv[1]
        if os.path.exists(FILE):
            DIR = sys.argv[1]
        else:
            print("Invalid directory.")
            exit()

    with open(DIR, "r") as d:
        FILECONTENTS = d.read()
    if FILECONTENTS != "":
        print("yippee!")
    else:
        print("aww man...")

main()
import sys
import subprocess
import os

if sys.platform.startswith("win"):
    platform = "win"
elif sys.platform.startswith("linux"):
    platform = "linux"
elif sys.platform.startswith("darwin"):
    platform = "darwin"
else:
    print("You are attempting to run this script on an invalid system. Catnip only works on Windows, Mac, and Linux.")
    exit()

if len(sys.argv) > 1:
    packages = sys.argv[1:]
    for package in packages:
        if ".kit" in package:
            url = f"https://raw.githubusercontent.com/cloudyskaisss/kitcoda/refs/heads/main/{package}"
            
        else:
            url = f"https://raw.githubusercontent.com/cloudyskaisss/kitcoda/refs/heads/main/{package}.kit"
        
        print(subprocess.check_output(['curl', url]))
        if subprocess.check_output(['curl', url]) == b"404: Not Found":
            if platform == "win":
                os.system("cls")
            else:
                os.system("clear")
            print(f"Invalid package {package}")
            exit()
else:
    print("Please input a package to download.")
    exit()

os.system(f'curl {url} > {package}')

#!/usr/bin/env python
import subprocess, requests, sys, getopt, os, shutil
key = "0C263D8C22DCB085894899C3A3796383E9BF9DE0CBFB08C9BF2DEF2E84F29D74"
repak_url = "https://github.com/natimerry/repak-rivals/releases/download/0.5.8/repak_cli-installer.sh"
argumentList = sys.argv[1:]
options = "hf:"

def initializeScript():
    result = checkRepakInstalled()
    if str(result) == "None":
        installRepak()
        main()
    else:
        formattedVersion = str(result).split(" ")[1].split("\\n")[0]
        print("Repak installed. Version: " + formattedVersion)
        main()

def main():
    try:
        arguments, values = getopt.getopt(argumentList, options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h"):
                print("Usage: repak-file.py -f <file>")
            elif currentArgument in ("-f"):
                # Display the argument after the -f or --file
                print(("File name: " + currentValue))
                fileName = currentValue
                runRepak(fileName)
    except getopt.error as err:
        print(str(err))

def runRepak(file):
    #Run unpack `repak --aes-key 0C263D8C22DCB085894899C3A3796383E9BF9DE0CBFB08C9BF2DEF2E84F29D74 unpack [file] --verbose`
    subprocess.run(["repak", "--aes-key", key, "unpack", file, "--verbose"])
    #Delete the file
    os.remove(file)
    #Get the folder name by removing the extension
    folder = file.split(".")[0]
    print("Folder: " + folder)
    #Pack the folder back `repak--aes-key 0C263D8C22DCB085894899C3A3796383E9BF9DE0CBFB08C9BF2DEF2E84F29D74 pack "%%~dpnF" --version V11 --verbose --patch-uasset --compression Oodle`
    subprocess.run(["repak", "--aes-key", key, "pack", folder, "--version", "V11", "--verbose", "--patch-uasset", "--compression", "Oodle"])
    #Remove the folder
    shutil.rmtree(folder)
    #Rename the file to the old name but with _9999999 added before _P.pak
    tempFolderName = folder[:-2]
    print("Temp folder name: " + tempFolderName)
    NewFileName = tempFolderName + "_9999999_P.pak"
    os.rename(file, NewFileName)

def checkRepakInstalled():
    try:
        return subprocess.check_output(['repak', '--version'])
    except:
        print("Repak not installed. Installing repak...")

def installRepak():
    #Download file
    print("Downloading repak file...")
    r = requests.get(repak_url)
    with open("repak_cli-installer.sh", "wb") as code:
        code.write(r.content)
    print("Downloaded repak file...")
    #Install repak
    print("Installing repak...")
    os.system("chmod +x repak_cli-installer.sh")
    os.system("./repak_cli-installer.sh")


initializeScript()

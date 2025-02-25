#!/usr/bin/env python
import subprocess, requests, sys, getopt, os, shutil, packaging.version, re

key = "0C263D8C22DCB085894899C3A3796383E9BF9DE0CBFB08C9BF2DEF2E84F29D74"
repak_url = "https://github.com/natimerry/repak-rivals/releases/download/v0.7.1/repak_cli-installer.sh"
argumentList = sys.argv[1:]
options = "hfu"

def get_new_name(folder_name):
    lower_name = folder_name.lower()
    has_9999999 = '_9999999' in lower_name
    has_p = '_p' in lower_name

    new_name = folder_name
    if not has_9999999:
        new_name += '_9999999'
    if not has_p:
        new_name += '_P'

    new_name = re.sub(r'_p_9999999', '_9999999_P', new_name, flags=re.IGNORECASE)
    new_name += '.pak'
    return new_name

def process_pak_file(pak_file):
    if not os.path.isfile(pak_file):
        print(f"Error: {pak_file} does not exist.")
        return

    abs_pak_file = os.path.abspath(pak_file)
    parent_dir = os.path.dirname(abs_pak_file)
    file_name = os.path.basename(abs_pak_file)
    folder_name = os.path.splitext(file_name)[0]
    folder_path = os.path.join(parent_dir, folder_name)

    keep_dir = os.path.exists(folder_path)
    original_cwd = os.getcwd()

    try:
        os.chdir(parent_dir)
        subprocess.run(["repak", "--aes-key", key, "unpack", file_name, "--verbose"])
        os.remove(file_name)
        subprocess.run(["repak", "--aes-key", key, "pack", folder_name, "--version", "V11", "--verbose", "--patch-uasset", "--compression", "Oodle"])

        new_name = get_new_name(folder_name)
        generated_pak = f"{folder_name}.pak"
        os.rename(generated_pak, new_name)

        if not keep_dir:
            shutil.rmtree(folder_name)
    finally:
        os.chdir(original_cwd)

def process_update(path):
    if os.path.isdir(path):
        print("Folder patching is not currently supported")
    elif os.path.isfile(path):
        if path.lower().endswith('.pak'):
            process_pak_file(path)
        else:
            print(f"Skipping non-pak file: {path}")
    else:
        print(f"Error: {path} does not exist.")

def initializeScript():
    result = checkRepakInstalled()
    if str(result) == "None":
        installRepak()
        main()
    else:
        formattedVersion = str(result).split(" ")[1].split("\\n")[0]
        print("Repak installed. Version: " + formattedVersion)
        if packaging.version.Version(str(formattedVersion)) < packaging.version.Version("0.7.1"):
            print("Repak version is outdated. Updating repak...")
            installRepak()
            main()
        else:
            main()

def main():
    try:
        arguments, values = getopt.getopt(argumentList, options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h"):
                print("Usage: repak-file.py [-f <file> | -u <file/dir> ...]")
            elif currentArgument in ("-f"):
                print("File name: " + currentValue)
                fileName = currentValue
                runRepak(fileName)
            elif currentArgument in ("-u"):
                if not values:
                    print("Error: -u option requires at least one file")
                    sys.exit(1)
                for value in values:
                    process_update(value)
    except getopt.error as err:
        print(str(err))

def runRepak(file):
    subprocess.run(["repak", "--aes-key", key, "unpack", file, "--verbose"])
    os.remove(file)
    folder = file.split(".")[0]
    print("Folder: " + folder)
    subprocess.run(["repak", "--aes-key", key, "pack", folder, "--version", "V11", "--verbose", "--patch-uasset", "--compression", "Oodle"])
    shutil.rmtree(folder)
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
    print("Downloading repak file...")
    r = requests.get(repak_url)
    with open("repak_cli-installer.sh", "wb") as code:
        code.write(r.content)
    print("Downloaded repak file...")
    print("Installing repak...")
    os.system("chmod +x repak_cli-installer.sh")
    os.system("./repak_cli-installer.sh")

initializeScript()

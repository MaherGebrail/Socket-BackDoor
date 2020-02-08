#!/usr/bin/python3
from os import getcwd, listdir, chdir, system, getuid
from pathlib import Path
from getpass import getuser, getpass
from elevate import elevate
from subprocess import check_output,PIPE

path_ = getcwd()

if getuid() != 0:
    print("To Become perminantly super User : Enter [SUDO-ALL]")

while True:

    if getcwd() != path_:
        chdir(path_)

    if getuid() == 0:
        mark = "#"
    else:
        mark = ">"

    get_command = input(f"{getcwd()}{mark} ").strip()
    if get_command == "SUDO-ALL":
        elevate(graphical=False)

    elif "cd " in (get_command+" ")[:3]:
        try:
            chdir(get_command[2:].strip())
            path_ = getcwd()
        except FileNotFoundError:
            if get_command == "cd":
                path_ = str(Path.home())
            else:
                print("path not exist")
            pass

    else:
        try:
            if get_command[:5] == "sudo ":
                """getpass func stuck if not running in terminal ,
                 so comment it and uncomment getpass input , if running from editor"""
                get_pass_ = getpass(f"[sudo] password for {getuser()}:") #from terminal (secret pass)
                #     get_pass_ = input(f"[sudo] password for {getuser()}:") # from editor (unsecret pass)
                out = check_output(f"echo {get_pass_} |sudo {get_command[4:]}", shell=True, stderr=PIPE).decode()
                print(out)
            else:
                system(get_command)
        except:
            print("Broken Command !! ,it may get you out of this terminal !")
            pass


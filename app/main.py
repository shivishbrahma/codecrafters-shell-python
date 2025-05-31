import sys
import shutil
import os
from typing import Tuple, List
import shlex


def parse_arguments(command: str) -> Tuple[str, List[str]]:
    # command_parts = command.split(" ", maxsplit=1)
    command_parts = shlex.split(command)
    cmd = command_parts[0]
    if len(command_parts) == 1:
        return (cmd, [])

    args = command_parts[1:]

    # args = list(filter(lambda x: x.strip() != "", args))
    # print(str(args), file=sys.stderr)

    return (cmd, args)


def parse_command(command: str):
    cmd, args = parse_arguments(command)

    commands_list = ["echo", "exit", "type", "pwd"]

    if cmd == "echo":
        print(" ".join(args))
        return

    if cmd == "type":
        if len(args) == 0:
            print("{}: missing file operand".format(command))
            return

        if args[0] in commands_list:
            print("{} is a shell builtin".format(args[0]))
            return

        if path := shutil.which(args[0]):
            print("{} is {}".format(args[0], path))
            return

        print("{}: not found".format(args[0]))
        return

    if cmd == "exit":
        err_code = 0
        if len(args) > 0:
            err_code = int(args[0])
        sys.exit(err_code)

    if cmd == "pwd":
        print(os.getcwd())
        return

    if cmd == "cd":
        if len(args) == 1:
            dir_path = os.path.expanduser(args[0])
            if os.path.exists(dir_path):
                os.chdir(dir_path)
            else:
                print("{}: {}: No such file or directory".format(cmd, args[0]))
            return

    if path := shutil.which(cmd):
        os.system(command)
        return

    print("{}: command not found".format(cmd))


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    # Wait for user input
    command = input()
    parse_command(command)
    main()


if __name__ == "__main__":
    main()

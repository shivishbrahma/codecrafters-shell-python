import sys
import shutil
import os
from typing import Tuple, List
import shlex


def parse_arguments(command: str) -> Tuple[str, List[str]]:
    command_parts = shlex.split(command)
    filename = None
    is_error = False
    cmd = command_parts[0]

    if len(command_parts) == 1:
        return (cmd, [], None, is_error)

    args = command_parts[1:]
    out_op_idx = -1

    if "1>" in args:
        out_op_idx = args.index("1>")
    if "2>" in args:
        out_op_idx = args.index("2>")
        is_error = True
    if ">" in args:
        out_op_idx = args.index(">")

    if out_op_idx != -1:
        filename = args[out_op_idx + 1]
        args = args[:out_op_idx]

    return (cmd, args, filename, is_error)


def parse_command(command: str):
    cmd, args, filename, is_error = parse_arguments(command)

    if filename is None:
        file = sys.stdout
    elif is_error:
        # file = open(filename, "w")
        with open(filename, "w") as f:
            f.write("")
        file = sys.stderr
    else:
        file = open(filename, "w")

    commands_list = ["echo", "exit", "type", "pwd", "cd"]

    if cmd == "echo":
        print(" ".join(args), file=file)
        return

    if cmd == "type":
        if len(args) == 0:
            print("{}: missing file operand".format(command), file=file)
            return

        if args[0] in commands_list:
            print("{} is a shell builtin".format(args[0]), file=file)
            return

        if path := shutil.which(args[0]):
            print("{} is {}".format(args[0], path), file=file)
            return

        print("{}: not found".format(args[0]), file=file)
        return

    if cmd == "exit":
        err_code = 0
        if len(args) > 0:
            err_code = int(args[0])
        sys.exit(err_code)

    if cmd == "pwd":
        print(os.getcwd(), file=file)
        return

    if cmd == "cd":
        if len(args) == 1:
            dir_path = os.path.expanduser(args[0])
            if os.path.exists(dir_path):
                os.chdir(dir_path)
            else:
                print(
                    "{}: {}: No such file or directory".format(cmd, args[0]),
                    file=file,
                )
            return

    if path := shutil.which(cmd):
        os.system(command)
        return

    print("{}: command not found".format(cmd), file=file)


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    # Wait for user input
    command = input()
    parse_command(command)
    main()


if __name__ == "__main__":
    main()

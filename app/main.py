import sys
import shutil
import os
from typing import Tuple, List


def parse_arguments(command: str) -> Tuple[str, List[str]]:
    command_parts = command.split(" ", maxsplit=1)
    cmd = command_parts[0]
    if len(command_parts) == 1:
        return (cmd, [])

    quotes = ["'", '"']
    command_parts = command_parts[-1]
    if quotes[0] not in command_parts and quotes[1] not in command_parts:
        return (cmd, list(filter(lambda x: x.strip() != "", command_parts.split(" "))))

    args = []
    i = 0
    while i < len(command_parts):
        if command_parts[i] in quotes:
            quote_idx = quotes.index(command_parts[i])
            start_idx = i + 1
            end_idx = command_parts.find(quotes[quote_idx], start_idx)
            if end_idx == -1:
                print("{}: unmatched quote".format(command))
                return (cmd, [])
            args.append(command_parts[start_idx:end_idx])

            if (
                end_idx != len(command_parts) - 1
                and command_parts[end_idx + 1] == quotes[quote_idx]
            ):
                start_idx = end_idx + 2
                end_idx = command_parts.find(quotes[quote_idx], start_idx + 1)
                args[-1] += command_parts[start_idx:end_idx]
        else:
            start_idx = i
            end_idx = command_parts.find(" ", start_idx)
            if end_idx == -1:
                args.append(command_parts[start_idx:])
                break
            args.append(command_parts[start_idx:end_idx])
        i = end_idx + 1

    args = list(filter(lambda x: x.strip() != "", args))
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

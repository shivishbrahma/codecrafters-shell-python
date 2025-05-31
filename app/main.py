import sys
import shutil
import os


def parse_command(command):
    command_parts = command.split()

    if len(command_parts) == 0:
        return

    commands_list = ["echo", "exit", "type", "pwd"]

    if command_parts[0] == "echo":
        sys.stdout.write(" ".join(command_parts[1:]) + "\n")
        return

    if command_parts[0] == "type":
        if len(command_parts) == 1:
            sys.stdout.write("{}: missing file operand\n".format(command))
            return

        if command_parts[1] in commands_list:
            sys.stdout.write("{} is a shell builtin\n".format(command_parts[1]))
            return

        if path := shutil.which(command_parts[1]):
            sys.stdout.write("{} is {}\n".format(command_parts[1], path))
            return

        sys.stdout.write("{}: not found\n".format(command_parts[1]))
        return

    if command_parts[0] == "exit":
        sys.exit(int(command_parts[1]))

    if command_parts[0] == "pwd":
        sys.stdout.write(os.getcwd())
        sys.stdout.write("\n")
        return

    if command_parts[0] == "cd":
        if len(command_parts) > 1:
            dir_path = os.path.expanduser(command_parts[1])
            if os.path.exists(dir_path):
                os.chdir(dir_path)
            else:
                sys.stdout.write(
                    "{}: {}: No such file or directory\n".format(
                        command_parts[0], command_parts[1]
                    )
                )
            return

    if path := shutil.which(command_parts[0]):
        os.system(command)
        return

    sys.stdout.write("{}: command not found\n".format(command_parts[0]))


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    # Wait for user input
    command = input()
    parse_command(command)
    main()


if __name__ == "__main__":
    main()

import sys


def parse_command(command):
    command_parts = command.split()

    if len(command_parts) == 0:
        return

    if command_parts[0] == "echo":
        sys.stdout.write(" ".join(command_parts[1:]))
        sys.stdout.write("\n")
        return

    if command_parts[0] == "exit":
        sys.exit(int(command_parts[1]))

    sys.stdout.write("{}: command not found\n".format(command))


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    # Wait for user input
    command = input()
    parse_command(command)
    main()


if __name__ == "__main__":
    main()

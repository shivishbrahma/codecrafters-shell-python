import sys


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")

    # Wait for user input
    command = input()

    sys.stdout.write("{}: command not found\n".format(command))


if __name__ == "__main__":
    main()

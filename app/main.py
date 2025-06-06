import os
import sys
import shlex
import shutil
import readline
import subprocess
from typing import Tuple, List, Union

# Globals
commands = ["echo", "exit", "type", "pwd", "cd", "history"]
executables = {}
tab_state = {"count": 0, "last_text": ""}
history_list = []

def load_exec():
    for dir in os.getenv("PATH", "").split(os.pathsep):
        if os.path.isdir(dir):
            for file in os.listdir(dir):
                full_path = os.path.join(dir, file)
                if file not in executables and os.path.isfile(full_path):
                    executables[file] = full_path


def completer(text, state):
    load_exec()
    autocomplete_list = sorted(set(commands + list(executables.keys())))
    matches = [cmd for cmd in autocomplete_list if cmd.startswith(text)]

    if tab_state["last_text"] != text:
        tab_state["count"] = 0
        tab_state["last_text"] = text

    if state == 0 and len(matches) > 1:
        if tab_state["count"] == 0 and not all(
            match.startswith(matches[0]) for match in matches[1:]
        ):
            sys.stdout.write("\a")
            tab_state["count"] += 1
            return None
        elif tab_state["count"] == 1:
            print("\n" + "  ".join(matches))
            sys.stdout.write("$ {}".format(text))
            sys.stdout.flush()
            return text

    if state < len(matches):
        return matches[state] + " "

    sys.stdout.write("\a")
    return None


def parse_arguments(
    command: str,
) -> Tuple[List[str], List[List[str]], Union[str, None], str, bool]:
    cmd, args, filename, redirect_mode, has_pipe = [], [], None, "", False
    command_split = shlex.split(command)
    has_pipe = "|" in command_split

    command_parts, command_part = [], []
    for part in command_split:
        if part == "|":
            command_parts.append(command_part)
            command_part = []
        else:
            command_part.append(part)
    if command_part:
        command_parts.append(command_part)

    for part in command_parts:
        cmd.append(part[0])
        part_args = part[1:] if len(part) > 1 else []

        for mode in ["1>", "2>", ">", ">>", "1>>", "2>>"]:
            if mode in part_args:
                idx = part_args.index(mode)
                filename = part_args[idx + 1]
                redirect_mode = mode
                part_args = part_args[:idx]
                break

        args.append(part_args)

    return cmd, args, filename, redirect_mode, has_pipe


def run_builtin(cmd, args):
    if cmd == "echo":
        return " ".join(args) + "\n"
    if cmd == "type":
        if not args:
            return f"{cmd}: missing file operand\n"
        if args[0] in commands:
            return f"{args[0]} is a shell builtin\n"
        if path := shutil.which(args[0]):
            return f"{args[0]} is {path}\n"
        return f"{args[0]}: not found\n"
    if cmd == "exit":
        sys.exit(int(args[0]) if args else 0)
    if cmd == "pwd":
        return os.getcwd() + "\n"
    if cmd == "cd":
        if len(args) == 1:
            dir_path = os.path.expanduser(args[0])
            if os.path.exists(dir_path):
                os.chdir(dir_path)
                return None
            return f"{cmd}: {args[0]}: No such file or directory\n"

    if cmd == "history":
        # len_size = len(str(len(history_list)))
        out = ""
        for lineno, command in enumerate(history_list):
            out += f"{lineno} {command}\n"
        return out


def handle_output(stdout, stderr=None, redirect_mode="", filename=None):
    # print("Redirect_mode:", redirect_mode)
    mode = "w" if ">" in redirect_mode and ">>" not in redirect_mode else "a"
    stdout_file = (
        open(filename, mode)
        if redirect_mode.endswith(">") and not redirect_mode.startswith("2")
        else sys.stdout
    )
    stderr_file = open(filename, mode) if redirect_mode.startswith("2") else sys.stderr

    if stderr and stderr is not None:
        stderr_file.write(stderr)
    if stdout and stdout is not None:
        # print(type(stdout_file))
        stdout_file.write(stdout)


def parse_command(command: str):
    history_list.append(command)
    cmd, args, filename, redirect_mode, has_pipe = parse_arguments(command)

    # Building process chain
    processes = []
    prev_stdout = None

    for i in range(len(cmd)):
        sys_cmd = [cmd[i]] + args[i]
        stdout_target = subprocess.PIPE if i < len(cmd) - 1 or not has_pipe else None
        stdin_src = prev_stdout if prev_stdout else None

        if cmd[i] in commands:
            prev_stdout = run_builtin(cmd[i], args[i])
            if i == len(cmd) - 1:
                handle_output(
                    stdout=prev_stdout, redirect_mode=redirect_mode, filename=filename
                )
                return

        elif cmd[i] in executables:
            sys_cmd = [cmd[i]] + args[i]

            if isinstance(stdin_src, str):
                p = subprocess.Popen(
                    sys_cmd,
                    stdin=subprocess.PIPE,
                    stdout=stdout_target,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                p.stdin.write(stdin_src)
                # p.stdin.close()
            else:
                p = subprocess.Popen(
                    sys_cmd,
                    stdin=stdin_src,
                    stdout=stdout_target,
                    stderr=subprocess.PIPE,
                    text=True,
                )

            if prev_stdout and not isinstance(prev_stdout, str):
                prev_stdout.close()
            prev_stdout = p.stdout
            processes.append(p)
        else:
            print(f"{cmd[i]}: command not found")
            return

    # Wait for last process output
    stdout, stderr = processes[-1].communicate()

    handle_output(
        stdout=stdout, stderr=stderr, redirect_mode=redirect_mode, filename=filename
    )


def main():
    while True:
        try:
            command = input("$ ")
            parse_command(command)
        except EOFError:
            break


if __name__ == "__main__":
    load_exec()
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    main()

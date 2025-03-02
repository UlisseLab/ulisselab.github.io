#!/bin/env python3
import sys
import re


lines = sys.stdin.readlines()


def fix_lifetimes(lines):
    new_lines = []

    for i, line in enumerate(lines):
        match = re.match(r".+<(.+)>.+", line)
        if not match:
            new_lines.append(line)
            continue

        lifetime = match.group(1)

        if lifetime == "Infinity":
            new_lines.append(line)
            continue

        lifetime = int(lifetime)

        if lifetime >= 0:
            line = line.replace(f"<{lifetime}>", "")
            new_lines.append(line)
            continue

        new_pos = max(len(new_lines) + lifetime, 0)

        # remove the invalid lifetime
        line = line.replace(f"<{lifetime}>", "")
        new_lines.insert(new_pos, line)

        print(f"Moved line {i + 1} -> {new_pos + 1}", file=sys.stderr)

    return new_lines


program = fix_lifetimes(lines)
program = "".join(program)


program = re.sub(r"!+", "", program)
for i in range(1, 100):
    program = re.sub(r";([\w|!|(|)]+)", r"!(\1)", program)

program = program.replace("const const const", "let")
program = program.replace("const const", "let")
program = program.replace("const var", "let")
program = program.replace("var var", "let")

program = re.sub(r"let (\d+)", r"let var_\1", program)


program = program.replace("42 +=", "var_42 +=")
program = program.replace("42 -=", "var_42 -=")
program = program.replace("42 *=", "var_42 *=")
program = program.replace("42 ^ ", "var_42 ^ ")
program = program.replace("42 = ", "var_42 = ")
program = program.replace("42 * ", "var_42 * ")
program = program.replace("42 / ", "var_42 / ")
program = program.replace("42 % ", "var_42 % ")
program = program.replace("42 + ", "var_42 + ")
program = program.replace("42 - ", "var_42 - ")
program = program.replace("!42", "!var_42")


program = re.sub("<Infinity>", "", program)
program = re.sub(r"functi (.+?) \(\) =>", r"function \1()", program)
program = re.sub(r"print", "console.log", program)

# array starts at -1 ...
program = re.sub(r"(\w+)\[(.+)\]", r"\1[\2 + 1]", program)


print(program)

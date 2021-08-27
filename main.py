from src.interpreter import FekInterpreter
from src.error import FekException
import sys, os
argv = sys.argv[1:]

if argv:
    inter = FekInterpreter(f"{argv[0]}")
    path = argv[0]
else:
    inter = FekInterpreter("<stdin>")
    path = None

def execute(string: str):
    return inter.interpret(string)

if __name__ == "__main__":
    if path is not None:
        if os.path.exists(path):
            try:
                try:
                    code = open(path).read()
                except FileNotFoundError:
                    print("File not found")
                    exit(1)
            except PermissionError:
                print("Access denied")
                exit(1)
            if code and not code.isspace():
                try:
                    print(f"[Running '{path}']\n")
                    code = execute(code)
                    print(f"\n[Exit with code: {code}]")
                    exit(code)
                except FekException as e:
                    print(e)
                    print(f"[Exit with code: 1]")
                    exit(1)
                except KeyboardInterrupt:
                    exit(0)
            exit(0)
        else:
            print("File not found")
            exit(1)
    while True:
        try:
            code = input("=> ")
            if code and not code.isspace():
                execute(code)
        except FekException as e:
            print(e)
        except (KeyboardInterrupt, EOFError):
            break
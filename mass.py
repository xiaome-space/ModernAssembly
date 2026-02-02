import os
import sys
import ast
import random
import time
import json

def parse_value(parts):
    string = []
    for i in parts:
        try:
            string.append(ast.literal_eval(i))
        except:
            string.append(i)

    label_head = []
    label_tail = []
    num = 0

    for i in string:
        if isinstance(i, str) and i:
            if i[0] in "\"'":
                label_head.append(num)
            if i[-1] in "\"'":
                label_tail.append(num)
        num += 1

    if label_head and label_tail and len(label_head) == len(label_tail):
        label_head.sort()
        label_tail.sort()

        for i in range(len(label_head)-1, -1, -1):
            start = label_head[i]
            end = label_tail[i]

            combined = " ".join(str(x) for x in string[start:end+1])

            try:
                repaired = ast.literal_eval(combined)
            except:
                if (combined[0] == combined[-1] and combined[0] in "\"'"):
                    repaired = combined[1:-1]
                else:
                    repaired = combined

            string[start:end+1] = [repaired]

    bracket_starts = []
    bracket_ends = []

    for idx, item in enumerate(string):
        if isinstance(item, str):
            if item.startswith('[') or item.startswith('{'):
                bracket_starts.append(idx)
            if item.endswith(']') or item.endswith('}'):
                bracket_ends.append(idx)

    if bracket_starts and bracket_ends and len(bracket_starts) == len(bracket_ends):
        bracket_starts.sort()
        bracket_ends.sort()

        for i in range(len(bracket_starts)-1, -1, -1):
            start = bracket_starts[i]
            end = bracket_ends[i]

            combined = " ".join(str(x) for x in string[start:end+1])

            try:
                repaired = ast.literal_eval(combined)
            except:
                repaired = combined

            string[start:end+1] = [repaired]

    return string

def init():
    global var
    var = {"ps":"/> ", "rcx":None, "code":[], "call":[], "pwd": pwd()}
    return var

def mov(name, value):
    global var
    var[name] = value
    return var

def list():
    if not var:
        print("没有任何寄存器")
        return

    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()
        table = Table(title="", box=box.ROUNDED)

        table.add_column("名称", justify="right", style="cyan")
        table.add_column("值", justify="left", style="bright_green")

        for name in var:
            table.add_row(name, str(var[name]))

        console.print(table)
    except:
        max_len = 0
        for key in var:
            key_len = len(str(key))
            if key_len > max_len:
                max_len = key_len

        for key, value in var.items():
            aligned_name = str(key).ljust(max_len)

            print(f"\x1b[36m{aligned_name}\033[0m = \033[92m{value}\033[0m")

def delete(name):
    global var
    if var.get(name):
        del var[name]
    else:
        error(["del", f"{name}"], f"寄存器 \"{name}\" 不存在", 1)

def preprocess_command(raw_cmd):
    def eval_expr(expr):
        try:
            result = eval(expr, globals(), var)
            return json.dumps(result, separators=(',', ':'))
        except:
            return f"#[{expr}]"

    result = []
    i = 0
    n = len(raw_cmd)

    while i < n:
        if raw_cmd[i:i+2] == '#[':
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if raw_cmd[j] == '[':
                    depth += 1
                elif raw_cmd[j] == ']':
                    depth -= 1
                j += 1

            if depth == 0:
                expr = raw_cmd[i+2:j-1]
                result.append(eval_expr(expr))
                i = j
            else:
                result.append('#[')
                i += 2
        else:
            result.append(raw_cmd[i])
            i += 1

    return ''.join(result)

def decision(first, mode, second):
    try:
        if mode == "==":
            if first == second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == ">":
            if first > second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == "<":
            if first < second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == ">=":
            if first >= second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == "<=":
            if first <= second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == "!=":
            if first != second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == "is":
            if first is second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        elif mode == "in":
            if first in second:
                return True if not var.get("back") == True else False
            else:
                return False if not var.get("back") == True else True
        else:
            error(["if", repr(first), mode, repr(second)], "无效的比较模式", 2)
    except TypeError:
        error(["if", repr(first), mode, repr(second)], "无法比较不同类型的值", "arg")

def module():
    for root, dirs, files in os.walk('./module'):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code = f.read()

                before = set([k for k, v in globals().items() if callable(v)])

                try:
                    exec(code, globals())
                except Exception as e:
                    error([f"{file}"], f"加载模块时遇到错误: {e}")

                after = set([k for k, v in globals().items() if callable(v)])
                new_funcs = after - before

                for func_name in new_funcs:
                    obj = globals()[func_name]
                    if callable(obj) and not isinstance(obj, type):
                        var["call"].append(func_name)

def error(cmd=None, info=None, position=None):
    if not (cmd is None or cmd == ""):
        cmd = [str(item) for item in cmd]
        print("\033[91m+ " + f"{' '.join(cmd)}")

    if position is None or position == "":
        pass
    elif position == 0:
        print("+ " + "^" * len(cmd[0]))
    elif type(position) is int:
        cmd = [str(item) for item in cmd]
        print("+ " + " " * len(' '.join(cmd[:position])) + (' ' if cmd[:position-1][:0] != ' ' else '') + "^" * len(cmd[position]))
    elif position == "all":
        cmd = [str(item) for item in cmd]
        print("+ " + "^" * len(' '.join(cmd)))
    elif position == "command":
        print("+ " + "^" * len(cmd[0]))
    elif position == "arg":
        cmd = [str(item) for item in cmd]
        print("+ " + " " * len(cmd[0]) + ' ' + "^" * len(' '.join(cmd[1:])))

    if not (cmd is None or cmd == ""):
        print("+")

    if not (info is None or info == ""):
        print("\033[93m- " + info)

    print("\033[0m")

def pwd():
    return os.getcwd()

def main(cmd):
    global var

    cmd = preprocess_command(cmd)
    cmd = cmd.split()
    cmd = parse_value(cmd)

    if not cmd:
        return

    elif cmd[0].startswith(';'):
        return

    elif cmd[0] in var["call"]:
        if len(cmd) > 1:
            var[cmd[0]] = cmd[1:]
        else:
            var[cmd[0]] = ""

        var["rcx"] = cmd[0]

    elif cmd[0] == "exit":
        var["rcx"] = "exit"

    elif cmd[0] == "mass":
        error(cmd, "MASS出现毁灭性错误: 作者放假了", "all")

    elif cmd[0] == "code":
        var["code"] = []
        while True:
            code = input("Code> ")
            if code == "done":
                break
            var["code"].append(code)

    elif cmd[0] == "mov":
        if len(cmd) >= 3:
            mov(cmd[1], cmd[2])
        else:
            error(cmd, "\"mov\" 需要至少 2 个参数", "arg")

    elif cmd[0] == "list":
        list()

    elif cmd[0] == "start":
        var["rcx"] = "start"

    elif cmd[0] == "print":
        var["string"] = " ".join(str(item) for item in cmd[1:])
        var["rcx"] = "write"

    elif cmd[0] == "python":
        if len(cmd) == 1:
            var["string"] = "\n".join(var["code"])
        else:
            var["string"] = " ".join(cmd[1:])

        var["rcx"] = "python"

    elif cmd[0] == "clear":
        var["rcx"] = "clear"

    elif cmd[0] == "init":
        var=init()

    elif cmd[0] == "input":
        if len(cmd) >= 2:
            var["string"] = " ".join(cmd[1:])
        else:
            var["string"] = ""

        var["rcx"] = "read"

    elif cmd[0] == "del":
        var["string"] = cmd[1]
        var["rcx"] = "delete"

    elif cmd[0] == "loop":
        if len(cmd) >= 2:
            if len(cmd) >= 3 and cmd[2] == "if":
                if len(cmd) >= 6:
                    if (len(cmd) >= 7) and (cmd[6] == "back"):
                        var["back"] = True
                    else:
                        try:
                            del var["back"]
                        except:
                            pass

                    ret = decision(cmd[3], cmd[4], cmd[5])
                    if ret:
                        if cmd[1] == 0:
                            while True:
                                for code in var["code"]:
                                    main(code)
                                    status()

                        else:
                            for _ in range(cmd[1]):
                                for code in var["code"]:
                                    main(code)
                                    status()

            else:
                var["times"] = int(cmd[1])
                var["rcx"] = "loop"

        else:
            cmd.append("   ")
            error(cmd, "\"loop\" 需要至少 1 个参数", "arg")

    elif cmd[0] == "call":
        if len(cmd) == 2:
            var["call"].append(cmd[1])
        else:
            if not var["call"] == []:
                print("\x1b[36m已注册函数列表:\033[0m")
                for idx, func in enumerate(var["call"], 1):
                    print(f"  \033[90m{idx:2d}.\033[0m \033[92m{func}\033[0m")
            else:
                print("\x1b[36m没有注册任何函数\033[0m")

    elif cmd[0] == "uncall":
        if len(cmd) == 2:
            try:
                var["call"].remove(cmd[1])
            except ValueError:
                error(["call", f"{cmd[1]}"], f"函数 \"{cmd[1]}\" 未注册", 1)
        else:
            cmd.append("   ")
            error(cmd, "\"uncall\" 需要 1 个参数", "arg")

    elif cmd[0] == "calc":
        if len(cmd) >= 2:
            expression = " ".join(str(x) for x in cmd[1:])
            var["string"] = expression
            var["rcx"]    = "calc"

    elif cmd[0] == "if":
        if len(cmd) >= 4:
            var["first"]  = cmd[1]
            var["mode"]   = cmd[2]
            var["second"] = cmd[3]
            var["rcx"]    = "decision"
            if (len(cmd) >= 5) and (cmd[4] == "back"):
                var["back"] = True
            else:
                try:
                    del var["back"]
                except:
                    pass

        else:
            cmd.append("   ")
            error(cmd, "\"if\" 需要至少 3 个参数", "arg")

    elif cmd[0] == "random":
        if len(cmd) == 3:
            var["first"]  = cmd[1]
            var["second"] = cmd[2]
            var["rcx"]    = "random"
        else:
            cmd.append("   ")
            error(cmd, "\"random\" 需要 2 个参数", "arg")

    elif cmd[0] == "sleep":
        if len(cmd) == 2:
            var["int"] = cmd[1]
            var["rcx"] = "sleep"
        else:
            error(cmd, "\"sleep\" 需要 1 个整数或浮点数", "arg")

    elif cmd[0] == "pwd":
        var["rcx"] = "pwd"

    elif cmd[0] == "cd":
        if len(cmd) == 2:
            var["string"] = cmd[1]
            var["rcx"]    = "chdir"
        else:
            cmd.append("   ")
            error(cmd, "\"cd\" 需要 1 个目录", "arg")

    elif cmd[0] == "rm":
        if len(cmd) == 2:
            var["string"] = cmd[1]
            var["rcx"]    = "remove"
        else:
            cmd.append("   ")
            error(cmd, "\"rm\" 需要 1 个文件或目录", "arg")

    elif cmd[0] == "tee":
        var["rcx"] = "tee"

    elif cmd[0] == "touch":
        if len(cmd) == 2:
            var["string"] = cmd[1]
            var["rcx"]    = "touch"
        else:
            cmd.append("   ")
            error(cmd, "\"touch\" 需要 1 个文件", "arg")

    elif cmd[0] == "mkdir":
        if len(cmd) == 2:
            var["string"] = cmd[1]
            var["rcx"]    = "mkdir"
        else:
            cmd.append("   ")
            error(cmd, "\"mkdir\" 需要 1 个目录", "arg")

    elif cmd[0] == "cat":
        if len(cmd) == 2:
            var["string"] = cmd[1]
            var["rcx"]    = "cat"
        else:
            cmd.append("   ")
            error(cmd, "\"cat\" 需要 1 个文件", "arg")

    elif cmd[0] == "ls":
        var["rcx"] = "ls"

    elif cmd[0] == "for":
        if len(cmd) >= 2:
            if len(cmd) >= 5 and cmd[2] == "if":
                if len(cmd) == 6:
                    if cmd[4] == "back":
                        var["back"] = True
                    else:
                        try:
                            del var["back"]
                        except:
                            pass
                else:
                    try:
                        del var["back"]
                    except:
                        pass
                ret = decision(cmd[3], cmd[4], cmd[5])
                if ret == True:
                    for var["eax"] in cmd[1]:
                        for code in var["code"]:
                            main(code)
                            status()

            else:
                var["string"] = cmd[1]
                var["rcx"] = "for"
        else:
            cmd.append("   ")
            error(cmd, "\"for\" 只需要 1 个参数", "arg")

    elif cmd[0] == "sort":
        if len(cmd) >= 2:
            var["string"] = cmd[1]
            var["rcx"]    = "sort"
        else:
            cmd.append("   ")
            error(cmd, "\"sort\" 需要 1 个对象", "arg")

    elif cmd[0] == "split":
        if len(cmd) >= 2:
            var["string"] = cmd[1]
            var["rcx"]    = "split"
        else:
            cmd.append("   ")
            error(cmd, "\"split\" 需要 1 个字符串", "arg")

    elif cmd[0] == "join":
        if len(cmd) >= 2:
            var["string"] = cmd[1]
            var["rcx"]    = "join"
        else:
            cmd.append("   ")
            error(cmd, "\"join\" 需要 1 个对象", "arg")

    elif cmd[0] == "len":
        if len(cmd) >= 2:
            var["string"] = cmd[1]
            var["rcx"]    = "len"
        else:
            cmd.append("   ")
            error(cmd, "\"len\" 需要 1 个字符串", "arg")

    else:
        error(cmd, "未找到此指令", "command")

def status():
    global var
    if var["rcx"] == None:
        return

    elif var["rcx"] == "exit":
        exit(0)

    elif var["rcx"] == "start":
        for code in var["code"]:
            main(code)
            status()

    elif var["rcx"] == "write":
        if var.get("string"):
            print(f"{var.get('string', '')}")

    elif var["rcx"] == "python":
        if var.get("string"):
            if type(var["string"]) == list:
                for code in var["string"]:
                    exec(code, globals())
            else:
                exec(var["string"], globals())

    elif var["rcx"] == "clear":
        os.system('cls')

    elif var["rcx"] == "read":
        if var.get("string"):
            user_input = input(var["string"])
            var["input"] = user_input

    elif var["rcx"] == "delete":
        if var.get("string"):
            delete(var["string"])

    elif var["rcx"] == "loop":
        times = var["times"]
        if times == 0:
            while True:
                for code in var["code"]:
                    main(code)
                    status()

        for _ in range(int(times)):
            for code in var["code"]:
                main(code)
                status()

    elif var["rcx"] == "calc":
        if var.get("string"):
            try:
                expression = var["string"]
                result = eval(expression)
            except Exception as e:
                error([f"{expression}", ""], f"计算错误: {e}", "all")
                result = None

            var["eax"] = result

    elif var["rcx"] == "decision":
        if var.get("first"):
            if var.get("mode"):
                if var.get("second"):
                    ret = decision(var["first"], var["mode"], var["second"])
                    if ret:
                        for code in var["code"]:
                            main(code)
                            status()
                else:
                    error(["if", var.get("first"), var.get("mode"), "   "], "需要第二个比较值", 3)
            else:
                error(["if", var.get("first"), "   "], "需要比较模式", 2)
        else:
            error(["if", "   "], "需要两个比较值", 1)

    elif var["rcx"] == "random":
        if var.get("first") and var.get("second"):
            var["random"] = random.randint(int(var["first"]), int(var["second"]))
        else:
            error(["random", "   "], "需要一个范围", 1)

    elif var["rcx"] == "sleep":
        try:
            time.sleep(var["int"])
        except TypeError:
            error(["sleep", repr(f"{var["int"]}")], "需要整数或浮点数", "arg")
        except Exception as e:
            error(["sleep", str(int)], f"错误: {e}", "arg")

    elif var["rcx"] == "pwd":
        print(f"\x1b[36m{pwd()}\033[0m")

    elif var["rcx"] == "chdir":
            if var.get("string"):
                try:
                    os.chdir(var["string"])
                except FileNotFoundError:
                    error(["cd", f"{var["string"]}"], "目录不存在", "arg")
                except PermissionError:
                    error(["cd", f"{var["string"]}"], "权限不足", "arg")
                except NotADirectoryError:
                    error(["cd", f"{var["string"]}"], "期望目录", "arg")
                except Exception as e:
                    error(["cd", f"{var["string"]}"], f"错误: {e}", "arg")
            else:
                error(["cd", "   "], "需要一个目录", "arg")

    elif var["rcx"] == "remove":
        if var.get("string"):
            try:
                if os.path.isfile(var["string"]):
                    os.remove(var["string"])
                else:
                    os.rmdir((var["string"]))
            except FileNotFoundError:
                error(["rm", f"{var["string"]}"], "文件或目录不存在", "arg")
            except PermissionError:
                error(["rm", f"{var["string"]}"], "权限不足", "arg")
            except Exception as e:
                error(["rm", f"{var["string"]}"], f"错误: {e}", "arg")
        else:
            error(["rm", "   "], "需要一个文件或目录", "arg")

    elif var["rcx"] == "tee":
        if var.get("string"):
            try:
                with open(var["string"], "w", encoding="utf-8") as f:
                    for line in var["code"]:
                        f.write(line + "\n")

            except FileNotFoundError:
                error(["tee", f"{var["string"]}"], "文件不存在", "arg")
            except PermissionError:
                error(["tee", f"{var["string"]}"], "权限不足", "arg")
            except Exception as e:
                error(["tee", f"{var["string"]}"], f"错误: {e}", "arg")
        else:
            error(["tee", "   "], "需要一个文件", "arg")

    elif var["rcx"] == "touch":
        if var.get("string"):
            try:
                with open(var["string"], "w", encoding="utf-8") as f:
                    pass
            except PermissionError:
                error(["touch", f"{var["string"]}"], "权限不足", "arg")
            except Exception as e:
                error(["touch", f"{var["string"]}"], f"错误: {e}", "arg")
        else:
            error(["touch", "   "], "需要一个文件", "arg")

    elif var["rcx"] == "mkdir":
        if var.get("string"):
            try:
                os.mkdir(var["string"])
            except FileExistsError:
                error(["mkdir", var["string"]], "目录已存在", "arg")
            except PermissionError:
                error(["mkdir", f"{var["string"]}"], "权限不足", "arg")
            except Exception as e:
                error(["mkdir", f"{var["string"]}"], f"错误: {e}", "arg")
        else:
            error(["mkdir", "   "], "需要一个目录", "arg")

    elif var["rcx"] == "cat":
        if var.get("string"):
            try:
                with open(var["string"], "r", encoding="utf-8") as f:
                    print(f.read())

            except FileNotFoundError:
                error(["cat", f"{var["string"]}"], "文件不存在", "arg")
            except IsADirectoryError:
                error(["cat", f"{var["string"]}"], "期望文件", "arg")
            except PermissionError:
                error(["cat", f"{var["string"]}"], "权限不足", "arg")
            except Exception as e:
                error(["cat", f"{var["string"]}"], f"错误: {e}", "arg")
        else:
            error(["cat", "   "], "需要一个文件", "arg")

    elif var["rcx"] == "ls":
        for f in os.listdir():
            print(f, end='   ')
        print()

    elif var["rcx"] == "for":
        if var.get("string"):
            for var["eax"] in var["string"]:
                for code in var["code"]:
                    main(code)
                    status()
        else:
            error(["for", "   "], "需要迭代对象", "arg")

    elif var["rcx"] == "sort":
        if var.get("string"):
            try:
                var["eax"] = sorted(var["string"])
            except TypeError:
                error(["sort", f"{var['string']}"], "无法排序", "arg")
        else:
            error(["sort", "   "], "需要 1 个对象", "arg")

    elif var["rcx"] == "split":
        if var.get("string"):
            var["eax"] = var["string"].split()
        else:
            error(["split", "   "], "需要 1 个字符串", "arg")

    elif var["rcx"] == "join":
        if var.get("string"):
            var["eax"] = ' '.join(var["string"])
        else:
            error(["join", "   "], "需要 1 个对象", "arg")

    elif var["rcx"] == "len":
        if var.get("string"):
            var["eax"] = len(var["string"])
        else:
            error(["len", "   "], "需要 1 个字符串", "arg")

    elif var["rcx"] in var["call"]:
        if var.get(var["rcx"]):
            try:
                exec(f"{var['rcx']}(var[\"{var['rcx']}\"])")
            except TypeError:
                error([var['rcx']] + var[var["rcx"]], f"不需要参数", "arg")
            except IndexError:
                error([var['rcx']] + var[var["rcx"]] + ["   "], f"参数过少", "arg")
            except ValueError as e:
                error([var['rcx']], f"值错误: {e}")
            except KeyError as e:
                error([var['rcx']], f"无效的键: {e}")
            except RuntimeError as e:
                error([var['rcx']], f"迭代时出现错误: {e}")
            except Exception as e:
                error([var['rcx']], f"运行失败: {e}")
            finally:
                del var[var["rcx"]]
            try:
                del var[var["rcx"]]
            except:
                pass

        else:
            try:
                exec(f"{var['rcx']}()")
            except TypeError:
                error([var['rcx']] + ["   "], f"参数过少", "arg")
            except ValueError as e:
                error([var['rcx']], f"值错误: {e}")
            except KeyError as e:
                error([var['rcx']], f"无效的键: {e}")
            except RuntimeError as e:
                error([var['rcx']], f"迭代时出现错误: {e}")
            except Exception as e:
                error([var['rcx']], f"运行失败: {e}")
    else:
        error(["rcx", "=", var["rcx"]], "RCX状态错误", 2)

    var["pwd"] = pwd()
    var["rcx"] = None

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        args = sys.argv
        if args[1] == "--version" or args[1] == "-v":
            ver = random.uniform(1.00, 9.99)
            print(f"Medern Assembly\n版本: {ver:.2f}")

        elif args[1] == "-c":
            if len(args) >= 3:
                var=init()
                main(' '.join(args[2:]))
                status()
            else:
                args.append("   ")
                error(args, "\"-c\" 需要一个命令", 2)

        elif os.path.exists(args[1]):
            var=init()
            with open(args[1], "r", encoding="utf-8") as f:
                for code in f.read().splitlines():
                    main(code)
                    status()
        else:
            error(args, f"没有这个参数或文件: \"{" ".join(args[1:])}\"", 1)
        exit(0)

    var=init()
    module()
    while True:
        try:
            cmd = input(var["ps"] if var.get("ps") else "/> ")
            main(cmd)
            status()
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
        except TypeError as e:
            error(cmd.split(), f"类型错误: {e}", "all")
        except ValueError as e:
            error(cmd.split(), f"值错误: {e}", "all")
        except KeyError as e :
            error(cmd.split(), f"无效的键: {e}", "all")
        except RuntimeError as e:
            error(cmd.split(), f"迭代时出现错误: {e}", "all")
        except Exception as e:
            error(cmd.split(), f"错误: {e}", "all")
        finally:
            var["rcx"] = None

# Modern Assembly (MASS)
#   寄存器:
#     ps     - 提示符寄存器   (存储提示符)
#     rcx    - 控制寄存器     (存储要运行的CPU指令)
#     code   - 代码寄存器     (存储代码行)
#     string - 通用寄存器     (存储字符串)
#     times  - 循环次数寄存器 (存储循环次数)
#     input  - 输入寄存器     (存储用户输入)
#     eax    - 计算结果寄存器 (存储表达式计算结果)
#     first  - 参数寄存器     (存储第一个参数)
#     second - 参数寄存器     (存储第二个参数)
#     mode   - 模式寄存器     (存储模式)
#     random - 随机数寄存器   (储存random命名输出的随机数)
#     int    - 数字寄存器     (存储整数&浮点数)
#     back   - 反转寄存器     (存储if是否反转结果的选项)
#     pwd    - 路径寄存器     (存储当前的工作路径)
#
#   指令:
#     mov <寄存器名> <值> - 将值赋给寄存器
#     code                - 进入代码输入模式，输入done结束
#     list                - 列出所有寄存器及其值
#     start               - 执行代码寄存器中的代码
#     print <字符串>      - 输出字符串到控制台
#     python <代码>       - 执行Python代码，若无参数则执行code录制的代码
#     clear               - 清屏
#     init                - 重置所有寄存器
#     input <提示符>      - 显示提示符并读取用户输入，存储在input寄存器中
#     del <寄存器名>      - 删除指定寄存器
#     loop <次数>         - 循环执行code录制的代码指定次数(0为无限)
#          <次数> if <if> - 条件循环
#     call <函数名>       - 注册函数
#     uncall <函数名>     - 注销函数
#     calc <表达式>       - 计算表达式并将结果存储在eax寄存器中
#     if <值> <模式> <值> - 比较，如果为True则执行code录制的代码(尾部接back反转结果)
#     random <int> <int>  - 生成随机数到random寄存器
#     sleep <int或float> - 等待
#     pwd                 - 列出路径
#     cd <文件夹>         - 切换目录
#     ls                  - 列出文件/文件夹
#     rm                  - 删除文件/文件夹
#     touch               - 创建文件
#     tee                 - 写入code录制的内容到文件
#     mkdir               - 创建文件夹
#     cat                 - 查看文件
#     for <对象>          - 遍历对象到eax
#         <对象> if <if>  - 条件遍历
#     sort <对象>         - 对对象进行排序并存储在eax寄存器中
#     split <字符串>      - 将字符串按空格拆分为列表并存储在eax寄存器中
#     join <对象>         - 将对象按空格连接为字符串并存储在eax寄存器中
#     len <字符串>        - 获取字符串长度并存储在eax寄存器中
#     exit                - 退出解释器
#
#   命令行参数:
#     <文件>    - 解释运行文件 (太垃圾了不建议，语句全部用不了，因为没法用code)
#     --version - 打印版本
#
#   手动操作:
#     print:
#       mov string <字符串>
#       mov rcx write
#     input:
#       mov string <提示符>
#       mov rcx read
#     del:
#       mov string <寄存器名>
#       mov rcx delete
#     loop:
#       mov times <次数>
#       mov rcx loop
#     start:
#       code
#       mov rcx start
#     python:
#       code
#       mov rcx python
#     clear:
#       mov rcx clear
#     reinit:
#       mov rcx reinit
#     calc:
#       mov string <表达式>
#       mov rcx calc
#     if:
#       code
#       mov first <值>
#       mov mode <模式>
#       mov second <值>
#       mov rcx decision
#     random:
#       mov first <值>
#       mov second <值>
#       mov rcx random
#     pwd:
#       mov rcx pwd
#     cd:
#       mov string 目录
#       mov rcx chdir
#     ls:
#       mov rcx ls
#     rm:
#       mov string <文件/文件夹>
#       mov rcx remove
#     touch:
#       mov string <文件>
#       mov rcx touch
#     mkdir:
#       mov string <文件夹>
#       mov rcx mkdir
#     cat:
#       mov string <文件>
#       mov rcx cat
#     tee:
#       code
#       mov rcx tee
#     for:
#       mov string <对象>
#       mov rcx for
#     sleep:
#       mov int <整数或浮点数>
#       mov rcx sleep
#     sort:
#       mov string <对象>
#       mov rcx sort
#     split:
#       mov string <字符串>
#       mov rcx split
#     join:
#       mov string <对象>
#       mov rcx join
#     len:
#       mov string <字符串>
#       mov rcx len
#     exit:
#       mov rcx exit
#
#   语法:
#     #[变量]  - 使用变量内容
#     ; <内容> - 注释(需要在一行的开头)
#
#   模块教程:
#     将自定义函数写入module目录下的.py文件中，函数名为调用名
#     函数可接受一个参数
#     如def myfunc(args): ...
#     如果输入myfunc a b
#     则args为['a', 'b']
#

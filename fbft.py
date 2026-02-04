import os
import shutil

global choose, files, dirs
choose = 0
files = []
dirs = []

def fbft():
    global choose, files, dirs
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        pwd = os.getcwd()
        print(f"{pwd}")
        print()
        print()
        print()

        files = []
        dirs = []

        dirfile = os.listdir('.')
        n = 0
        dirfile.append("..")

        if choose >= len(dirfile):
            choose = 0
        elif choose < 0:
            choose = len(dirfile) - 1

        for f in dirfile:
            if os.path.isfile(f):
                files.append(f)
            elif os.path.isdir(f):
                dirs.append(f + "/")

        files.sort()
        dirs.sort()

        dirfile = dirs + files
        for f in dirfile:
            if n == choose:
                print(f"> {f}")
            else:
                print(f"  {f}")

            n += 1

        print()
        print(message if 'message' in locals() else "")
        print()

        try:
            del message
        except:
            pass

        key = input(":")

        if key:
            if key == "q" or key == "quit" or key == "exit":
                break

            elif key == 'w':
                choose -= 1

            elif key == 's':
                choose += 1

            elif key == 'W':
                choose -= 3

            elif key == 'S':
                choose += 3

            elif key == 'd':
                if os.path.isdir(dirfile[choose]):
                    os.chdir(dirfile[choose])
                else:
                    message = "所选项不是目录"

            elif key == 'rm':
                cmd = input(f"确认删除\"{dirfile[choose]}\"? (y/n): ")
                if cmd == "y":
                    try:
                        if os.path.isdir(dirfile[choose]):
                            shutil.rmtree(dirfile[choose])
                        else:
                            os.remove(dirfile[choose])
                    except Exception as e:
                        message = f"错误: {str(e)}"

            elif key == 'cp':
                cmd = input("输入目标路径: ")
                try:
                    if os.path.isdir(dirfile[choose]):
                        shutil.copytree(dirfile[choose], cmd)
                    else:
                        shutil.copy2(dirfile[choose], cmd)
                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == 'mv':
                cmd = input("输入目标路径: ")
                try:
                    shutil.move(dirfile[choose], cmd)
                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == 'rename':
                cmd = input("输入新名称: ")
                try:
                    os.rename(dirfile[choose], cmd)
                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == 'cat':
                try:
                    if os.path.isdir(dirfile[choose]):
                        message = "所选项是目录"
                    else:
                        with open(dirfile[choose], 'r', encoding='utf-8') as f:
                            content = f.read()
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(content)
                            input("\n按回车键返回...")

                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == "mkfile":
                cmd = input("输入文件名: ")
                try:
                    with open(cmd, 'w', encoding='utf-8') as f:
                        pass
                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == "mkdir":
                cmd = input("输入目录名: ")
                try:
                    os.mkdir(cmd)
                except Exception as e:
                    message = f"错误: {str(e)}"

            elif key == 'info':
                raw_path = dirfile[choose].rstrip('/\\')

                if not os.path.exists(raw_path):
                    message = "文件不存在"
                else:
                    try:
                        st = os.stat(raw_path)

                        info = [
                            f"-----{raw_path}-----",
                            f"类型: {'目录' if os.path.isdir(raw_path) else '文件'}",
                            f"大小: {st.st_size:,} 字节",
                            f"权限: {oct(st.st_mode)[-3:]}"
                        ]

                        print("\n" + "\n".join(info))
                        input("\n按回车继续...")

                    except Exception as e:
                        message = f"错误: {e}"

            elif key == "help":
                print("可用命令:")
                print("  w/s    - 上下移动光标")
                print("  W/S    - 快速上下移动光标")
                print("  d      - 打开目录或文件")
                print("  rm     - 删除当前选中项")
                print("  cp     - 复制当前选中项")
                print("  mv     - 移动当前选中项")
                print("  rename - 重命名当前选中项")
                print("  cat    - 查看当前选中文件内容")
                print("  mkfile - 创建新文件")
                print("  mkdir  - 创建新目录")
                print("  info   - 显示当前选中项信息")
                print("  help   - 显示帮助信息")
                input("\n按回车键返回...")

#if __name__ == "__main__":
#    fbft()

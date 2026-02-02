import os

def tictactoe():
    print("欢迎来到井字棋游戏")
    input("按回车键开始游戏...")

    json = {"1": " ", "2": " ", "3": " ", "4": " ", "5": " ", "6": " ", "7":" ", "8": " ", "9": " "}
    player = "X"
    occupy = False
    invalid = False
    change = False

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
     {json['1']} | {json['2']} | {json['3']}
    ---+---+---
     {json['4']} | {json['5']} | {json['6']}
    ---+---+---
     {json['7']} | {json['8']} | {json['9']}
        """)

        if change:
            player = "O" if player == "X" else "X"

        if occupy == True:
            print("该位置已经被占用了~")
            occupy = False

        elif invalid == True:
            print("请输入1-9之间的数字~")
            invalid = False
        else:
            print()
            occupy = False

        print()

        pinput = input(f"\"{player}\"请选择位置 (1-9): ")

        if pinput in json:
            if json[pinput] == " ":
                json[pinput] = player
                invalid = False
                occupy = False
                change = True
            else:
                invalid = False
                occupy = True
                change = False
                continue
        else:
            invalid = True
            occupy = False
            change = False
            continue

        if (json["1"] == json["2"] == json["3"] != " ") or \
           (json["4"] == json["5"] == json["6"] != " ") or \
           (json["7"] == json["8"] == json["9"] != " ") or \
           (json["1"] == json["4"] == json["7"] != " ") or \
           (json["2"] == json["5"] == json["8"] != " ") or \
           (json["3"] == json["6"] == json["9"] != " ") or \
           (json["1"] == json["5"] == json["9"] != " ") or \
           (json["3"] == json["5"] == json["7"] != " "):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"""
     {json['1']} | {json['2']} | {json['3']}
    ---+---+---
     {json['4']} | {json['5']} | {json['6']}
    ---+---+---
     {json['7']} | {json['8']} | {json['9']}
            """)
            print(f"玩家 \"{player}\" 获胜!")
            break

def ttt():
    tictactoe()

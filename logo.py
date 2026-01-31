import turtle
import time

t = None

def logo():
    global t
    if t is None:
        t = turtle.Turtle()
        t.speed(1)
    try:
        t.forward(0)
    except:
        turtle.TurtleScreen._RUNNING = True
        t = turtle.Turtle()
        t.speed(1)

def fd(args):
    global t
    logo()
    t.forward(args[0])
    print(f"前进 {args[0]}")
    time.sleep(0.01)

def rt(args):
    global t
    logo()
    t.right(args[0])
    print(f"右转 {args[0]}°")
    time.sleep(0.01)

def lt(args):
    global t
    logo()
    t.left(args[0])
    print(f"左转 {args[0]}°")
    time.sleep(0.01)

def pu():
    global t
    logo()
    t.penup()
    print("提笔")
    time.sleep(0.01)

def pd():
    global t
    logo()
    t.pendown()
    print("落笔")
    time.sleep(0.01)

def cs():
    global t
    if t:
        t.clear()
    t = None
    print("清屏")
    time.sleep(0.01)

def setw(args):
    global t
    logo()
    t.width(args[0])
    print(f"粗细 {args[0]}")
    time.sleep(0.01)

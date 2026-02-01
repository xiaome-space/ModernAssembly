# ModernAssembly
## Chinese

ModernAssembly 是我用 Python 创建的一种伪汇编语言 （不是真正的汇编！！！）

**推荐安装Rich库 ```pip install rich```**

它内置了25个指令

还有非常简单的module功能

在module目录创建一个可以是任意名称的.py文件

只要在这个文件中写几个函数就可以使用了

参数会成一个列表传入

例如:
```Python
def hello():
    print("Hello,My MASS Module!")

def echo(args):
    print(' '.join(args))
```
在MASS中:
```MASS
/> hello
Hello,My MASS Module!
/> echo Hi
Hi
```

## English

ModernAssembly is a pseudo-assembly I created using Python (Not True Assembly!!!)

It has 25 built-in commands

There is also a very simple module feature

In the module directory, create a .py file with any name

You just need to write a few functions in this file to use it

The parameters will be passed in as a list

For example:
```Python
def hello():
    print("Hello, My MASS Module!")

def echo(args):
    print(' '.join(args))
```
In MASS:
```MASS
/> hello
Hello, My MASS Module!
/> echo Hi
Hi
```
(Use Bing Translate for English)

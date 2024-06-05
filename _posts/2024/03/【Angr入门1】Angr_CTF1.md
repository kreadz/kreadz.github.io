# AngrCTF入门

本文基于一个GitHub上关于Angr在CTF上应用的题库，具体的地址为：

```
https://github.com/ZERO-A-ONE/AngrCTF_FITM
```

本文所使用Ubuntu环境皆为20.04 LTS 版本
![](https://img-blog.csdnimg.cn/direct/1d14124d73bb47bb8d7ee69647483b13.png)


## angr安装

参考：https://github.com/Hustcw/Angr_Tutorial_For_CTF

此处安装的pypy3.6，是一种运行速度更快的python解释器。

![](https://files.mdnice.com/user/53147/87c65393-34e2-4c9c-820e-818751bb0429.png)


## 简介

### 符号执行

​	符号执行就是在运行程序时，用符号来替代真实值。符号执行相较于真实值执行的优点在于，当使用真实值执行程序时，我们能够遍历的程序路径只有一条, 而使用符号进行执行时，由于符号是可变的，我们就可以利用这一特性，尽可能的将程序的每一条路径遍历，这样的话，必定存在至少一条能够输出正确结果的分支, 每一条分支的结果都可以表示为一个离散关系式,使用约束求解引擎即可分析出正确结果。

### Angr

​	Angr是加州大学圣芭芭拉分校基于Python设计的工具，它结合了静态分析技术与动态分析技术是当前符号化执行领域较为先进的工具，其挖掘漏洞效果好，在许多竞赛中表现卓越。Angr总的来说是一个多架构的二进制分析平台，具备对二进制文件的动态符号执行能力和多种静态分析能力。在逆向中，一般使用的其动态符号执行解出Flag，但其实Angr还在诸多领域存在应用，比如对程序脆弱性的分析中。

## 00_angr_find

首先检查一下文件：

```bash
syc@ubuntu:~/Desktop/TEMP$ checksec '/home/syc/Desktop/TEMP/00_angr_find' 
[*] '/home/syc/Desktop/TEMP/00_angr_find'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

用IDA打开查看一下伪C代码：

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  signed int i; // [esp+1Ch] [ebp-1Ch]
  char s1[9]; // [esp+23h] [ebp-15h]
  unsigned int v6; // [esp+2Ch] [ebp-Ch]

  v6 = __readgsdword(0x14u);
  printf("Enter the password: ");
  __isoc99_scanf("%8s", s1);
  for ( i = 0; i <= 7; ++i )
    s1[i] = complex_function(s1[i], i);
  if ( !strcmp(s1, "JACEJGCS") )
    puts("Good Job.");
  else
    puts("Try again.");
  return 0;
}
```

这里可以发现关键的函数complex_function对我们输入的字符串处理后，与字符串"JACEJGCS"进行了比较，我们可以进入查看该函数：

```c
int __cdecl complex_function(signed int a1, int a2)
{
  if ( a1 <= 64 || a1 > 90 )
  {
    puts("Try again.");
    exit(1);
  }
  return (3 * a2 + a1 - 65) % 26 + 65;
}
```

很标准的可以使用Angr进行解题的题型，也可以使用很常规的爆破手段去解题：

```python
str1 = "JACEJGCS"
flag = ""
def complex_function(a1,a2):
    return (3 * a2 + a1 - 65) % 26 + 65
if __name__ == "__main__":
    for i in range(len(str1)):
        for j in range(64,90):      
            if ord(str1[i]) == complex_function(j,i):
                flag += chr(j)
                break            
    print(flag)
```

这题基础题主要是熟悉一下Angr的基本使用步骤,一般来说使用Angr的步骤可以分为：

- 创建 project
- 设置 state
- 新建符号量 : BVS (bitvector symbolic ) 或 BVV (bitvector value)
- 把符号量设置到内存或者其他地方
- 设置 Simulation Managers ， 进行路径探索的对象
- 运行，探索满足路径需要的值
- 约束求解，获取执行结果

先放一下解这题的脚本，然后逐以解释：

```python
import angr
import sys
def Go():
    path_to_binary = "./00_angr_find"
    project = angr.Project(path_to_binary, auto_load_libs=False)
    initial_state = project.factory.entry_state()
    simulation = project.factory.simgr(initial_state)

    print_good_address = 0x8048678  
    simulation.explore(find=print_good_address)
  
    if simulation.found:
        solution_state = simulation.found[0]
        solution = solution_state.posix.dumps(sys.stdin.fileno())
        print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
    else:
        raise Exception('Could not find the solution')
if __name__ == "__main__":
    Go()
```

查看运行一下看看：

![](https://note-book.obs.cn-east-3.myhuaweicloud.com/Angr_CTF/%E4%B8%80/1596338176%281%29.jpg)

得到flag：JXWVXRKX，和我们之前用传统方法得到答案一致，接下来开始分析一个简单的angr脚本构成

### 创建Project

```python
path_to_binary = "./00_angr_find" 
project = angr.Project(path_to_binary, auto_load_libs=False)
```

使用 angr的首要步骤就是创建Project加载二进制文件。angr的二进制装载组件是CLE，它负责装载二进制对象（以及它依赖的任何库）和把这个对象以易于操作的方式交给angr的其他组件。angr将这些包含在Project类中。一个Project类是代表了你的二进制文件的实体。你与angr的大部分操作都会经过它

auto_load_libs 设置是否自动载入依赖的库，在基础题目中我们一般不需要分析引入的库文件，这里设置为否

> - 如果`auto_load_libs`是`True`（默认值），真正的库函数会被执行。这可能正是也可能不是你想要的，取决于具体的函数。比如说一些libc的函数分析起来过于复杂并且很有可能引起path对其的尝试执行过程中的state数量的爆炸增长
> - 如果`auto_load_libs`是`False`，且外部函数是无法找到的，并且Project会将它们引用到一个通用的叫做`ReturnUnconstrained`的`SimProcedure`上去，它就像它的名字所说的那样：它返回一个不受约束的值

### 设置 state

```python
initial_state = project.factory.entry_state()
```

state代表程序的一个实例镜像，模拟执行某个时刻的状态，就类似于**快照**。保存运行状态的上下文信息，如内存/寄存器等,我们这里使用`project.factory.entry_state()`告诉符号执行引擎从程序的入口点开始符号执行，除了使用`.entry_state()` 创建 state 对象, 我们还可以根据需要使用其他构造函数创建 state

### 设置 Simulation Managers

```python
simulation = project.factory.simgr(initial_state)
```

Project  对象仅表示程序一开始的样子，而在执行时，我们实际上是对SimState对象进行操作，它代表程序的一个实例镜像，模拟执行某个时刻的状态

`SimState`   对象包含程序运行时信息，如内存/寄存器/文件系统数据等。SM（Simulation Managers）是angr中最重要的控制接口，它使你能够同时控制一组状态(state)的符号执行，应用搜索策略来探索程序的状态空间。

### 运行，探索满足路径需要的值

```python
print_good_address = 0x8048678  
simulation.explore(find=print_good_address)
```

符号执行最普遍的操作是找到能够到达某个地址的状态，同时丢弃其他不能到达这个地址的状态。SM为使用这种执行模式提供了`.explore()`方法

当使用`find`参数启动`.explore()`方法时，程序将会一直执行，直到发现了一个和`find`参数指定的条件相匹配的状态。`find`参数的内容可以是想要执行到的某个地址、或者想要执行到的地址列表、或者一个获取state作为参数并判断这个state是否满足某些条件的函数。当`active`stash中的任意状态和`find`中的条件匹配的时候，它们就会被放到`found stash`中，执行随即停止。之后你可以探索找到的状态，或者决定丢弃它，转而探索其它状态。

这里0x8048678的地址值是根据IDA打开后我们可以发现是保存导致打印“ Good Job”的块地址的变量

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20200802164840.png)

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802165123.png)

若能输出正确的字符串"Good Job"即代表我们的执行路径是正确的

### 获取执行结果

```python
if simulation.found:
        solution_state = simulation.found[0]  # 获取通过 explore 找到符合条件的状态
        solution = solution_state.posix.dumps(sys.stdin.fileno())
        print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
```

此时相关的状态已经保存在了`simgr`当中，我们可以通过`simgr.found`来访问所有符合条件的分支，这里我们为了解题，就选择第一个符合条件的分支即可

这里解释一下`sys.stdin.fileno()`,在UNIX中，按照惯例，三个文件描述符分别表示标准输入、标准输出和标准错误

```python
>>> import sys
>>> sys.stdin.fileno()
0
>>> sys.stdout.fileno()
1
>>> sys.stderr.fileno()
2
```

所以一般也可以写成：

```python
 solution = solution_state.posix.dumps(0)
```

## 01_angr_avoid

这题主要是引入了`.explore()`方法的另一个参数void，我们可以看看这个方法的原型

```python
def explore(self, stash='active', n=None, find=None, avoid=None, find_stash='found', avoid_stash='avoid', cfg=None,um_find=1, **kwargs):
```

和之前提到过的find参数类是，你还可以按照和`find`相同的格式设置另一个参数——`avoid`。当一个状态和`avoid`中的条件匹配时，它就会被放进`avoided stash`中，之后继续执行。

首先检查一下文件：

```bash
syc@ubuntu:~/Desktop/TEMP$ checksec '/home/syc/Desktop/TEMP/01_angr_avoid' 
[*] '/home/syc/Desktop/TEMP/01_angr_avoid'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

这题用IDA打开想F5的话，会提示main函数过大，虽然其实也不用F5，但是我还是想看看反汇编出来的main函数，这里我使用的是retdec（https://github.com/avast/retdec）

下载下来后，运行这段命令执行反汇编操作：

```powershell
PS C:\Users\syc> python C:\Users\syc\Downloads\retdec-v4.0-windows-64b\retdec\bin\retdec-decompiler.py D:\build\AngrCTF_FITM\01_angr_avoid\01_angr_avoid
```

运行需要一点时间，稍等一会儿就可以在根目录获得C语言的源代码

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802212543.png)

查看一下获得的源代码的main函数

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802212828.png)

这题就是为了angr而生的题目，我们只需要让执行流只进入maybe_good函数，而避免进入avoid_me函数即可，现在需要拿到这两个函数的地址

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802213325.png)

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802213419.png)

最后编写的EXP：

```python
import angr
import sys
def Go():
    path_to_binary = "./01_angr_avoid" 
    project = angr.Project(path_to_binary, auto_load_libs=False)
    initial_state = project.factory.entry_state()
    simulation = project.factory.simgr(initial_state)

    avoid_me_address =   0x080485A8
    maybe_good_address = 0x080485E0

    simulation.explore(find=maybe_good_address, avoid=avoid_me_address)
  
    if simulation.found:
        solution_state = simulation.found[0]
        solution = solution_state.posix.dumps(sys.stdin.fileno())
        print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
    else:
        raise Exception('Could not find the solution')
if __name__ == "__main__":
    Go()
```

运行获得flag：

![](https://note-book.obs.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200802214124.png)

## 02_angr_find_condition

这一题和之前的题目其实一样的，只不过题目本意是教会我们如何根据程序本身的输出来告诉angr应避免或保留的内容。因为有时候打开二进制文件将看到有很多打印“ Good Job”的块，或“Try Again”的块。每次都记录下这些块的所有起始地址是一个麻烦的的问题，这时候我们可以直接根据打印到stdout的内容告诉angr保留或丢弃状态

先检查一下文件：

```bash
syc@ubuntu:~/Desktop/TEMP$ checksec '/home/syc/Desktop/TEMP/02_angr_find_condition' 
[*] '/home/syc/Desktop/TEMP/02_angr_find_condition'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

用ida打开一下查看一下main函数

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  signed int i; // [esp+18h] [ebp-40h]
  signed int j; // [esp+1Ch] [ebp-3Ch]
  char s1[20]; // [esp+24h] [ebp-34h]
  char s2[4]; // [esp+38h] [ebp-20h]
  int v8; // [esp+3Ch] [ebp-1Ch]
  unsigned int v9; // [esp+4Ch] [ebp-Ch]

  v9 = __readgsdword(0x14u);
  for ( i = 0; i <= 19; ++i )
    s2[i] = 0;
  *(_DWORD *)s2 = 1381128278;
  v8 = 1381320010;
  printf("Enter the password: ");
  __isoc99_scanf("%8s", s1);
  for ( j = 0; j <= 7; ++j )
    s1[j] = complex_function(s1[j], j + 8);
  if ( !strcmp(s1, s2) )
    puts("Good Job.");
  else
    puts("Try again.");
  return 0;
}
```

```c
int __cdecl complex_function(signed int a1, int a2)
{
  if ( a1 <= 64 || a1 > 90 )
  {
    puts("Try again.");
    exit(1);
  }
  return (31 * a2 + a1 - 65) % 26 + 65;
}
```

几乎没变，用之前的脚本改一改也能跑出flag：

```python
str1 = "VXRRJEUR"
flag = ""
def complex_function(a1,a2):
    return (31 * a2 + a1 - 65) % 26 + 65
if __name__ == "__main__":
    for i in range(len(str1)):
        for j in range(64,90):      
            if ord(str1[i]) == complex_function(j,i+8):
                print(i+8)
                flag += chr(j)
                break            
    print(flag)
```

angr的exp：

```python
import angr
import sys
def Go():
    path_to_binary = "./02_angr_find_condition" 
    project = angr.Project(path_to_binary, auto_load_libs=False)
    initial_state = project.factory.entry_state()
    simulation = project.factory.simgr(initial_state)

    def is_successful(state):
        stdout_output = state.posix.dumps(sys.stdout.fileno())
        if b'Good Job.' in stdout_output:
            return True
        else: 
            return False

    def should_abort(state):
        stdout_output = state.posix.dumps(sys.stdout.fileno())
        if b'Try again.' in  stdout_output:
            return True
        else: 
            return False

    simulation.explore(find=is_successful, avoid=should_abort)
  
    if simulation.found:
        solution_state = simulation.found[0]
        solution = solution_state.posix.dumps(sys.stdin.fileno())
        print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
    else:
        raise Exception('Could not find the solution')
    
if __name__ == "__main__":
    Go()
```

重点是分析一下引入的两个新函数，选择其中一个来说一说：

```python
def is_successful(state):
        stdout_output = state.posix.dumps(sys.stdout.fileno())
        if b'Good Job.' in stdout_output:
            return True
        else: 
            return False
```

我们将打印到标准输出的内容放入`stdout_output`变量中。请注意，这不是字符串，而是字节对象，这意味着我们必须使用`b'Good Job.'`而不是仅`"Good Job."`来检查我们是否正确输出了“ Good Job”

引入一个函数来对状态进行检测是为了实现动态的选择想获取的state。回想一下之前我们的`simulation.explore`都是固定写死的具体地址，但我们引入一个函数就可以动态的进行分析获取state

运行一下获得答案：

![](https://note-book.obs.cn-east-3.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200804174207.png)

## 03_angr_simbolic_registers

这题主要是因为angr在处理复杂格式的字符串scanf()输入的时候不是很好，我们可以直接将符号之注入寄存器，也就是主要学会符号化寄存器

首先检查一下文件：

```bash
syc@ubuntu:~/Desktop/TEMP$ checksec 03_angr_symbolic_registers
[*] '/home/syc/Desktop/TEMP/03_angr_symbolic_registers'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

拖入IDA查看一下程序逻辑：

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int v3; // ebx
  int v4; // eax
  int v5; // edx
  int v6; // ST1C_4
  unsigned int v7; // ST14_4
  unsigned int v9; // [esp+8h] [ebp-10h]
  unsigned int v10; // [esp+Ch] [ebp-Ch]

  printf("Enter the password: ");
  v4 = get_user_input();
  v6 = v5;
  v7 = complex_function_1(v4);
  v9 = complex_function_2(v3);
  v10 = complex_function_3(v6);
  if ( v7 || v9 || v10 )
    puts("Try again.");
  else
    puts("Good Job.");
  return 0;
}
```

关键的函数就是需要分析`get_user_input()`和`complex_function()`

```c
int get_user_input()
{
  int v1; // [esp+0h] [ebp-18h]
  int v2; // [esp+4h] [ebp-14h]
  int v3; // [esp+8h] [ebp-10h]
  unsigned int v4; // [esp+Ch] [ebp-Ch]

  v4 = __readgsdword(0x14u);
  __isoc99_scanf("%x %x %x", &v1, &v2, &v3);
  return v1;
}
```

```c
unsigned int __cdecl complex_function_1(int a1)
{
  return (((((((((((((((((((((a1 + 17062705) ^ 0xB168C552) + 647103529) ^ 0x9F14CFD7) - 548738866) ^ 0xF78063EF)
                      - 1352480098) ^ 0x5D1F4C6)
                    - 57802472) ^ 0xB6F70BF8)
                  - 1347645151
                  + 648671421) ^ 0x3D5082FE)
                - 9365053) ^ 0xD0150EAD)
              + 1067946459) ^ 0xE6E03877)
            - 359192087
            + 961945065) ^ 0xE1EECD69)
          - 1817072919) ^ 0x6B86ECF5)
        - 449212884) ^ 0x2012CCDB;
}
```

可以发现这次的输入是一个复杂的格式化字符串，`"%x %x %x"`意味着使用三个十六进制值作为输入，我们看一下汇编代码

![](https://note-book.obs.cn-east-3.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200804220541.png)

可以得知我们输入的三个值最后是分别赋值给了EAX，EBX，EDX寄存器，所以我们要控制输入只需要控制这三个寄存器的值就行

> **Q**: passwd0、passwd1、passwd2 是使用 claripy.BVS 创建的三个符号变量，代表三个密码，每个密码的大小为32位。这三个符号变量的值在测试的时候是怎样取值和变化的？<br>**A**: 在符号执行过程中，这些符号变量 passwd0、passwd1 和 passwd2 会被赋予一系列的值，这些值是由 angr 的路径群（state group）和探索策略（exploration strategy）决定的。angr 会尝试不同的输入组合来探索程序的所有可能行为。

> **Q**:约束可以以多种形式存在，这里angr是怎么根据这些原属来源找到具体约束的形式和位置？当多种约束都可以决定分支或者多个约束共同决定分支的时候，angr又怎么处理？<br>**A**:angr 是通过分析二进制程序的控制流和数据流来确定约束的形式和位置的。这个过程通常涉及以下几个步骤：
1. 控制流图（Control Flow Graph, CFG）构建
angr 首先会构建目标程序的控制流图（CFG）。CFG 是一个图，其中的节点表示程序的基本块（一段连续的指令序列，通常以跳转指令结束），边表示控制流的转移（即程序执行从一个基本块转移到另一个基本块的路径）。

2. 数据流分析
angr 执行数据流分析来跟踪变量的定义和使用，以及它们如何影响程序的执行。这包括寄存器和内存中的值。数据流分析帮助 angr 理解程序中的变量如何被计算和使用，以及它们如何影响程序的控制流。

3. 约束的识别
在执行到条件分支（如 if 语句、循环等）时，angr 会识别出这些条件，并将其转换为约束。例如，如果遇到 if (x > 10)，angr 会创建一个约束 x > 10。

4. 约束的应用
当 angr 遇到一个条件分支时，它会根据当前状态的约束来决定是否可以沿着这个分支执行。如果状态的约束满足分支条件，那么 angr 会探索这个分支；如果不满足，angr 会探索其他可能的分支或者创建新的状态。

5. 多约束处理
当多个约束共同决定一个分支时，angr 会尝试组合这些约束，以找到满足所有条件的路径。这可能涉及到以下策略：<br>(1) 路径分裂（Path Splitting）：angr 会创建多个新状态，每个状态包含不同的约束组合。这样，angr 可以并行探索多个可能的执行路径。<br>(2) 约束求解（Constraint Solving）：angr 使用求解器（如 claripy）来找到满足所有约束的变量值。如果求解器找到了解决方案，angr 会使用这些值来更新状态的约束，并继续探索。<br>(3) 状态合并（State Merging）：在某些情况下，angr 可能会合并具有相似约束的状态，以减少探索的状态数量并提高效率。
6. 探索策略
angr 提供了多种探索策略，如深度优先搜索（DFS）、广度优先搜索（BFS）、最大影响优先搜索（MIPS）等。这些策略帮助 angr 决定如何遍历状态空间，以及在遇到多个可能的分支时如何选择。

7. 状态空间探索
angr 会持续探索状态空间，直到找到满足 find 函数条件的状态或遇到 avoid 函数定义的条件。在探索过程中，angr 会不断更新状态的约束，并根据这些约束来分裂和合并状态。

通过上述过程，angr 能够有效地处理复杂的约束组合，并找到导致特定程序行为的输入。这个过程是自动化的，但也需要足够的时间和内存资源，因为符号执行可能会探索大量的状态和路径。





看一下最后的EXP，然后再逐步分析：

```python
import angr
import sys
import claripy
def Go():
    path_to_binary = "./03_angr_symbolic_registers" 
    project = angr.Project(path_to_binary, auto_load_libs=False)
    start_address = 0x08048980
    initial_state = project.factory.blank_state(addr=start_address)

    passwd_size_in_bits = 32
    # passwd0、passwd1、passwd2 是使用 claripy.BVS 创建的三个符号变量，代表三个密码，每个密码的大小为32位。claripy.BVS 是 claripy 库中的一个函数，用于创建符号化的比特向量（Bit Vector）。
    passwd0 = claripy.BVS('passwd0', passwd_size_in_bits)
    passwd1 = claripy.BVS('passwd1', passwd_size_in_bits)
    passwd2 = claripy.BVS('passwd2', passwd_size_in_bits)
    # 将这三个符号变量分别赋值给 initial_state 的寄存器 eax、ebx 和 edx，这些寄存器将被用于传递参数给二进制文件的入口点。
    initial_state.regs.eax = passwd0
    initial_state.regs.ebx = passwd1
    initial_state.regs.edx = passwd2
    # simulation 使用 project.factory.simgr 创建了一个符号执行的模拟图（state machine graph），从 initial_state 开始。
    simulation = project.factory.simgr(initial_state) 

    def is_successful(state):
        stdout_output = state.posix.dumps(sys.stdout.fileno())
        if b'Good Job.\n' in stdout_output:
            return True
        else: 
            return False

    def should_abort(state):
        stdout_output = state.posix.dumps(sys.stdout.fileno())
        if b'Try again.\n' in  stdout_output:
            return True
        else: 
            return False
    # simulation.explore 函数执行符号执行探索，寻找满足 is_successful 条件的状态，并避免满足 should_abort 条件的状态。
    simulation.explore(find=is_successful, avoid=should_abort)
  
    if simulation.found:
        for i in simulation.found:
            solution_state = i
            # 当 simulation.explore 找到满足 find 函数条件的状态时，它会停止探索并返回这些成功的状态。然后，代码会从这些成功的状态中提取 passwd0、passwd1 和 passwd2 的值，并将它们格式化为十六进制字符串输出。这些值是由 angr 在探索过程中动态计算和确定的，它们满足了程序的特定条件，即输出 "Good Job." 字符串。
            solution0 = format(solution_state.solver.eval(passwd0), 'x')
            solution1 = format(solution_state.solver.eval(passwd1), 'x')
            solution2 = format(solution_state.solver.eval(passwd2), 'x')
            solution = solution0 + " " + solution1 + " " + solution2
            print("[+] Success! Solution is: {}".format(solution))
            # print(simgr.found[0].posix.dumps(0))
    else:
        raise Exception('Could not find the solution')
    
if __name__ == "__main__":
    Go()
```

运行一下获得结果：

![](https://note-book.obs.cn-east-3.myhuaweicloud.com/Angr_CTF/%E4%B8%80/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20200804221823.png)

这次我们可以不用从main函数的开头开始，这里我们直接跳过`get_user_input()`函数，直接设置寄存器`eax, ebx, edx`

### states

从这题开始，我们可以更多的窥见states的功能，states这只是factory提供的多个构造函数中的一个，即  `AngrObjectFactory`，提供重要分析对象的接口

#### 状态预设

除了使用`.entry_state()` 创建 state 对象, 我们还可以根据需要使用其他构造函数创建 state:

|        名称        |                             描述                             |
| :----------------: | :----------------------------------------------------------: |
|  `.entry_state()`  |           构造一个已经准备好从函数入口点执行的状态           |
|   `.blank_state`   | 构造一个“空状态”，它的大多数数据都是未初始化的。当使用未初始化的的数据时，一个不受约束的符号值将会被返回 |
|   `.call_state`    |             构造一个已经准备好执行某个函数的状态             |
| `.full_init_state` | 构造一个已经执行过所有与需要执行的初始化函数，并准备从函数入口点执行的状态。比如，共享库构造函数（constructor）或预初始化器。当这些执行完之后，程序将会跳到入口点 |

请注意，这次我们使用的是`blank_state()`方法，而不是`entry_state()`。通过传递`addr=start_address`，我们有效地告诉`blank_state()`在该特定地址创建一个新状态

```python
start_address = 0x08048980
initial_state = project.factory.blank_state(addr=start_address)
```

#### 位向量(bitvector)

更应该准确的说是符号位向量，符号位向量是angr用于将符号值注入程序的数据类型。这些将是angr将解决的方程式的“ x”，也就是约束求解时的自变量。可以通过 `BVV(value,size)` 和 `BVS( name, size)` 接口创建位向量，也可以用 FPV 和 FPS 来创建浮点值和符号

在这里我们使用claripy通过`BVS()`方法生成三个位向量。此方法有两个参数：第一个是angr用来引用位向量的名称，第二个是位向量本身的大小（以位为单位）。由于符号值存储在寄存器中，并且寄存器的长度为32位，因此位向量的大小将为32位

```python
passwd_size_in_bits = 32
passwd0 = claripy.BVS('passwd0', passwd_size_in_bits)
passwd1 = claripy.BVS('passwd1', passwd_size_in_bits)
passwd2 = claripy.BVS('passwd2', passwd_size_in_bits)
```

#### 访问寄存器

`get_user_input()`对输入进行了解析并将其放入三个寄存器中，我们可以通过 `state.regs` 对象的属性访问以及修改寄存器的数据

是时候把我们之前创建的符号位向量（bitvectors）放入属于他们的地方：寄存器`EAX`，`EBX`和`EDX`。我们将修改`initial_state`之前创建的内容并更新寄存器的内容

```python
initial_state.regs.eax = passwd0
initial_state.regs.ebx = passwd1
initial_state.regs.edx = passwd2
```

现在我们必须定义`find`and `avoid`状态，我们将像以前一样进行操作：

```python
def is_successful(state):
	stdout_output = state.posix.dumps(sys.stdout.fileno())
	if b'Good Job.\n' in stdout_output:
		return True
	else: 
		return False

def should_abort(state):
	stdout_output = state.posix.dumps(sys.stdout.fileno())
	if b'Try again.\n' in  stdout_output:
		return True
	else: 
		return False

simulation.explore(find=is_successful, avoid=should_abort)
```

#### 约束求解

可以通过使用`state.solver.eval(symbol)`对各个断言进行评测来求出一个合法的符号值（若有多个合法值，返回其中的一个），我们根据`eval()`之前注入的三个符号值调用求解器引擎的方法

```python
solution0 = format(solution_state.solver.eval(passwd0), 'x')
solution1 = format(solution_state.solver.eval(passwd1), 'x')
solution2 = format(solution_state.solver.eval(passwd2), 'x')
solution = solution0 + " " + solution1 + " " + solution2
print("[+] Success! Solution is: {}".format(solution))
```
> **Q**:在探索过程中，angr 会创建多个状态（state），每个状态代表程序执行的一个可能路径。每个状态都有自己的寄存器和内存的副本，以及一组约束（constraints），这些约束定义了符号变量可能的值。随着探索的进行，angr 会根据程序的控制流和约束条件来更新这些状态的约束，并尝试新的输入组合。这里的约束具体是怎么样的？是不是对于每一个分支跳转结构都有这样一个约束，来控制跳转到每一条路径？还有就是这些约束有可能以那些形式存在？比如这里的寄存器值，临时变量或者全局变量值，或者控制跳转的标志位？

**A**:在 angr 的符号执行过程中，约束（constraints）是用来限制符号变量可能值的条件。这些约束来源于程序的控制流和数据流分析，它们确保符号执行能够准确地模拟程序的实际执行行为。下面是对约束的详细解释：
##### 约束的来源
条件分支：程序中的 if 语句、循环、跳转等控制流结构会产生约束。例如，if (x > 10) 会产生一个约束，限制 x 必须大于 10 才能沿着这个分支路径执行。

函数调用：函数参数、返回值和函数内部的逻辑也会产生约束。例如，如果一个函数期望接收一个非空指针，那么这个约束会被加入到状态中。

内存访问：对内存的读写操作也会产生约束。例如，如果程序试图读取一个数组的某个索引，那么这个索引必须在数组的有效范围内。

系统调用：在涉及操作系统交互的程序中，系统调用的参数和返回值也是约束的来源。

##### 约束的形式
约束可以以多种形式存在，包括但不限于：

寄存器值：例如，eax 寄存器的值必须满足某个条件，如 eax == 5。
内存地址：例如，访问的内存地址必须是有效的，或者某个内存区域的值必须满足特定条件。
全局变量值：全局变量的值可能受到程序逻辑的限制。
控制跳转的标志位：例如，条件跳转指令可能会设置或清除特定的标志位，如 zero flag 或 carry flag。
临时变量：在复杂的计算或逻辑操作中，临时变量的值也可能受到约束。
##### 约束的作用
在符号执行过程中，angr 会根据这些约束来探索程序的不同执行路径。每个状态都包含了一组当前满足的约束，这些约束定义了状态的可能行为。当程序执行到一个新的分支点时，angr 会根据分支条件分裂（split）状态，为每个可能的分支创建新的状态，并更新相应的约束。

例如，如果程序中有 if (x < 20) 这样的分支，angr 会创建两个新状态：一个满足 x < 20 的约束，另一个满足 x >= 20 的约束。然后，angr 会继续探索这些新状态，直到找到满足 find 函数条件的状态，或者遇到 avoid 函数定义的条件。

##### 约束的求解
在探索过程中，angr 会使用 claripy 的求解器来求解约束。求解器尝试找到满足所有当前约束的符号变量的具体值。当找到一个满足条件的状态时，angr 会记录下导致这个状态的输入值（即符号变量的值），并在探索结束后输出这些值作为解决方案。

总之，约束是 angr 符号执行中的关键概念，它们指导 angr 探索程序的不同执行路径，并最终找到满足特定条件的输入。这些约束可以来源于程序的各个方面，包括分支条件、内存访问、函数调用等，并且可以以多种不同的形式存在。

> **Q**:约束可以以多种形式存在，这里angr是怎么根据这些原属来源找到具体约束的形式和位置？当多种约束都可以决定分支或者多个约束共同决定分支的时候，angr又怎么处理？

**A**:angr 是通过分析二进制程序的控制流和数据流来确定约束的形式和位置的。这个过程通常涉及以下几个步骤：

1. 控制流图（Control Flow Graph, CFG）构建
angr 首先会构建目标程序的控制流图（CFG）。CFG 是一个图，其中的节点表示程序的基本块（一段连续的指令序列，通常以跳转指令结束），边表示控制流的转移（即程序执行从一个基本块转移到另一个基本块的路径）。

2. 数据流分析
angr 执行数据流分析来跟踪变量的定义和使用，以及它们如何影响程序的执行。这包括寄存器和内存中的值。数据流分析帮助 angr 理解程序中的变量如何被计算和使用，以及它们如何影响程序的控制流。

3. 约束的识别
在执行到条件分支（如 if 语句、循环等）时，angr 会识别出这些条件，并将其转换为约束。例如，如果遇到 if (x > 10)，angr 会创建一个约束 x > 10。

4. 约束的应用
当 angr 遇到一个条件分支时，它会根据当前状态的约束来决定是否可以沿着这个分支执行。如果状态的约束满足分支条件，那么 angr 会探索这个分支；如果不满足，angr 会探索其他可能的分支或者创建新的状态。

5. 多约束处理
当多个约束共同决定一个分支时，angr 会尝试组合这些约束，以找到满足所有条件的路径。这可能涉及到以下策略：

    - 路径分裂（Path Splitting）：angr 会创建多个新状态，每个状态包含不同的约束组合。这样，angr 可以并行探索多个可能的执行路径。
    - 约束求解（Constraint Solving）：angr 使用求解器（如 claripy）来找到满足所有约束的变量值。如果求解器找到了解决方案，angr 会使用这些值来更新状态的约束，并继续探索。
    - 状态合并（State Merging）：在某些情况下，angr 可能会合并具有相似约束的状态，以减少探索的状态数量并提高效率。
6. 探索策略
angr 提供了多种探索策略，如深度优先搜索（DFS）、广度优先搜索（BFS）、最大影响优先搜索（MIPS）等。这些策略帮助 angr 决定如何遍历状态空间，以及在遇到多个可能的分支时如何选择。

7. 状态空间探索
angr 会持续探索状态空间，直到找到满足 find 函数条件的状态或遇到 avoid 函数定义的条件。在探索过程中，angr 会不断更新状态的约束，并根据这些约束来分裂和合并状态。

  通过上述过程，angr 能够有效地处理复杂的约束组合，并找到导致特定程序行为的输入。这个过程是自动化的，但也需要足够的时间和内存资源，因为符号执行可能会探索大量的状态和路径。


> **Q**:在angr中，数据流分析时，除了分析代码中定义的和使用的变量意外，还有没有其他数据？比如寄存器值，跳转标志位等.

**A**:在 angr 中，数据流分析不仅仅局限于分析代码中定义和使用的变量，它还包括对程序执行过程中所有可能影响数据流的因素的分析。这当然包括寄存器值、跳转标志位等其他数据。以下是 angr 在数据流分析中可能考虑的一些其他数据类型：

1. 寄存器值：angr 会跟踪寄存器中的值，因为它们在程序执行中扮演着关键角色。寄存器通常用于存储临时计算结果、函数参数、返回值以及控制指令的执行。

2. 跳转标志位：许多指令会影响处理器的状态标志位，例如，比较指令和算术指令可能会设置零标志位、进位标志位等。这些标志位的值可能会影响后续的条件跳转指令。

3. 内存地址和内容：angr 会分析内存读写操作，包括对全局变量、堆和栈的访问。内存地址的有效性和内存内容的变化都是数据流分析的一部分。

4. 控制流相关的变量：某些程序可能会使用特殊的变量来控制执行流程，例如，用于循环计数的变量或用于确定分支选择的变量。

5. 系统调用和外部函数的参数：当程序进行系统调用或调用外部库函数时，参数的值和返回值也会影响数据流。

6. 程序状态和配置：程序的某些状态，如是否处于异常处理状态，或者程序的配置选项，也可能影响数据流。

angr 使用这些数据来构建符号执行的状态，每个状态都包含了程序在某一时刻的所有可能信息。在探索过程中，angr 会根据程序的执行逻辑和约束条件来更新这些数据，并根据这些更新来探索新的执行路径。



## 参考文献

【1】angr官方文档—— https://docs.angr.io/core-concepts

【2】angr 系列教程(一)核心概念及模块解读—— https://xz.aliyun.com/t/7117#toc-14

【3】Introduction to angr Part 0 —— https://blog.notso.pro/2019-03-20-angr-introduction-part0/

【4】angr文档翻译 —— https://www.jianshu.com/p/3ecafe70157

【5】AngrCTF_FITM —— https://github.com/ZERO-A-ONE/AngrCTF_FITM
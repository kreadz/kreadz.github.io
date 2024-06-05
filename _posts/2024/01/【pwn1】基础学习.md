## ubuntu中pwndbg的配置
**pwndbg启动之~/.gdbinit配置**
```shell
source /home/z/pwndbg/gdbinit.py
set context-output /dev/pts/1 # 实现gdb调试信息输出至/dev/pts/1
```
参考杜超大佬,如下配置写入~/.gdbinit，如果使用pwndbg需要alias写入gdb=init-pwndbg
```shell
define init-peda
source /home/z/peda/peda.py
peda config context.redirec/dev/pst/1
end
document init-peda
Initializes the PEDA (Python Exploit Development Assistant for GDB) framework
end

define init-pwndbg
source /home/z/pwndbg/gdbinit.py
set context-output /dev/pts/1
end
document init-pwndbg
Initializes PwnDBG
end

define init-gef
source /home/z/gef/gef.py
#gef config context.redirect /dev/pst/1
end
document init-gef
Initializes GEF (GDB Enhanced Features)
end

```

## 脚本简易快速入门
```python
#导入Pwntools
from pwn import *
#链接
r = remote("目标地址str类型", 目标端口int类型)与服务器交互
r = process("目标程序位置")与本地程序交互
构造playload之打包
p64(int)将int类型打包成64位存储
p32(int)将int类型打包成32位存储
发送
r.sendline(playload)发送playload为一行（自动在尾部加上\n）
接收
r.recv()接收到结束
r.recvuntil(end, drop=True)end(str)接受到end之后截至，drop=True时不包括end，drop=False时包括end
#打开交互
r.interactive()一般在末尾都要加
```

## 栈
ESP 栈顶指针 （extended stack pointer）英文直译是：扩展栈指针
EBP 栈底指针 ，指的是本层call子程序的栈底，就是最上层call的栈底。不是整个栈空间的栈底 （extended base pointer）英文直译是扩展基址指针

#### push 入栈（给call传参数）
push eax 等价于 sub esp , 4 mov [esp],eax 把eax压入栈等价于 县 让esp栈指针 - 4 ，然后把 eax的值存入到 esp指向的空间里，也就是栈顶空间里

#### pop 出栈（call 结束后还原eip）
pop eax 等价于 mov eax,[esp] add esp , 4 把栈里的值出栈给eax 。等价于 先把 esp栈顶指向的空间的值 复制给 eax,然后把栈顶指针 + 4

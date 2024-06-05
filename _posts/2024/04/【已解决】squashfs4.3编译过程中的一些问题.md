#! https://zhuanlan.zhihu.com/p/692513152
## Q: 执行./build.sh时，mksquashfs.c和unsquashfs.c报错找不到major()和minor()函数的定义，找不到‘makedev’

```shell
cc -O2  -I. -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_GNU_SOURCE -DCOMP_DEFAULT=\"gzip\" -Wall -DGZIP_SUPPORT -DXATTR_SUPPORT -DXATTR_DEFAULT   -c -o mksquashfs.o mksquashfs.c
mksquashfs.c: In function ‘create_inode’:
mksquashfs.c:987:24: error: called object ‘major’ is not a function or function pointer
  987 |   unsigned int major = major(buf->st_rdev);
      |                        ^~~~~
mksquashfs.c:987:16: note: declared here
  987 |   unsigned int major = major(buf->st_rdev);
      |                ^~~~~
mksquashfs.c:988:24: error: called object ‘minor’ is not a function or function pointer
  988 |   unsigned int minor = minor(buf->st_rdev);
      |                        ^~~~~
mksquashfs.c:988:16: note: declared here
  988 |   unsigned int minor = minor(buf->st_rdev);
      |                ^~~~~
mksquashfs.c:1011:24: error: called object ‘major’ is not a function or function pointer
 1011 |   unsigned int major = major(buf->st_rdev);
      |                        ^~~~~
mksquashfs.c:1011:16: note: declared here
 1011 |   unsigned int major = major(buf->st_rdev);
      |                ^~~~~
mksquashfs.c:1012:24: error: called object ‘minor’ is not a function or function pointer
 1012 |   unsigned int minor = minor(buf->st_rdev);
      |                        ^~~~~
mksquashfs.c:1012:16: note: declared here
 1012 |   unsigned int minor = minor(buf->st_rdev);
      |                ^~~~~
mksquashfs.c: In function ‘dir_scan2’:
mksquashfs.c:3527:17: warning: implicit declaration of function ‘makedev’ [-Wimplicit-function-declaration]
 3527 |   buf.st_rdev = makedev(pseudo_ent->dev->major,
      |                 ^~~~~~~
make: *** [<builtin>: mksquashfs.o] Error 1

```

**解决方法**

### step1
vim ./buid.sh
注释掉以下两句

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/cdf07d987d87424eabc52c07b5327fe0.png)

这里是为了下一步我们修改mksquashfs.c和unsquashfs.c不被覆盖。

### step2
在mksquashfs.c和unsquashfs.c文件中加上头文件
```
include <sys/sysmacros.h>

```
### step3 
再次运行./buid.sh

## 其他问题
wget https://downloads.sourceforge.net/project/squashfs/squashfs/squashfs4.3/squashfs4.3.tar.gz
时卡住，可以修改./buid.sh中的这句代码，换成sourceforge的镜像

```
https://liquidtelecom.dl.sourceforge.net/
```
将下载地址中https://nchc.dl.sourceforge.net/改为https://liquidtelecom.dl.sourceforge.net/

## 参考
1. https://blog.csdn.net/zhangxu5274/article/details/116033700
2. https://blog.csdn.net/u012763794/article/details/79957554

1、先安装依赖：
```shell
sudo apt-get install python-dev libffi-dev build-essential virtualenvwrapper
```
1
2、然后修改配置文件，在用户根目录下编辑.bashrc文件,添加如下代码：
```shell
export WORKON_HOME=$HOME/.virtualenvs
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
```

3、启动配置文件：
```shell
source ~/.bashrc
```
4、 最后就可以直接安装了：
```shell
mkvirtualenv --python=$(which python3) angr && pip install angr
```
5、然后还有其他一些的命令：
workon查看其他环境
![](https://img-blog.csdnimg.cn/img_convert/b3a58d5fb42954a4a83a4af161fb9880.png)

进入angr环境


![](https://img-blog.csdnimg.cn/img_convert/de8a12b22a91067acba76382deac7ffa.png)
退出

![](https://img-blog.csdnimg.cn/img_convert/def47760ffd8ff28c0233a6bf4696078.png)

![](https://img-blog.csdnimg.cn/img_convert/55bf875de847adb650bfd9b414c1aefd.png)

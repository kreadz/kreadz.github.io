本文主要介绍Cisco ASA5520型号防火墙系统，并进行模拟测试实验。主要目的是：

1. 利用eveng模拟搭建测试环境和网络拓扑。
2. 摸清ASA5520系统的ACL访问控制机制

## 1 前置知识
![](https://img-blog.csdnimg.cn/img_convert/b84331ea4aef40bf8ddd8d057df5b5ec.png)

SecureCRT打开SFTP
```shell
lcd F:\Download # 打开发送端目录
cd /opt/unetlab/addons/qemu # 打开接收端目录
put -r xxx #上传某个目录
# put xxx.zip #上传文件
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions
# 59a79d05-01fa-445a-88a9-fab3c73c3307
```

上传文件

![](https://img-blog.csdnimg.cn/img_convert/ce3b9a019e684c1f353995f91ece527c.png)

添加设备

![](https://img-blog.csdnimg.cn/img_convert/19afc27d4052cd31dc158d8787956f69.png)

修改telnet目的shell的应用

![](https://img-blog.csdnimg.cn/img_convert/0a9655bc48a9bf40b29d0dcb94bf9e8d.png)

在浏览提端打开可跳转SecureCRT打开shell

![](https://img-blog.csdnimg.cn/img_convert/0209e7766b86728d3f36c3e87395f398.png)

但是使用securecrt打开遇到了非法端口号问题，研究无解，遂安装Xshell可以


## 2 路由配置
### 2.1 VPC模拟搭建拓扑环境
eth0和eth1

![](https://img-blog.csdnimg.cn/img_convert/2b34ca0303499d1977b0a79f76306a4a.png)



![](https://img-blog.csdnimg.cn/img_convert/5f51bf84d4daab3ef9545626988862e4.png)


![](https://img-blog.csdnimg.cn/img_convert/66cafa79e8281ed1699b1f702abdcee5.png)

上面是简单的虚拟pc搭建，证明环境模拟的可行性，下面将进行实际win主机模拟搭建拓扑环境。

### 2.2 Win7 x64模拟搭建拓扑环境
Win7镜像制作和导入具体内容参考：
- https://blog.csdn.net/kengkeng123qwe/article/details/123179096
- 镜像添加技巧：https://www.shiyl.com/archives/eve-ng-2.html

相关问题解决链接：
- 【已解决】EVENG导入Win7镜像以后可以启动无法VNC打开https://blog.csdn.net/void_zk/article/details/136281727

最终拓扑：

![](https://img-blog.csdnimg.cn/img_convert/2b6cddaf09f8534eedcdd88ac67d3daf.png)


### 2.3 日志功能开启、查看与配置
**启用日志：logging enable**
你会看到：
```cli
ciscoasa# show logging 
Syslog logging: disabled
    Facility: 20
    Timestamp logging: disabled
    Hide Username logging: enabled
    Standby logging: disabled
    Debug-trace logging: disabled
    Console logging: disabled
    Monitor logging: disabled
    Buffer logging: disabled
    Trap logging: disabled
    Permit-hostdown logging: disabled
    History logging: disabled
    Device ID: disabled
    Mail logging: disabled
    ASDM logging: disabled
```
但是这个时候**show logging**命令我们什么日志细节都看不见，如何解决呢？

不知道怎么了，最近连cisco官网都进不去了，cisco设备相关问题的官方回答都看不到了。日志查看的命令一直搜寻未果，后来在一篇帖子里终于找到：
> 启用日志记录并不意味着您可以在 CLI 或 ASDM 上查看日志，因为 ASA 仅生成消息，但不会将其保存到您可以查看它们的位置，因此您需要指定 ASA 应将日志发送到哪些位置。<br>(https://www.packetswitch.co.uk/cisco-asa-syslog-simplified/)

假设我想查看严重性级别为 CLI 和更低 ASDM 的日志。运行以下命令将系统日志发送到内部缓冲区和 ASDM。默认内部缓冲区大小为 4KB，可以使用该命令增加大小。应用配置后，**可以从 CLI（通过发出）和 ASDM（通过实时日志）查看日志。**

```cli
logging buffered warnings #
logging asdm informational
logging buffer-size 102400 #增加内部缓冲区大小
```
设置完毕，就应该能看到相关的日志内容了。使用Outside的主机【202.100.1.1】ping Inside的主机【10.1.1.1】。

![](https://img-blog.csdnimg.cn/img_convert/c463133dde40f13e795d8f073ce21d14.png)

查看防火墙日志。此时日志就已经打印在cli中了。

![](https://img-blog.csdnimg.cn/img_convert/9f947b3bf58b9322d945632a9f556824.png)

### 2.4 ASDM安装：
- 参考：https://blog.csdn.net/GhostRaven/article/details/85179833

不用设置静态IP，新增网卡之后直接配置就好了
#### asa配置
![](https://img-blog.csdnimg.cn/img_convert/32297a6d1197c73543dfd8c869aed8c2.png)


#### ASDM Launcher安装

![](https://img-blog.csdnimg.cn/img_convert/39a9e64ec807cb3b593b74a89fde1001.png)

使用前需要先安装JAVA虚拟机jre-6u20-windows-i586_itmop.com.exe，安装了JRE后就能正常开始使用

![](https://img-blog.csdnimg.cn/img_convert/8865359c857f068b15980202263696ef.png)

这里的eth2是我新增eveng中一块主机模式的网卡，这样eveng中的虚拟设备就可以从本地访问了。但是好像不能和本机的内网网段冲突，比如我这里是192.168.226.0/24,本机是192.168.59.0/24。

#### 结果：
能够成功登录ASDM，可查看日志等信息。

![](https://img-blog.csdnimg.cn/img_convert/d09564b72ee9307e9688dc4426a5fd5e.png)


## 3 防火墙预警反馈测试
### 3.1 telnet连接

![](https://img-blog.csdnimg.cn/img_convert/e8712e8d5369e6163c4b7beb72932bb5.png)

对于从其他区域达到内网因为ASA会拦截一切陌生流量（白名单模式），所以连接内部设备的telnet请求肯定会被拦截。

查看日志拦截到相关请求：

![](https://img-blog.csdnimg.cn/img_convert/a86c2d3889fb86417eafa4c73f0ac421.png)

### 3.2 web端访问被拦截

从主机模式的网卡尝试访问ASA的web端，发现也被拦截

![](https://files.mdnice.com/user/53147/d441e035-e117-45d0-87e6-ab3c66faf0d6.png)




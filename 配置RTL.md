
# 配置 Remote_Terminal

1.配置Napcat
(napcat推荐部署在linux 系统上，因为在Windows 上部署napcat有很大的可能被大手做局)

[Napcat安装](https://napneko.github.io/guide/boot/Shell)

在安装完napcat后,通过终端执行napcat即可进入napcat的终端配置页面

在终端页面中,先选择"查看日志"

在日志输出中,使用手机QQ登录napcat

随后返回,选择"配置 Napcat"

选择你所登录的QQ账户对应的QQ号

选择"Websocket 服务端"

配置对应的端口及token

在配置完成后,退出并进行下一步

2.配置环境

首先,你需要设置一个新的Python虚拟环境(这里以conda为例)

[Linux 安装 Anaconda](https://www.anaconda.com/docs/getting-started/anaconda/install/linux-install)

安装好Anaconda后,使用任意一种方法(sftp,wget,ftp)将该项目上传/下载到Linux 系统中

对于虚拟环境的配置，我推荐使用VS code + ssh 连接 + Python插件的形式安装

在配置好虚拟环境后,在虚拟环境中执行 "pip install -r requirements.txt" 安装依赖  

3.获取Github_PAT

[获取Github_PAT](https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#%E5%88%9B%E5%BB%BA-personal-access-token-classic)

4.配置config.py

按照config.py 中的注释修改文件

5.运行

使用虚拟环境中的python 运行main.py

在正常情况下,应该可见终端中输出"连接成功！当前登录账号: "

至此，便安装好了rtl

# hnzj-login

## 目录

- [介绍](#about)
- [入门](#getting_started)
- [使用](#usage)

## 介绍 <a name = "about"></a>
此项目用于登录自动登录河南职业技术学院校园网。

## 入门 <a name = "getting_started"></a>

### 环境安装

```
pip install -r requirements.txt
```
### 运行
```
python main.py
```


## 使用 <a name = "usage"></a>

使用前，请先配置config.ini文件，具体配置如下：

```
[login]
# 账号
userid      = 0123456789
# 密码
password    = 012345
# 运营商，如电信："ctc"、联通: "cucc"、移动："cmcc"
Corporation = cmcc

[config]
# 持续运行防止网络断开, True为是，False为否
keep_alive  = False
# 每隔多少秒运行一次
timesleep   = 60
# 测试网址
pingurl     = bing.com
# 窗口隐藏
hide_window = False
```

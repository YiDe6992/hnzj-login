import time
import login
import configparser
import logging
import ctypes

version = "0.0.1"
logging.info("程序开始 " + login.sys_time())
logging.info("版本：" + version)

# 读取配置文件
config = configparser.ConfigParser()
logging.info("读取配置文件")
try:
    config.read('config.ini')
except UnicodeDecodeError:
    config.read('config.ini', encoding='utf-8-sig')
except Exception as e:
    logging.error("配置文件读取失败")
    exit()

# 获取登录信息
userid      = config['login']['userid']
password    = config['login']['password']
Corporation = config['login']['Corporation']

# 判断是否开启自动登录
if config['config']['keep_alive'] == 'True':
    keep_alive = True
else:
    keep_alive = False

# 判断是否隐藏窗口
if config['config']['hide_window'] == 'True':
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        # 隐藏窗口
        ctypes.windll.user32.ShowWindow(whnd, 0) 
        logging.info("窗口已隐藏")

# 获取等待时间  
timesleep  = float(config['config']['timesleep'])

# 获取测试网址
pingurl = config['config']['pingurl']

# 程序逻辑
if keep_alive:
    logging.info("持续运行已开启")
    while True:
        logging.info("检查网络")

        if login.ping("bing.com") == False:
            logging.info("尝试连接校园网")
            login.run(userid, password, Corporation)
            logging.info("等待{}秒".format(timesleep))
        else:
            logging.info("网络正常")
            logging.info("等待{}秒".format(timesleep))
        time.sleep(timesleep)
else:
    logging.info("持续运行已关闭")
    logging.info("检查网络")
    if login.ping(pingurl) == False:
        logging.info("尝试连接校园网")
        login.run(userid, password, Corporation)
    else:
        logging.info("网络正常")

    logging.info("程序结束 " + login.sys_time())

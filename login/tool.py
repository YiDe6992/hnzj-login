import time
import configparser
import logging


# 获取当前时间
def sysTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# 读取配置文件
def initconfig():
    config = configparser.ConfigParser()
    logging.info("读取配置文件")
    try:
        config.read('config.ini')
    except UnicodeDecodeError:
        config.read('config.ini', encoding='utf-8-sig')
    except Exception as e:
        logging.error("配置文件读取失败")
        exit()

    return config
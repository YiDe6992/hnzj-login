import time
import logging
import login.login as login
import login.tool as tool
import login.log as log


version = "0.0.2"

def main():
    # 初始化日志
    log.logInit()

    logging.info("程序开始 " + tool.sysTime())
    logging.info("版本：" + version)

    # 初始化配置文件
    config = tool.initconfig()
    # 获取等待时间  
    timesleep  = float(config['config']['timesleep'])
    # 判断是否开启自动登录
    match config["config"]["keepalive"].lower():
        case "true":
            keepAlive = True
        case "false":
            keepAlive = False
        case _:
            keepAlive = False        # 兜底，防止配置写错

    app = login.LoginApp(
        config['config']['pingurl'],
        config['login']['userid'],
        config['login']['password'],
        config['login']['Corporation'],
        int(config["login"]["nettype"])
    )

    a = True
    while a:
        if keepAlive:
            logging.info("持续运行已开启")

        logging.info("检查网络")
        if app.ping():
            logging.info("网络正常")
        else:
            logging.info("尝试连接校园网")
            app.run()

        if keepAlive:
            time.sleep(timesleep)
            logging.info("等待{}秒".format(timesleep))
        else:
            a = False
            logging.info("程序结束 " + tool.sysTime())
        


if __name__ == "__main__":
    main()
import logging

def logInit():
    # 创建文件处理器并指定UTF-8编码
    file_handler = logging.FileHandler('log.txt', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 添加文件处理器
    logger.addHandler(file_handler)

    # 创建一个输出到控制台的处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 设置控制台日志级别

    # 设置控制台输出的格式
    console_handler.setFormatter(formatter)

    # 将控制台处理器添加到根日志记录器
    logger.addHandler(console_handler)
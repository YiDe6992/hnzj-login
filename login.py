import os
import sys
import time
import platform
import ctypes
import logging
import ping3
import socket
import requests
import psutil


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

# 检测是否从终端运行
def is_running_from_terminal():
    """检查程序是否从终端运行"""
    try:
        # 方法1: 检查标准输出是否连接到终端
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        
        # 方法2: 检查是否有控制台窗口 (Windows)
        if os.name == 'nt':
            GetConsoleWindow = ctypes.windll.kernel32.GetConsoleWindow
            return GetConsoleWindow() != 0
            
    except Exception:
        pass
    return False

# 获取当前时间
def sys_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# 执行 ping 命令并返回结果

def ping(host):
    try:
        # 根据操作系统设置适当的超时和计数
        if platform.system().lower() == "windows":
            # Windows 默认发送 4 个包
            result = ping3.ping(host, timeout=10)
        else:
            # Linux/Mac 默认发送 4 个包
            result = ping3.ping(host, timeout=10)
        
        # ping3 返回延迟时间（秒）或 False（如果失败）
        # 如果返回数字（延迟时间），则表示成功；如果返回 False 或 None，则表示失败
        return result is not None and result is not False
    except Exception:
        # 任何异常都返回 False
        return False
    

# 获取本机当前使用的IP地址
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("114.114.114.114", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None
    
# 根据IP地址获取对应的MAC地址
def get_mac_by_ip(target_ip):
    
    try:
        interfaces = psutil.net_if_addrs()
        
        for _, addresses in interfaces.items():
            ipv4_addr = None
            mac_addr = None
            
            # 遍历每个地址族的信息
            for addr in addresses:
                # 使用正确的地址族常量
                if addr.family == socket.AF_INET:  # IPv4地址
                    ipv4_addr = addr.address
                elif addr.family == psutil.AF_LINK:  # MAC地址
                    mac_addr = addr.address
            
            # 如果找到匹配的IP，返回对应的MAC地址
            if ipv4_addr == target_ip and mac_addr:
                # 确保MAC地址格式为连字符分隔
                return mac_addr.replace(':', '-')
    except Exception as e:
        logging.error(f"获取MAC地址时出错: {e}")
    
    return None


def run(userid, password, Corporation):
    # 获取当前网络信息
    current_ip = get_ip_address()
    if not current_ip:
        logging.error("无法获取IP地址，请检查网络连接")
        exit(1)

    current_mac = get_mac_by_ip(current_ip)
    if not current_mac:
        current_mac = "00-00-00-00-00-00"
        logging.warning("无法获取MAC地址，使用默认值")

    logging.info(f"当前MAC: {current_mac}")
    logging.info(f"当前MAC: {current_mac}")

    # 用户信息
    username = userid + "@" + Corporation
    # 基础URL
    base_url = "http://172.16.1.38:801/eportal/"

    # 参数字典
    params = {
        "c": "ACSetting",
        "a": "Login",
        "loginMethod": "1",
        "protocol": "http:",
        "hostname": "172.16.1.38",
        "port": "",
        "iTermType": "1",
        "wlanuserip": current_ip,
        "wlanacip": "null",
        "wlanacname": "null",
        "redirect": "null",
        "session": "null",
        "vlanid": "0",
        "mac": current_mac,
        "ip": current_ip,
        "enAdvert": "0",
        "jsVersion": "2.4.3",
        "DDDDD": f",0,{username}",
        "upass": password,
        "R1": "0",
        "R2": "0",
        "R3": "0",
        "R6": "0",
        "para": "00",
        "0MKKey": "123456",
        "buttonClicked": "",
        "redirect_url": "",
        "err_flag": "",
        "username": "",
        "password": "",
        "user": "",
        "cmd": "",
        "Login": "",
        "v6ip": ""
    }

    try:
        # 先访问一次门户页面，获取可能的cookie
        session = requests.Session()
        logging.info("正在访问门户页面...")
        portal_response = session.get("http://172.16.1.38", timeout=10)
        logging.info(f"门户页面访问状态码: {portal_response.status_code}")

        # 发送认证请求

        logging.info("正在发送认证请求...")
        response = session.get(base_url, params=params, timeout=10)
        logging.info(f"认证请求状态码: {response.status_code}")
        
        # 检查响应内容
        response_text = response.text
        if "认证成功" in response_text:
            logging.info("认证成功!")
        elif "已在线" in response_text:
            logging.info("账号已在其他设备登录")
        elif "密码错误" in response_text:
            logging.error("密码错误，请检查后重试")
        elif "Msg=01" in response_text:
            logging.error("认证失败，错误代码01")
        else:
            logging.error("无法确定认证结果，响应内容:")
            logging.error(response_text[:500])
            
    except requests.exceptions.RequestException as e:
        logging.error("请求失败:", e)
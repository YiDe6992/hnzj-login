import os
import sys
import platform
import ctypes
import logging
import time
import ping3
import socket
import requests
import psutil


class LoginApp():
    def __init__(self, host, userid, password, Corporation, nettype):
        self.host           = host
        self.userid         = userid
        self.password       = password
        self.Corporation    = Corporation
        self.nettype        = nettype

    def run(self):
        # 获取当前网络IP
        current_ip = self.get_ip_address()
        if not current_ip:
            logging.error("无法获取IP地址，请检查网络连接")
            exit(1)
        # 获取当前网络MAC
        current_mac = self.get_mac_by_ip(current_ip)
        if not current_mac:
            current_mac = "00-00-00-00-00-00"
            logging.warning("无法获取MAC地址，使用默认值")

        logging.info(f"当前MAC: {current_mac}")

        # 组合用户信息
        username = self.userid + "@" + self.Corporation

        match self.nettype:
            case 0:
                # 学生校园网
                base_url = "http://172.16.1.38:801/eportal/"
                params = {
                    "c": "ACSetting",
                    "a": "Login",
                    "loginMethod": "1",
                    "protocol": "http:",
                    "hostname": "172.16.1.38",
                    "port": "",
                    "iTermType": "1",
                    "wlanuserip": current_ip,
                    "wlanacip": "172.20.1.1",
                    "wlanacname": "",
                    "redirect": "null",
                    "session": "null",
                    "vlanid": "0",
                    "mac": current_mac,
                    "ip": current_ip,
                    "enAdvert": "0",
                    "jsVersion": "2.4.3",
                    "DDDDD": f",0,{username}",
                    "upass": self.password,
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

            case 1:
                # 老师校园网
                base_url = "http://10.100.2.30:801/eportal/portal/login"
                params = {
                    "callback": "dr1003",
                    "login_method": 1,
                    "user_account": f",0,{username}",
                    "user_password": self.password,
                    "wlan_user_ip": current_ip,
                    "wlan_user_ipv6": "",
                    "wlan_user_mac": current_mac,
                    "wlan_ac_ip": "",
                    "wlan_ac_name": "",
                    "jsVersion": "4.2.1",
                    "terminal_type": 1,
                    "lang": "zh-cn",
                    "lang": "zh",
                    "v": str(int(time.time()*1000))[-4:] 
                }
        
        try:
            # 先访问一次门户页面，获取可能的cookie
            session = requests.Session()
            logging.info("正在访问门户页面...")
            match self.nettype:
                case 0:
                    portal_response = session.get("http://172.16.1.38", timeout=10)
                case 1:
                    portal_response = session.get("http://10.100.2.30", timeout=10)
                case _:
                    raise ValueError(f"不支持的 nettype: {self.nettype}")
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


    # 检测是否从终端运行 暂不使用
    def _is_running_from_terminal(self):
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


    # 执行 ping 命令并返回结果
    def ping(self) -> bool:
        try:
            # 无论 Windows 还是 Linux/Mac，统一用 ping3
            delay = ping3.ping(str(self.host), timeout=10)
            return isinstance(delay, (int, float)) and delay > 0
        except Exception:
            return False
    

    # 获取本机当前使用的IP地址
    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("114.114.114.114", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None
    

    # 根据IP地址获取对应的MAC地址
    def get_mac_by_ip(self, target_ip):
        
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



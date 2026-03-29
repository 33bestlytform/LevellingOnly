# utils/logger.py
import logging
import os
import datetime

class Logger:
    def __init__(self):
        """初始化日志"""
        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建日志文件
        log_file = os.path.join(log_dir, f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def info(self, message):
        """
        记录信息日志
        :param message: 日志信息
        """
        self.logger.info(message)
    
    def warning(self, message):
        """
        记录警告日志
        :param message: 日志信息
        """
        self.logger.warning(message)
    
    def error(self, message):
        """
        记录错误日志
        :param message: 日志信息
        """
        self.logger.error(message)
    
    def debug(self, message):
        """
        记录调试日志
        :param message: 日志信息
        """
        self.logger.debug(message)
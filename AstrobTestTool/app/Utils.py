import logging
import os.path
from datetime import datetime
from os.path import abspath
from threading import Thread

import yaml
from PySide2.QtWidgets import QFileDialog


class ConfigManager:
    def __init__(self, config_path: str):
        """
        config_path:为yaml文件的路径
        """
        self.config_path = None
        self.config = None
        self.reload_config(config_path)

    def reload_config(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileExistsError
        self.config_path = config_path
        with open(self.config_path, 'r') as configfile:
            config = yaml.safe_load(configfile)
        self.config = config

    def set_config(self, config_obj: object):
        if not self.config_path:
            raise AttributeError('config not set')
        with open(self.config_path, 'w') as configfile:
            yaml.dump(config_obj, configfile)


def get_save_path(window, file_method):
    try:
        file_name = '[' + str(datetime.now())[5:].replace(":", "·").replace("-", "").split(".")[0].replace(" ", "]")
        file_name = file_name.split(']')[0] + f']' + file_name.split(']')[1]
        filePath = QFileDialog.getSaveFileName(window, '保存路径', f'{abspath(".")}\\screen\\{file_name}.{file_method}',
                                               f'.{file_method}(*.{file_method})')

        return filePath[0]
    except TypeError:
        print('save_file:TypeError', 1)
        return False


def open_save_file(file_path):
    try:
        from os import system
        thread = Thread(target=system, args=[f"{file_path}", ])
        thread.setDaemon(True)
        thread.start()
        return file_path
    except FileNotFoundError:
        print('%s文件不存在' % file_path)


class LogManager:
    logger = logging.getLogger('AstrobTestToolLogger')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('TestTool.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    @staticmethod
    def debug(message):
        LogManager.logger.debug(message)

    @staticmethod
    def info(message):
        LogManager.logger.info(message)

    @staticmethod
    def warning(message):
        LogManager.logger.warning(message)

    @staticmethod
    def error(message):
        LogManager.logger.error(message)

    @staticmethod
    def pull_log(device_path, bytes_written, total_bytes):
        LogManager.debug(f"Pulling {device_path}: {bytes_written}/{total_bytes} bytes")

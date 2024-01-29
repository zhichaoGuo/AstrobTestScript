import gzip
import logging
import os
import pickle

import pymssql
import yaml

from QuerySqlDataCase.QueryScript import QueryObj, QueryEJV


class PathUtils:
    @staticmethod
    def get_path_all_dir(path: str) -> list:
        """
        返回path下文件夹的绝对路径的列表
        :param path: 绝对路径
        :return: 绝对路径的列表
        """
        r = []
        for path_dir in os.listdir(path):
            # 跳过文件
            if os.path.isdir(os.path.join(path, path_dir)):
                r.append(os.path.join(path, path_dir))
        return r

    @staticmethod
    def get_path_all_xml(path: str) -> list:
        """
        返回path下xml文件的绝对路径的列表
        :param path:
        :return:
        """
        r = []
        for path_file in os.listdir(path):
            xml_full_path = os.path.join(path, path_file)
            if os.path.isfile(xml_full_path) and xml_full_path[-4:].lower() == '.xml':
                r.append(xml_full_path)
        return r

    @staticmethod
    def get_path_all_xml_gz(path: str) -> list:
        """
        返回path下.xml.gz文件的绝对路径的列表
        :param path: 绝对路径
        :return: .xml.gz文件的绝对路径的列表
        """
        r = []
        for zip_path in os.listdir(path):
            zip_full_path = os.path.join(path, zip_path)
            if os.path.isfile(zip_full_path) and zip_full_path[-7:].lower() == '.xml.gz':
                r.append(zip_full_path)
        return r

    @staticmethod
    def get_path_all_xlsx(path: str) -> list:
        """
        返回path下.xlsx文件的绝对路径的列表
        :param path: 绝对路径
        :return: .xlsx文件的绝对路径的列表
        """
        r = []
        for zip_path in os.listdir(path):
            zip_full_path = os.path.join(path, zip_path)
            if os.path.isfile(zip_full_path) and zip_full_path[-5:].lower() == '.xlsx':
                r.append(zip_full_path)
        return r

    @staticmethod
    def get_path_all_dat(path: str) -> list:
        """
        返回path下.dat文件的绝对路径的列表
        :param path: 绝对路径
        :return: .dat文件的绝对路径的列表
        """
        r = []
        for zip_path in os.listdir(path):
            zip_full_path = os.path.join(path, zip_path)
            if os.path.isfile(zip_full_path) and zip_full_path[-4:].lower() == '.dat':
                r.append(zip_full_path)
        return r


class ZipUtils:
    @staticmethod
    def unzip_gz_and_delete(zip_file_path: str) -> bool:
        """
        解压缩.gz文件到当前路径并删除原文件
        :param zip_file_path: .gz文件绝对路径
        :return:
        """
        try:
            unzip_file_name = os.path.basename(zip_file_path)[:-3]
            unzip_file_path = os.path.join(os.path.dirname(zip_file_path), unzip_file_name)
            with gzip.open(zip_file_path, 'rb') as f_in, open(unzip_file_path, 'wb') as f_out:
                f_out.write(f_in.read())
            os.remove(zip_file_path)
            LogUtils.debug('[解压完成]%s' % zip_file_path)
            return True
        except Exception as err:
            LogUtils.error('unzip gz and delete fail:%s' % err)
            return False


class LogUtils:
    logger = logging.getLogger('QueryDataCaseLogger')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('QueryDataCase.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    @staticmethod
    def debug(message):
        LogUtils.logger.debug(message)

    @staticmethod
    def info(message):
        LogUtils.logger.info(message)

    @staticmethod
    def warning(message):
        LogUtils.logger.warning(message)

    @staticmethod
    def error(message):
        LogUtils.logger.error(message)


class SqlServer:
    def __init__(self, host, port, user, password, database):
        self.conn = pymssql.connect(host=host, port=port,
                                    user=user, password=password,
                                    database=database)
        self.cursor = self.conn.cursor()

    def query(self, script_obj: QueryObj) -> list:
        """
        执行查询，接受查询类，需要实现script方法和QueryResults子类
        如果查询语句需要参数，需要先将查询类实例化传递参数存为私有变量，由script方法直接拿实例私有变量
        :param script_obj:
        :return:
        """
        LogUtils.info(script_obj.script())
        self.cursor.execute(script_obj.script())
        res = []
        for r in self.cursor.fetchall():
            if r:
                res.append(script_obj.QueryResults(r))

        return res

    def close(self):
        self.conn.close()


class ModelUtils:
    @staticmethod
    def return_unique_node(nodes: list, aim_node: QueryEJV.QueryResults) -> (list or None):
        """
        返回列表中坐标不同于给定的EJV查询结果坐标的点
        :param nodes:
        :param aim_node:
        :return:
        """
        if len(nodes) != 2:
            return None
        out = None
        for node in nodes:
            loc = [node.LAT, node.LON]
            if loc != [aim_node.LATITUDE, aim_node.LONGITUDE]:
                out = node
        return out


def load_config():
    config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r'))
    return config


class ObjUtils:
    @staticmethod
    def save_obj(save_obj: object, save_path: str,save_name:str):
        with open(os.path.join(save_path, f"{save_name}.pkl"), 'wb') as _:
            LogUtils.info(f"SAVE obj:{save_name}.pkl to %s" % save_path)
            pickle.dump(save_obj, _)

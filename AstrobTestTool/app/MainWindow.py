import os.path

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow

from AstrobTestTool.app.Device import DevicesManager
from AstrobTestTool.app.Utils import ConfigManager, LogManager
from AstrobTestTool.ui.MainWindowUI import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |  # 使能最小化按钮
                            Qt.WindowCloseButtonHint |  # 使能关闭按钮
                            Qt.WindowStaysOnTopHint)  # 窗体总在最前端
        self.setupUi(self)
        # self.setWindowIcon(QtGui.QIcon("htek.ico")) # 设置图标
        # 读取配置文件
        self.config_manager = ConfigManager(os.path.join(os.path.dirname(__file__), 'config.yml'))
        LogManager.debug('Read config:%s' % self.config_manager.config)
        # 根据配置文件配置box
        self.devices_manager = DevicesManager()
        # 获取devices列表，并配置box
        self.devices_list = self.devices_manager.devices_list
        # 绑定按键回调


        # 设置信号槽，锁案件，写信息，写log

    def closeEvent(self, event) -> None:
        from sys import exit
        exit(0)

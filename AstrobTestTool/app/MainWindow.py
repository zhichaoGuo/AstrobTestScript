import os.path

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QMainWindow

from AstrobTestTool.app.Device import DevicesManager, DeviceThread
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
        self.f_btn_refresh_devices()
        #
        self.device_thread = None
        # 绑定按键回调
        self.btn_refresh.clicked.connect(lambda: self.f_btn_refresh_devices())
        self.btn_connect_device.clicked.connect(lambda: self.f_btn_connect_devices())
        # 设置信号槽，锁按键，写信息，写log

    def closeEvent(self, event) -> None:
        from sys import exit
        exit(0)

    @Slot(str)
    def update_device_info(self, info):
        # 将label更新为接收到的信号，即更新后的内容
        self.label_devices_info.setText(info)

    @Slot(list)
    def update_devices_list(self, devices_list: list):
        self.box_devices.addItems(devices_list)

    @Slot(bool)
    def device_online_status(self, status: bool):
        """
        设备在线状态的槽函数负责再设备离线时控制界面状态
        """
        # todo
        self.lock_device_button(status)

    def lock_device_button(self, lock_status: bool):
        self.box_display_id.setEditable(lock_status)
        self.box_screencap_save_path.setEditable(lock_status)
        self.box_log_level.setEditable(lock_status)
        self.btn_screencap.setEnabled(lock_status)
        self.btn_screencap_clear_file.setEnabled(lock_status)
        self.btn_record_start.setEnabled(lock_status)
        self.btn_record_output.setEnabled(lock_status)

    def f_btn_refresh_devices(self):
        self.box_devices.addItems(self.devices_manager.devices_list)

    def f_btn_connect_devices(self):
        self.device_thread = DeviceThread(self.devices_manager, self.box_devices.currentText())
        self.device_thread.start()

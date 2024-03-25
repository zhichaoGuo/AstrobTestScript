import os.path
import time
from threading import Thread

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QMainWindow

from AstrobTestTool.app.Device import DevicesManager, DeviceThread
from AstrobTestTool.app.Utils import ConfigManager, LogManager, get_save_path
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
        self.box_screencap_save_path.addItems(self.config_manager.config['screen_cap']['save_path'])
        self.box_log_save_path.addItems(self.config_manager.config['logcat']['save_path'])
        self.f_btn_refresh_devices()
        self.all_button_status(False)
        # 设备心跳线程，在连接设备后创建线程
        self.device_thread = None
        self.device = None
        # 绑定按键回调
        self.btn_connect_device_status = True  # 设备未连接时Ture，设备链接时为False
        self.btn_refresh.clicked.connect(lambda: self.f_btn_refresh_devices())
        self.btn_connect_device.clicked.connect(lambda: self.f_btn_connect_devices())
        self.btn_screencap.clicked.connect(lambda: self.f_btn_screen_cap())
        # 设置信号槽，锁按键，写信息，写log

    def closeEvent(self, event) -> None:
        if self.device_thread:
            self.device_thread.running_status = False
            self.device_thread.wait()  # 防止线程异常退出
        from sys import exit
        exit(0)

    @Slot(str)
    def update_device_info(self, info):
        # 将label更新为接收到的信号，即更新后的内容
        self.label_devices_info.setText(info)

    @Slot(list)
    def update_devices_list(self, devices_list: list):
        self.box_devices.clear()
        self.box_devices.addItems(devices_list)

    @Slot(bool)
    def device_online_status(self, status: bool):
        """
        设备在线状态的槽函数负责再设备离线时控制界面状态
        """
        self.all_button_status(status)
        self.btn_connect_device_status = not status
        self.btn_refresh.setEnabled(self.btn_connect_device_status)
        self.box_devices.setEnabled(self.btn_connect_device_status)
        if self.btn_connect_device_status:
            # 此时为断开连接，需要等待心跳线程退出
            btn_text = '连接设备'
            self.device_thread.wait()  # 防止线程异常退出
            self.device_thread = None
            self.devices_manager.close_device()
            self.device = None
            self.f_btn_refresh_devices()
            self.update_devices_display_id([])
        else:
            btn_text = '断开设备'
        self.btn_connect_device.setText(btn_text)

    @Slot(list)
    def update_devices_display_id(self, display_id_list: list):
        self.box_display_id.clear()
        self.box_display_id.addItems(display_id_list)

    @Slot(object)
    def set_device(self, device):
        self.device = device

    def all_button_status(self, status: bool):
        self.box_display_id.setEnabled(status)
        self.box_screencap_save_path.setEnabled(status)
        self.box_log_level.setEnabled(status)
        self.box_log_save_path.setEnabled(status)
        self.btn_screencap.setEnabled(status)
        self.btn_screencap_clear_file.setEnabled(status)
        self.btn_record_start.setEnabled(status)
        self.btn_record_output.setEnabled(status)
        self.btn_log_clear.setEnabled(status)
        self.btn_log_start.setEnabled(status)
        self.btn_log_output.setEnabled(status)
        self.btn_log_clear_file.setEnabled(status)

    def f_btn_refresh_devices(self):
        self.update_devices_list(self.devices_manager.devices_serial_list)

    def f_btn_connect_devices(self):
        """
        点击连接设备按钮，通过self.btn_connect_device_status判断此时是连接还是断开
        在ui线程不执行逻辑，在设备心跳线程中根据实际状况通过信号改变ui线程的状态
        """
        if self.btn_connect_device_status:
            if self.box_devices.currentText():
                self.device = self.devices_manager.get_device(self.box_devices.currentText())
                self.device_thread = DeviceThread(self.devices_manager, self.box_devices.currentText())
                self.device_thread.signal_alive.connect(self.device_online_status)
                self.device_thread.signal_display_id.connect(self.update_devices_display_id)
                self.device_thread.signal_device_info.connect(self.update_device_info)
                self.device_thread.start()
            else:
                self.update_device_info('当前未选择设备')
        else:
            # 此时也不改变状态，而是通过心跳线程的信号来改变ui线程的状态
            self.device_thread.running_status = False

    def f_btn_screen_cap(self):
        file_path = get_save_path(self, 'png')
        display_id = self.box_display_id.currentText()
        if not display_id:
            self.update_device_info('未选中屏幕id')
            return None
        if file_path:
            # 起新线程下载syslog
            thread = Thread(target=self.device.screen_cap,
                            args=[self.box_screencap_save_path.currentText(), 'testtool.png', file_path, display_id, ])
            # 设置成守护线程
            thread.setDaemon(True)
            # 启动线程
            thread.start()
            self.update_device_info('保存截图成功')
        else:
            self.update_device_info('')

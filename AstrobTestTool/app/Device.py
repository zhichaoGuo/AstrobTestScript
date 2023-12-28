import os.path
import time

import usb1
from PySide2.QtCore import QThread, Signal
from adb_shell.adb_device import AdbDevice, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from AstrobTestTool.app.Utils import LogManager


class DevicesManager:
    adb_key_save_path = os.path.join(os.path.dirname(__file__), 'config', 'adbKey')

    @property
    def devices_list(self):
        from adb_shell.adb_device import UsbTransport

        devices = UsbTransport.USB1_CTX.getDeviceIterator(skip_on_error=True)
        # 遍历列表，调用每个AdbDevice对象的get_serial方法，返回设备的serial
        devices_list = []
        for device in devices:
            try:
                device_serial = device.getSerialNumber()
                if device_serial:
                    devices_list.append(device_serial)
            except usb1.USBErrorNotSupported as err:
                LogManager.debug('get_devices error:%s' % err)
            except usb1.USBErrorAccess as err:
                LogManager.debug('get_devices error:%s' % err)
                LogManager.warning('请检查是否存在命令窗口已运行adb，请在命令窗口执行adb kill-server')
        return devices_list

    @staticmethod
    def get_device(uuid: str):
        if uuid in DevicesManager.devices_list:
            with open(DevicesManager.adb_key_save_path) as f:
                priv = f.read()
            with open(DevicesManager.adb_key_save_path + '.pub') as f:
                pub = f.read()
            signer = PythonRSASigner(pub, priv)
            # 创建一个AdbDeviceUsb对象
            device = Device(serial=uuid)
            # 连接设备
            device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
            return device
        else:
            LogManager.warning('device:%s ,is not in devices list:%s' % (uuid, DevicesManager.devices_list))
            return None

    @staticmethod
    def gen_key():
        from adb_shell.auth.keygen import keygen
        keygen(DevicesManager.adb_key_save_path)

    def check_device_alive(self, uuid: str):
        return uuid in self.devices_list


class Device(AdbDeviceUsb):
    def __init__(self, serial):
        super().__init__(serial)

    def screen_cap(self, tmp_dir: str, tmp_name: str):
        self.shell(f'screencap {tmp_dir}/{tmp_name}')

    def pull_screen_cap(self, tmp_dir: str, tmp_name: str, local_dir: str, local_name: str):
        self.pull(f'{tmp_dir}/{tmp_name}', f'{local_dir}/{local_name}', LogManager.pull_log)


class DeviceThread(QThread):
    # 声明一个自定义信号
    # 信号是一个int变量
    signal = Signal(bool)

    def __init__(self, manager: DevicesManager,device_uuid:str):
        super().__init__()
        self.running_status = True
        self.manager = manager
        self.device_uuid = device_uuid

    def run(self):
        LogManager.info('Device Thread is running!')
        while self.running_status:
            if self.manager.check_device_alive(self.device_uuid):
                time.sleep(1)
            else:
                self.signal.emit(False)
                self.running_status = False
        LogManager.info('Device Thread is over!')

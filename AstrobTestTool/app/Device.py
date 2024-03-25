import os.path
import time

import usb1
from PySide2.QtCore import QThread, Signal
from adb_shell.adb_device import AdbDevice, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from AstrobTestTool.app.Utils import LogManager, get_save_path

from adb_shell.adb_device import UsbTransport


class DevicesManager:
    adb_key_save_path = os.path.join(os.path.dirname(__file__), 'config', 'adbKey')
    USB_CTX = usb1.USBContext()
    USB_CTX.open()

    def __init__(self):
        self.device = None  # 存连接的 Device类
        self.device_usb_obj = None  # 存连接的 UsbObject

    @property
    def devices_list(self):

        devices = self.USB_CTX.getDeviceIterator(skip_on_error=True)
        devices_list = []
        for device in devices:
            devices_list.append(device)
        return devices_list

    @property
    def devices_serial_dict(self):
        # 遍历列表，调用每个AdbDevice对象的get_serial方法，返回设备的serial
        devices_dict = {}
        for device in self.devices_list:
            try:
                device_serial = device.getSerialNumber()
                if device_serial:
                    devices_dict[device_serial] = device
            except usb1.USBErrorNotSupported as err:
                LogManager.debug('get_devices error:%s' % err)
            except usb1.USBErrorAccess as err:
                LogManager.debug('get_devices error:%s' % err)
                LogManager.warning('请检查是否存在命令窗口已运行adb，请在命令窗口执行adb kill-server')
        return devices_dict

    @property
    def devices_serial_list(self):
        return self.devices_serial_dict.keys()

    def get_device(self, uuid: str):
        if self.device:
            return self.device
        else:
            dev_list = self.devices_serial_list
            if uuid in dev_list:
                with open(DevicesManager.adb_key_save_path) as f:
                    priv = f.read()
                with open(DevicesManager.adb_key_save_path + '.pub') as f:
                    pub = f.read()
                signer = PythonRSASigner(pub, priv)
                # 创建一个AdbDeviceUsb对象
                self.device_usb_obj = self.devices_serial_dict[uuid]
                self.device = Device(serial=uuid)
                # 连接设备
                self.device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
                return self.device
            else:
                LogManager.warning('device:%s ,is not in devices list:%s' % (uuid, dev_list))
                return None

    @staticmethod
    def gen_key():
        from adb_shell.auth.keygen import keygen
        keygen(DevicesManager.adb_key_save_path)

    def check_device_alive(self):
        if not self.device:
            LogManager.warning('Check device alive but do not have device yet.')
            return False
        else:
            return self.device_usb_obj in self.devices_list

    def close_device(self):
        if self.device:
            self.device.close()
            self.device = None
            self.device_usb_obj = None
            return True
        else:
            LogManager.warning('Close device but do not have device yet.')
            return False


class Device(AdbDeviceUsb):
    signal_device_info = Signal(str)

    def __init__(self, serial):
        super().__init__(serial)

    def shell(self, command, transport_timeout_s=None, read_timeout_s=None, timeout_s=None, decode=True):
        LogManager.debug('shell cmd:%s' % command)
        return super().shell(command)

    @property
    def display_id(self):
        res = self.shell(f'dumpsys window displays | grep "Display: mDisplayId="')
        id_list = []
        for i in res.strip().split('\n'):
            cur_id = i.strip().split('=')[1]
            if cur_id.isdigit():
                id_list.append(cur_id)
            else:
                id_list.append(cur_id.split(' ')[0])
        return id_list

    def screen_cap(self, tmp_dir: str, tmp_name: str, local_file_path: str, display_id: str):
        # self.root()
        self.shell(f'screencap -d {display_id} {tmp_dir}/{tmp_name}')
        self.pull_screen_cap(tmp_dir, tmp_name, os.path.dirname(local_file_path), os.path.basename(local_file_path))



    def pull_screen_cap(self, tmp_dir: str, tmp_name: str, local_dir: str, local_name: str):
        self.pull(f'{tmp_dir}/{tmp_name}', f'{local_dir}/{local_name}', LogManager.pull_log)


class DeviceThread(QThread):
    # 声明一个自定义信号
    # 信号是一个int变量
    signal_alive = Signal(bool)
    signal_display_id = Signal(list)
    signal_device_info = Signal(str)

    def __init__(self, manager: DevicesManager, device_uuid: str):
        super().__init__()
        self.running_status = True
        self.signal_alive_send_flag = False
        self.manager = manager
        self.device_uuid = device_uuid
        self.devices_list = []

    def run(self):
        device = True
        # print(device)
        if device:
            # self.signal_set_device.emit(self.manager.get_device(self.device_uuid))
            self.signal_display_id.emit(self.manager.get_device(self.device_uuid).display_id)
            LogManager.info('Device Thread is running!')
            while self.running_status:
                if self.manager.check_device_alive():
                    if not self.signal_alive_send_flag:
                        self.signal_alive.emit(True)
                        self.signal_alive_send_flag = True
                    time.sleep(1)
                else:
                    self.running_status = False
            self.signal_alive.emit(False)
            LogManager.info('Device Thread is over!')
        else:
            self.signal_device_info.emit('无法连接到设备，查看log以了解更多')

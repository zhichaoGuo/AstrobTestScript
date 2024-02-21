import os
import shutil
import time

from Utils import LogUtils


def main(sql_db_name: str):
    # make case dir
    time_now = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
    work_dir = os.path.join(".", f"{sql_db_name}_{time_now}")
    if not os.path.exists(os.path.join(".", work_dir)):
        os.mkdir(os.path.join(".", work_dir))
        LogUtils.info("Mkdir: %s" % work_dir)

    shutil.copy(os.path.join(".", "QueryDataCase.log"), f"./{work_dir}")
    # LogUtils.logger.removeHandler(LogUtils.file_handler)
    os.remove(os.path.join(".", "QueryDataCase.log"))
    # shutil.move(os.path.join(".", "QueryDataCase.log"), f"./{work_dir}")


if __name__ == '__main__':
    main('Test_db')

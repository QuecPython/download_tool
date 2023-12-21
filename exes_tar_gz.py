import os
import zipfile

cmd = "tar -zcvf "
cmd1 = "tar -zxvf "
PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

# 打包exes目录下的各平台烧录工具
for i in os.listdir(PROJECT_ABSOLUTE_PATH + "\\exes\\"):
    os.chdir(PROJECT_ABSOLUTE_PATH + "\\exes\\")
    print(os.system(cmd + i + ".tar.gz " + i))


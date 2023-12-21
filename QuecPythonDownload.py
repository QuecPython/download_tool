import sys
import serial
import time
import os
import tempfile
import zipfile
import codecs
import json
import shutil
import configparser
import threading
import subprocess


# some software vars
if hasattr(sys, '_MEIPASS'):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
# download process
TIMEMONITOR = 0

class QuecPyDownloadError(Exception):
    pass


class runCommand(threading.Thread):
    def __init__(self, cmd, end_string, cwd):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.string = end_string
        self.cwd = cwd
        self.start()

    def run(self):
        global TIMEMONITOR
        print("real CMD: " + " ".join(self.cmd))
        if self.string == "Downloading...":
            p = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            i = 1
            for line in p.stdout:
                # print(line.decode(encoding='utf-8', errors='ignore'))
                if self.string in line.decode(encoding='utf-8', errors='ignore'):
                    TIMEMONITOR = i*10
                    print("updateProgress : \033[32m{}%\033[0m".format(str(TIMEMONITOR)))
                    i += 1
                if "DownLoad Passed" in line.decode(encoding='utf-8', errors='ignore'):
                    TIMEMONITOR = 100
                    print("updateProgress : \033[32m{}%\033[0m".format(str(TIMEMONITOR)))
                    p = subprocess.Popen(r'taskkill /F /IM ResearchDownload.exe',shell = True)
                if "[ERROR] DownLoad Failed" in line.decode(encoding='utf-8', errors='ignore'):
                    print("updateProgress : \033[31m=======Failed=======\033[0m")
        elif self.string == "[1]Upgrade:":
            p = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if self.string in line_decode:
                    TIMEMONITOR = line_decode.replace(self.string, '').strip()[:-1]
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                    if '[1]Upgrade: 100%' in line_decode:
                        TIMEMONITOR = 100
                        p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                        print("updateProgress : \033[32m{}%\033[0m".format(str(TIMEMONITOR)))
        elif self.string == "[1]DL-":
            p = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            i = 0
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if self.string in line_decode:
                    TIMEMONITOR = str(i)
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                    i += 2
                if '[1]Total upgrade time is' in line_decode:
                    # p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                    TIMEMONITOR = '100'
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                    p = subprocess.Popen(r'taskkill /F /IM QMulti_DL_CMD_V2.1.exe',shell = True)
        elif self.string == 'Add an WTPTP device: Device 1':
            p = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "Successfully to prepare temp folder file for wtptp download" in line_decode:
                    print("please restart")
                if "please plug in USB device ...." in line_decode:
                    for i in range(10):
                        TIMEMONITOR = str(i*10)
                        print("updateProgress : \033[32m{}%\033[0m".format(str(i*10)))
                        time.sleep(5)
                if "Device 1:Download Completed successfully" in line_decode:
                    TIMEMONITOR = 100
                    print("updateProgress : \033[32m{}%\033[0m".format(str(TIMEMONITOR)))
                    p = subprocess.Popen(r'taskkill /F /IM ResearchDownload.exe',shell = True)
        elif self.string == 'Device':
            p = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                try:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    if self.string in line_decode:
                        info = json.loads(line_decode)
                        Status = info.get("Status")
                        if Status == "Programming":
                            TIMEMONITOR = info.get("Progress")
                            print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                        elif Status == "Fail":
                            print("updateProgress : \033[31m=======Failed=======\033[0m")
                except Exception as e:
                    print("e: ", e)
        elif self.string == 'Eigen':
            TIMEMONITOR = 0
            # # pkg2img
            # cmd0 = ' '.join(self.cmd[:2] + ["pkg2img"])
            # print("---------- pkg2img ----------")
            # print(cmd0)
            # p = subprocess.Popen(cmd0, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # for line in p.stdout:
            #     line_decode = line.decode(encoding='utf-8', errors='ignore')
            #     print(line_decode)

            # process += 1
            # ql.set_value("timeMonitor", str(process))
            # ql.get_value('pub').sendMessage('updateProgress', arg1=str(process))

            config = configparser.ConfigParser(interpolation=None)
            config.read(self.cwd + "\\" + [i for i in os.listdir(self.cwd) if i not in ("platform_config.json", self.string)][0] + "\\quec_download_config.ini")

            # check connect
            cmd1 = ' '.join(self.cmd[:3] + ["probe"])
            p = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "RtsConditionAssign" in line_decode:
                    TIMEMONITOR += 1
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # flash pkg2img
            cmd0 = ' '.join(self.cmd[:2] + ["pkg2img"])
            print("---------- pkg2img ----------")
            print(cmd0)
            p = subprocess.Popen(cmd0, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                print(line_decode)

            TIMEMONITOR += 1
            print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # 
            cmd2 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["burn"])
            print("---------- Burn firmware ----------")
            print(cmd2)
            p = subprocess.Popen(cmd2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    print(line_decode)
                    TIMEMONITOR += 1
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # download ap_application.bin
            cmd3_2 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["flasherase"] + [config.get('File_1', 'START_ADDR') + config.get('File_1', 'MAX_SIZE')])
            print("---------- Download ap_application.bin flasherase ----------")
            print(cmd3_2)
            p = subprocess.Popen(cmd3_2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')

            cmd3_2 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["burnone flexfile2"])
            print("---------- Download ap_application.bin burnone ----------")
            print(cmd3_2)
            p = subprocess.Popen(cmd3_2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    TIMEMONITOR += 1
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # download ap_updater.bin
            cmd3_3 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["flasherase"] + [config.get('File_2', 'START_ADDR') + config.get('File_2', 'MAX_SIZE')])
            print("---------- Download ap_updater.bin flasherase ----------")
            print(cmd3_3)
            p = subprocess.Popen(cmd3_3, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                print(line_decode)

            cmd3_3 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["burnone flexfile3"])
            print("---------- Download ap_updater.bin burnone ----------")
            print(cmd3_3)
            p = subprocess.Popen(cmd3_3, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    print(line_decode)
                    TIMEMONITOR += 1
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # download customer_fs.bin
            cmd3_4 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["flasherase"] + [config.get('File_3', 'START_ADDR') + config.get('File_3', 'START_ADDR')])
            print("---------- Download customer_fs.bin flasherase ----------")
            print(cmd3_4)
            p = subprocess.Popen(cmd3_4, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                print(line_decode)

            cmd3_4 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["burnone flexfile4"])
            print("---------- Download customer_fs.bin burnone ----------")
            print(cmd3_4)
            p = subprocess.Popen(cmd3_4, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    print(line_decode)
                    TIMEMONITOR += 1
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                    
            if config.get('File', 'File_Count') == 4:
                # download customer_backup_fs.bin 
                cmd3_5 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["flasherase"] + [config.get('File_4', 'START_ADDR') + config.get('File_4', 'START_ADDR')])
                print("---------- Download customer_backup_fs.bin flasherase ----------")
                print(cmd3_5)
                p = subprocess.Popen(cmd3_5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    print(line_decode)

                cmd3_5 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["burnone flexfile5"])
                print("---------- Download customer_backup_fs.bin burnone ----------")
                print(cmd3_5)
                p = subprocess.Popen(cmd3_5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    if "files transferred" in line_decode:
                        print(line_decode)
                        TIMEMONITOR += 1
                        print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))

            # reset module
            cmd5 = ' '.join([self.cmd[0]] + ["--skipconnect 1"] + self.cmd[1:3] + ["sysreset"])
            print("---------- sysreset ----------")
            print(cmd5)
            p = subprocess.Popen(cmd5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                print(line_decode)
            print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
        elif self.string == 'FC41D':
            TIMEMONITOR = 0
            cmd1 = ' '.join(self.cmd)
            print("---------- Burn FC41D firmware ----------")
            print(cmd1)
            p = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                print(line_decode)
                if "Getting Bus" in line_decode:
                    print("please restart")
                if "Unprotected Flash" in line_decode:
                    TIMEMONITOR = 5
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                if "Begin EraseFlash" in line_decode:
                    TIMEMONITOR = 10
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                if "EraseFlash ->pass" in line_decode:
                    TIMEMONITOR = 30
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                if "Begin WriteFlash" in line_decode:
                    for i in range(15):
                        time.sleep(1)
                        TIMEMONITOR += 4
                        print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                if "Finished Successfully" in line_decode:
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
        else:
            p = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                print(line.decode(encoding='utf-8', errors='ignore'))
                line = line.decode(encoding='utf-8', errors='replace' if sys.version_info < (3, 5) else 'backslashreplace').rstrip()
                if self.string in line:
                    TIMEMONITOR = line[line.find(self.string)+len(self.string):-1]
                    print("updateProgress : \033[32m{}%\033[0m".format(TIMEMONITOR))
                    if '"progress" : 100,' in line:
                        p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                        print("updateProgress : \033[32m{}%\033[0m".format(str(100)))
                        return


class QuecPyDownload(object):
    def __init__(self, device, baudrate=115200, file=""):
        self.device, self.baudrate, self.file_name = device, baudrate, file
        self.platform = None
        self.tmp_path = tempfile.mkdtemp()
        print('------------------ Start preparing to download package: ------------------')
        self.tmp_name = self.get_platform()
        self.firmware_handler()

    def get_platform(self):
        if isZip(self.file_name):
            unzipFile(self.file_name, self.tmp_path)
            if ifExist(self.tmp_path + "\\platform_config.json"):
                try:
                    data = readJSON(self.tmp_path + "\\platform_config.json")
                    self.platform = data["platform"].strip()
                    if self.platform.upper() in ["ASR", "ASR1601", "ASR1606"]:
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                        shutil.copyfile(PROJECT_ABSOLUTE_PATH + "\\exes\\aboot\\adownload.exe", self.tmp_path.replace("/","\\") + "\\adownload.exe")
                    elif self.platform.lower() in ["unisoc", "unisoc8910", "unisoc8850"]:
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                    elif self.platform.upper() == "RDA8908A":
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                    elif self.platform.upper() == "MDM9X05":
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0] + "\\firehose\\partition.mbn"
                    elif self.platform.upper() == "ASR1803S":
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0] + "\\Falcon_EVB_QSPI_Nor_LWG_Only_Nontrusted_PM802_LPDDR2.blf"
                    elif self.platform.upper() == "FCM360W":
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                    elif self.platform.upper() == "FC41D":
                        newFW = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                    elif self.platform.upper() == "EIGEN":
                        fdir = [i for i in os.listdir(self.tmp_path) if i != "platform_config.json"][0]
                        newFW = fdir + "\\at_command.binpkg"
                        self.eigen_config(fdir, newFW)
                    else:
                        return None
                    newFW = os.path.join(self.tmp_path, newFW)
                    if not ifExist(newFW):
                        return None
                except Exception as e:
                    print(e)
                    return None
            else:
                if ifExist(self.tmp_path + "\\system.img"):
                    self.platform = "ASR1601"
                    shutil.copyfile(self.file_name, self.tmp_path + "\\" + self.file_name.split("\\")[-1])
                    newFW = self.tmp_path + "\\" + self.file_name.split("\\")[-1]
                else:
                    return None
        else:
            if self.file_name[-3:].lower() == "pac":
                self.platform = "unisoc"
                self.config = configparser.ConfigParser(interpolation=None)
                self.config.read(PROJECT_ABSOLUTE_PATH + "\\exes\\rda\\ResearchDownload.ini")
                if self.config["Options"]["EraseAll"] != "0":
                    self.config["Options"]["EraseAll"] = "0"
                    with open(PROJECT_ABSOLUTE_PATH + "\\exes\\rda\\ResearchDownload.ini", 'w+') as configfile:
                        self.config.write(configfile)
                shutil.copyfile(self.file_name, self.tmp_path + "\\" + self.file_name.split("\\")[-1])
                newFW = self.tmp_path + "\\" + self.file_name.split("\\")[-1]
            elif self.file_name[-3:].lower() == "lod":
                self.platform = "RDA8908A"
                shutil.copyfile(self.file_name, self.tmp_path + "\\" + self.file_name.split("\\")[-1])
                newFW = self.tmp_path + "\\" + self.file_name.split("\\")[-1]
            elif self.file_name[-3:].lower() == "blf":
                self.platform = "ASR1803S"
                self.fdir = fatherDir(self.file_name)
                self.fdir_name = self.fdir.split("\\")[-1]
                shutil.copytree(self.fdir, self.tmp_path.replace("/", "\\") + "\\" + self.fdir_name)
                newFW = self.tmp_path + "\\" + self.fdir_name  + "\\" + self.file_name.split("\\")[-1]
            elif self.file_name[-3:].lower() == "mbn":
                self.platform = "MDM9X05"
                fdir1 = fatherDir(self.file_name)
                fdir1_name = fdir1.split("\\")[-1]
                fdir2 = fatherDir(fdir1)
                fdir2_name = fdir2.split("\\")[-1]
                shutil.copytree(fdir2, self.tmp_path.replace("/", "\\") + "\\" + fdir2_name)
                newFW = self.tmp_path + "\\" + fdir2_name + "\\" + fdir1_name + "\\" + self.file_name.split("\\")[-1]
            elif self.file_name[-6:].lower() == "binpkg":
                self.platform = "EIGEN"
                fdir = fatherDir(self.file_name)
                fdir_name = fdir.split("\\")[-1]
                shutil.copytree(fdir, self.tmp_path.replace("/", "\\") + "\\" + fdir_name)
                newFW = self.tmp_path + "\\" + fdir_name  + "\\" + self.file_name.split("\\")[-1]
                self.eigen_config(fdir_name, newFW)
            elif self.file_name[-3:].lower() == "bin":
                if self.file_name.upper().find("FCM360W") != -1:
                    self.platform = "FCM360W"
                    shutil.copyfile(self.file_name, self.tmp_path + "\\" + self.file_name.split("\\")[-1])
                    newFW = self.tmp_path + "\\" + self.file_name.split("\\")[-1]
                elif self.file_name.upper().find("FC41D") != -1:
                    self.platform = "FC41D"
                    shutil.copyfile(self.file_name, self.tmp_path + "\\" + self.file_name.split("\\")[-1])
                    newFW = self.tmp_path + "\\" + self.file_name.split("\\")[-1]
                else:
                    return None
            else:
                return None
        return newFW

    def eigen_config(self, fdir, fw_name):
        try:
            self.config = configparser.ConfigParser(interpolation=None)
            self.config.read(self.tmp_path + "\\" + fdir + "\\quec_download_config.ini")
            self.File_Count = int(self.config.get('File', 'File_Count'))

            ap_application_addr = self.config.get('File_1', 'START_ADDR')
            ap_application_max = self.config.get('File_1', 'MAX_SIZE')
            self.flexfile2 = ap_application_addr + " " + ap_application_max

            ap_updater_addr = self.config.get('File_2', 'START_ADDR')
            ap_updater_max = self.config.get('File_2', 'MAX_SIZE')
            self.flexfile3 = ap_updater_addr + " " + ap_updater_max

            customer_fs_addr = self.config.get('File_3', 'START_ADDR')
            customer_fs_max = self.config.get('File_3', 'MAX_SIZE')
            self.flexfile4 = customer_fs_addr + " " + customer_fs_max

            if self.File_Count == 4:
                customer_backup_fs_addr = self.config.get('File_4', 'START_ADDR')
                customer_backup_fs_max = self.config.get('File_4', 'MAX_SIZE')
                self.flexfile5 =  customer_backup_fs_addr + " " + customer_backup_fs_max

            self.binpkg_config = configparser.ConfigParser(interpolation=None)
            self.binpkg_config_ini = self.tmp_path.replace("/", "\\")+ "\\Eigen\\config.ini"
            self.binpkg_config.read(self.binpkg_config_ini)

            self.binpkg_config.set('package_info', 'arg_pkg_path_val', fw_name)
            self.binpkg_config.set('bootloader', 'blpath', self.tmp_path.replace("/", "\\") + "\\blloadskip = 0")
            self.binpkg_config.set('system', 'syspath', self.tmp_path.replace("/", "\\") + "\\sysloadskip = 0")
            self.binpkg_config.set('cp_system', 'cp_syspath', self.tmp_path.replace("/", "\\") + "\\cp_sysloadskip = 0")

            self.binpkg_config.set('flexfile2', 'filepath', self.tmp_path.replace("/", "\\") + fdir + "\\ap_application.bin")
            self.binpkg_config.set('flexfile2', 'burnaddr', ap_application_addr)
            self.binpkg_config.set('flexfile3', 'filepath', self.tmp_path.replace("/", "\\") + fdir + "\\ap_updater.bin")
            self.binpkg_config.set('flexfile3', 'burnaddr', ap_updater_addr)
            self.binpkg_config.set('flexfile4', 'filepath', self.tmp_path.replace("/", "\\") + fdir + "\\customer_fs.bin")
            self.binpkg_config.set('flexfile4', 'burnaddr', customer_fs_addr)
            if self.File_Count == 4:
                self.binpkg_config.set('flexfile5', 'filepath', self.tmp_path.replace("/", "\\") + fdir + "\\customer_backup_fs.bin")
                self.binpkg_config.set('flexfile5', 'burnaddr', customer_backup_fs_addr)
            else:
                self.binpkg_config.remove_section('flexfile5')
            
        except Exception as e:
            print(e)
            print('please check firmware file ~')
            return

    def firmware_handler(self):
        download_overtime = 45
        # into download mode
        if self.platform.upper() in ["ASR", "ASR1601", "ASR1606", "unisoc", "unisoc8910", "unisoc8850", "EIGEN"]:
            conn = serial.Serial(self.device, self.baudrate)
            conn.write(('at+qdownload=1\r\n').encode())
            conn.close()
            self.device = comPortNumber({"EC600SCNAA":"2C7C:6001",
										   "EC600SCNLB":"2C7C:6002",
										   "EC600UCNLB":"2C7C:0901",
										   "BC25": "10C4:EA70",
										   "EC800GCNGA": "2C7C:0904",
										   "Eigen": "17D1:0001"
										  })
        if self.platform.upper() in ["ASR", "ASR1601", "ASR1606"]:
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\aboot")
            shutil.copyfile(PROJECT_ABSOLUTE_PATH + "\\exes\\aboot\\adownload.exe", self.tmp_path.replace("/","\\") + "\\adownload.exe")
            cmd = [self.tmp_path.replace("/","\\") + "\\adownload.exe", '-p', self.device, '-a', '-q', '-r', '-s', self.baudrate, self.tmp_name]
            print('------------------ adownload downloading factory package: ------------------')
            downloadProcess = '"progress" :'
        elif self.platform.lower() in ["unisoc", "unisoc8910", "unisoc8850"]:
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\rda")
            shutil.copytree(PROJECT_ABSOLUTE_PATH + "\\exes\\rda\\", self.tmp_path.replace("/", "\\")+ "\\rda\\")
            cmd = [self.tmp_path.replace("/","\\") + "\\CmdDloader.exe", '-pac', self.tmp_name]
            print('------------------ unisoc downloading upgrade package: ------------------')
            download_overtime = 600
            downloadProcess = 'Downloading...'
        elif self.platform.upper() == "RDA8908A":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\NB")
            shutil.copytree(PROJECT_ABSOLUTE_PATH + "\\exes\\NB\\", self.tmp_path.replace("/", "\\")+ "\\NB\\")
            cmd = [self.tmp_path.replace("/", "\\")+ "\\NB\\QMulti_DL_CMD_V2.1.exe", self.device[3:], self.baudrate, self.tmp_name]
            print('------------------ NB downloading upgrade package: ------------------')
            downloadProcess = '[1]Upgrade:'
        elif self.platform.upper() == "ASR1803S":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\blf_tools")
            shutil.copyfile(PROJECT_ABSOLUTE_PATH + "\\exes\\blf_tools\\SWDConsole.exe", self.tmp_path.replace("/","\\") + "\\SWDConsole.exe")
            cmd = [self.tmp_path.replace("/","\\") + "\\SWDConsole.exe", '-f', self.tmp_name]
            print('------------------ 200A download downloading factory package(blf): ------------------')
            downloadProcess = 'Add an WTPTP device: Device 1'
        elif self.platform.upper() == "MDM9X05":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\NB")
            shutil.copytree(PROJECT_ABSOLUTE_PATH + "\\exes\\NB\\", self.tmp_path.replace("/", "\\")+ "\\NB\\")
            cmd = [self.tmp_path.replace("/", "\\")+ "\\NB\\QMulti_DL_CMD_V2.1.exe", self.device[3:], self.baudrate, self.tmp_name]
            self.tmp_path = self.tmp_path.replace("/", "\\")+ "\\NB"
            print('------------------ BG95 download downloading factory package(mbn): ------------------')
            downloadProcess = '[1]DL-'
        elif self.platform.upper() == "EIGEN":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\Eigen")
            shutil.copytree(PROJECT_ABSOLUTE_PATH + "\\exes\\Eigen\\", self.tmp_path.replace("/", "\\")+ "\\Eigen")
            self.binpkg_config.set('config', 'line_0_com', self.device)
            with open(self.binpkg_config_ini, "w+", encoding='utf-8') as f:
                self.binpkg_config.write(f)
            cmd = [self.tmp_path.replace("/", "\\") + "\\Eigen\\flashtoolcli1.exe", '--cfgfile '+ self.binpkg_config_ini, '--port="%s"'%self.device]
            print('------------------ Eigen downloading upgrade package(binpkg): ------------------')
            downloadProcess = 'Eigen'
        elif self.platform.upper() == "FCM360W":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\FCM360W")
            shutil.copyfile(PROJECT_ABSOLUTE_PATH + "\\exes\\FCM360W\\EswinFlashTool.exe", self.tmp_path.replace("/","\\") + "\\EswinFlashTool.exe")
            cmd = [self.tmp_path.replace("/","\\") + "\\EswinFlashTool.exe", '-p', self.device[3:], '-b', "921600", '-file', self.tmp_name]
            print('------------------ FCM360W downloading factory package: ------------------')
            downloadProcess = 'Device'
        elif self.platform.upper() == "FC41D":
            checkExeFile(PROJECT_ABSOLUTE_PATH + "\\exes\\FC41D")
            shutil.copytree(PROJECT_ABSOLUTE_PATH + "\\exes\\FC41D", self.tmp_path.replace("/","\\") + "\\FC41D")
            cmd = [self.tmp_path.replace("/","\\") + "\\FC41D\\bk_loader.exe", 'download', '-p', self.device[3:], '-b', "921600", '-i', self.tmp_name]
            print('------------------ FC41D downloading factory package: ------------------')
            downloadProcess = 'FC41D'
        print("------------------ All pre-download preparations are complete ------------------")
        self.download_handler(cmd, downloadProcess, download_overtime)

    def download_handler(self, cmd, downloadProcess, download_overtime):
        # Flash thread 
        p4 = runCommand(cmd, downloadProcess, self.tmp_path)
        # Monitor thread
        T = threading.Thread(target=self.downloadTimeMonitor, args=(download_overtime, ))
        T.start()

    def downloadTimeMonitor(self, out_time):
        global TIMEMONITOR
        tmp = TIMEMONITOR
        i = 0
        try:
            while True:
                if tmp == TIMEMONITOR:
                    i += 1
                else:
                    i = 0
                tmp = TIMEMONITOR
                time.sleep(1)
                if i > out_time:
                    if self.platform.upper() in ["ASR", "ASR1601", "ASR1606"]:
                        p = subprocess.Popen(r'taskkill /F /IM adownload.exe',shell = True)
                    elif self.platform.lower() in ["unisoc", "unisoc8910", "unisoc8850"]:
                        p = subprocess.Popen(r'taskkill /F /IM CmdDloader.exe',shell = True)
                    elif self.platform.upper() == "RDA8908A":
                        p = subprocess.Popen(r'taskkill /F /IM QMulti_DL_CMD_V2.1.exe',shell = True)
                    elif self.platform.upper() == "ASR1803S":
                        p = subprocess.Popen(r'taskkill /F /IM SWDConsole.exe',shell = True)
                    elif self.platform.upper() == "MDM9X05":
                        p = subprocess.Popen(r'taskkill /F /IM QMulti_DL_CMD_V2.1.exe',shell = True)
                    elif self.platform.upper() == "EIGEN":
                        p = subprocess.Popen(r'taskkill /F /IM flashtoolcli1.exe',shell = True)
                    elif self.platform.upper() == "FCM360W":
                        p = subprocess.Popen(r'taskkill /F /IM EswinFlashTool.exe',shell = True)
                    elif self.platform.upper() == "FC41D":
                        p = subprocess.Popen(r'taskkill /F /IM bk_loader.exe',shell = True)

                    break
                if int(TIMEMONITOR) in (99,100):
                    break
            TIMEMONITOR = 0
            time.sleep(1)
            shutil.rmtree(self.tmp_path)
        except:
            pass
        return


def comPortNumber(vid_pid, port=""):
		for p in list(serial.tools.list_ports.comports()):
			for i in vid_pid.values():
				if port == "":
					if i in p.hwid:
						return p.device
				else:
					if i and port in p.hwid:
						return p.device


def isZip(Path):
    return zipfile.is_zipfile(Path)


def unzipFile(src, dst):
    with zipfile.ZipFile(src, 'r') as zip_ref:
        zip_ref.extractall(dst)

def checkExeFile(Path):
    if ifExist(Path):
        pass
    elif ifExist(Path + ".tar.gz"):
        os.system("tar -zxf " + Path + ".tar.gz -C exes")
    else:
        os.system("tar -zxf " + Path + ".tar.gz -C exes > /dev/null")


def readJSON(jsonName):
    with codecs.open(jsonName, 'r', 'utf-8') as f:
        data = json.load(f)
    return data


def ifExist(Path):
    # Determine if a file/directory exists
    return os.path.exists(Path)


def fatherDir(Path):
    # Gets the directory where the current file is located, the parent directory
    return os.path.dirname(Path)


def main():
    import argparse
    cmd_parser = argparse.ArgumentParser(description="Download firmware on the QuecPython.")
    cmd_parser.add_argument(
        "-d",
        "--device",
        default=os.environ.get("QUECPYTHON_DEVICE", "COM24"),
        help="the serial device of the QuecPython Download",
    )
    cmd_parser.add_argument(
        "-b",
        "--baudrate",
        default=os.environ.get("QUECPYTHON_BAUDRATE", "115200"),
        help="the baud rate of the serial device",
    )
    cmd_parser.add_argument(
        "-f", 
        "--file", 
        default="firmware file",
        help="input QuecPython firmware file"
    )
    args = cmd_parser.parse_args()
    # print(args.device, args.baudrate, args.file)
    # open the connection to the qpyoard
    try:
        qpy = QuecPyDownload(args.device, args.baudrate, args.file)
    except QuecPyDownloadError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
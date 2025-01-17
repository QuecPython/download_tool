import sys
import os
import subprocess
import time
import json
import configparser
import shutil
import serial
import serial.tools.list_ports
import zipfile
import codecs

# exe temp path
EXE_ABSOLUTE_PATH = sys._MEIPASS if getattr(sys,'frozen',False) else False
# some software vars
if hasattr(sys, '_MEIPASS'):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.realpath(sys.executable))
else:
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
# download process
TIMEMONITOR = 0


app_config = {
    "EXE_ABSOLUTE_PATH": EXE_ABSOLUTE_PATH,
    "PROJECT_ABSOLUTE_PATH": PROJECT_ABSOLUTE_PATH,
    "log": False
}

QuecPyDownloadPort = {  "EC600SCNAA":"2ECC:3017",
                        "EC600SCNLB":"2ECC:3004",
                        "EC600UCNLB":"0525:A4A7",
                        "BC25": "10C4:EA70",
                        "EC800GCNGA": "1782:4D16"
                        }


class QuecPyDownloadError(Exception):
    pass


def QuecPythonOutput(loginfo):
    if app_config['log']:
        print(loginfo, flush=True)
    else:
        if loginfo.startswith("Progress :"):
            print(loginfo, flush=True)

def comPortNumber(vid_pid):
    for p in serial.tools.list_ports.comports():
        for i in vid_pid.values():
            if i in p.hwid:
                return p.device
                

def isZip(Path):
    return zipfile.is_zipfile(Path)


def unzipFile(src, dst):
    with zipfile.ZipFile(src, 'r') as zip_ref:
        zip_ref.extractall(dst)

def checkExeFile(Path, temp_path=""):
    if ifExist(Path):
        shutil.copytree(Path, temp_path)
        return
    elif ifExist(Path + ".tar.gz"):
        if EXE_ABSOLUTE_PATH:
            os.system("tar -zxf " + Path + ".tar.gz -C " + EXE_ABSOLUTE_PATH + "\\exes")
        else:
            os.system("tar -zxf " + Path + ".tar.gz -C " + PROJECT_ABSOLUTE_PATH + "\\exes")
            shutil.copytree(Path, temp_path)
            return


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

def run_command(cmd, dw_str, cwd):
    QuecPythonOutput(" ".join(cmd))
    if app_config['log']:
        p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            line_decode = line.decode(encoding='utf-8', errors='ignore')
            QuecPythonOutput(line_decode)
    else:
        if dw_str == "Downloading...":
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            i = 1
            for line in p.stdout:
                QuecPythonOutput(line.decode(encoding='utf-8', errors='ignore'))
                if dw_str in line.decode(encoding='utf-8', errors='ignore'):
                    TIMEMONITOR = i*10
                    QuecPythonOutput("Progress : {}%".format(str(TIMEMONITOR)))
                    i += 1
                if "DownLoad Passed" in line.decode(encoding='utf-8', errors='ignore'):
                    TIMEMONITOR = 100
                    QuecPythonOutput("Progress : {}%".format(str(TIMEMONITOR)))
                    p = subprocess.Popen(r'taskkill /F /IM CmdDloader.exe',shell = True)
                if "[ERROR] DownLoad Failed" in line.decode(encoding='utf-8', errors='ignore'):
                    QuecPythonOutput("Progress : \033[31m=======Failed=======")
        elif dw_str == "[1]Upgrade:":
            p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
                if dw_str in line_decode:
                    TIMEMONITOR = line_decode.replace(dw_str, '').strip()[:-1]
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                    if '[1]Upgrade: 100%' in line_decode:
                        TIMEMONITOR = 100
                        p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                        QuecPythonOutput("Progress : {}%".format(str(TIMEMONITOR)))
        elif dw_str == "[1]DL-":
            p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            i = 0
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
                if dw_str in line_decode:
                    TIMEMONITOR = str(i)
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                    i += 2
                if '[1]Total upgrade time is' in line_decode:
                    # p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                    TIMEMONITOR = '100'
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                    p = subprocess.Popen(r'taskkill /F /IM QMulti_DL_CMD_V2.1.exe',shell = True)
        elif dw_str == 'Add an WTPTP device: Device 1':
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
                if "Successfully to prepare temp folder file for wtptp download" in line_decode:
                    QuecPythonOutput("please restart")
                if "please plug in USB device ...." in line_decode:
                    for i in range(10):
                        TIMEMONITOR = str(i*10)
                        QuecPythonOutput("Progress : {}%".format(str(i*10)))
                        time.sleep(5)
                if "Device 1:Download Completed successfully" in line_decode:
                    TIMEMONITOR = 100
                    QuecPythonOutput("Progress : {}%".format(str(TIMEMONITOR)))
                    p = subprocess.Popen(r'taskkill /F /IM ResearchDownload.exe',shell = True)
        elif dw_str == 'Device':
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                try:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    QuecPythonOutput(line_decode)
                    if dw_str in line_decode:
                        info = json.loads(line_decode)
                        Status = info.get("Status")
                        if Status == "Programming":
                            TIMEMONITOR = info.get("Progress")
                            QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                        elif Status == "Fail":
                            QuecPythonOutput("Progress : \033[31m=======Failed=======")
                except Exception as e:
                    QuecPythonOutput("e: ", e)
        elif dw_str == 'Eigen':
            TIMEMONITOR = 0
            # # pkg2img
            # cmd0 = ' '.join(cmd[:2] + ["pkg2img"])
            # QuecPythonOutput(" pkg2img ")
            # QuecPythonOutput(cmd0)
            # p = subprocess.Popen(cmd0, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # for line in p.stdout:
            #     line_decode = line.decode(encoding='utf-8', errors='ignore')
            #     QuecPythonOutput(line_decode)

            # process += 1
            # ql.set_value("timeMonitor", str(process))
            # ql.get_value('pub').sendMessage('Progress', arg1=str(process))

            config = configparser.ConfigParser(interpolation=None)
            config.read(cwd + "\\" + [i for i in os.listdir(cwd) if i not in ("platform_config.json", dw_str)][0] + "\\quec_download_config.ini")

            # check connect
            cmd1 = ' '.join(cmd[:3] + ["probe"])
            p = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
                if "RtsConditionAssign" in line_decode:
                    TIMEMONITOR += 1
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # flash pkg2img
            cmd0 = ' '.join(cmd[:2] + ["pkg2img"])
            QuecPythonOutput(" pkg2img ")
            QuecPythonOutput(cmd0)
            p = subprocess.Popen(cmd0, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)

            TIMEMONITOR += 1
            QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # 
            cmd2 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["burn"])
            QuecPythonOutput(" Burn firmware ")
            QuecPythonOutput(cmd2)
            p = subprocess.Popen(cmd2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    QuecPythonOutput(line_decode)
                    TIMEMONITOR += 1
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # download ap_application.bin
            cmd3_2 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["flasherase"] + [config.get('File_1', 'START_ADDR') + config.get('File_1', 'MAX_SIZE')])
            QuecPythonOutput(" Download ap_application.bin flasherase ")
            QuecPythonOutput(cmd3_2)
            p = subprocess.Popen(cmd3_2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')

            cmd3_2 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["burnone flexfile2"])
            QuecPythonOutput(" Download ap_application.bin burnone ")
            QuecPythonOutput(cmd3_2)
            p = subprocess.Popen(cmd3_2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    TIMEMONITOR += 1
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # download ap_updater.bin
            cmd3_3 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["flasherase"] + [config.get('File_2', 'START_ADDR') + config.get('File_2', 'MAX_SIZE')])
            QuecPythonOutput(" Download ap_updater.bin flasherase ")
            QuecPythonOutput(cmd3_3)
            p = subprocess.Popen(cmd3_3, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)

            cmd3_3 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["burnone flexfile3"])
            QuecPythonOutput(" Download ap_updater.bin burnone ")
            QuecPythonOutput(cmd3_3)
            p = subprocess.Popen(cmd3_3, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    QuecPythonOutput(line_decode)
                    TIMEMONITOR += 1
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # download customer_fs.bin
            cmd3_4 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["flasherase"] + [config.get('File_3', 'START_ADDR') + config.get('File_3', 'START_ADDR')])
            QuecPythonOutput(" Download customer_fs.bin flasherase ")
            QuecPythonOutput(cmd3_4)
            p = subprocess.Popen(cmd3_4, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)

            cmd3_4 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["burnone flexfile4"])
            QuecPythonOutput(" Download customer_fs.bin burnone ")
            QuecPythonOutput(cmd3_4)
            p = subprocess.Popen(cmd3_4, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                if "files transferred" in line_decode:
                    QuecPythonOutput(line_decode)
                    TIMEMONITOR += 1
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                    
            if config.get('File', 'File_Count') == 4:
                # download customer_backup_fs.bin 
                cmd3_5 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["flasherase"] + [config.get('File_4', 'START_ADDR') + config.get('File_4', 'START_ADDR')])
                QuecPythonOutput(" Download customer_backup_fs.bin flasherase ")
                QuecPythonOutput(cmd3_5)
                p = subprocess.Popen(cmd3_5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    QuecPythonOutput(line_decode)

                cmd3_5 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["burnone flexfile5"])
                QuecPythonOutput(" Download customer_backup_fs.bin burnone ")
                QuecPythonOutput(cmd3_5)
                p = subprocess.Popen(cmd3_5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout:
                    line_decode = line.decode(encoding='utf-8', errors='ignore')
                    if "files transferred" in line_decode:
                        QuecPythonOutput(line_decode)
                        TIMEMONITOR += 1
                        QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))

            # reset module
            cmd5 = ' '.join([cmd[0]] + ["skipconnect 1"] + cmd[1:3] + ["sysreset"])
            QuecPythonOutput(" sysreset ")
            QuecPythonOutput(cmd5)
            p = subprocess.Popen(cmd5, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
            QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
        elif dw_str == 'FC41D':
            TIMEMONITOR = 0
            cmd1 = ' '.join(cmd)
            QuecPythonOutput(" Burn FC41D firmware ")
            QuecPythonOutput(cmd1)
            p = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                line_decode = line.decode(encoding='utf-8', errors='ignore')
                QuecPythonOutput(line_decode)
                if "Getting Bus" in line_decode:
                    QuecPythonOutput("please restart")
                if "Unprotected Flash" in line_decode:
                    TIMEMONITOR = 5
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                if "Begin EraseFlash" in line_decode:
                    TIMEMONITOR = 10
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                if "EraseFlash ->pass" in line_decode:
                    TIMEMONITOR = 30
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                if "Begin WriteFlash" in line_decode:
                    for i in range(15):
                        time.sleep(1)
                        TIMEMONITOR += 4
                        QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                if "Finished Successfully" in line_decode:
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
        else:  # if dw_str / downloadProcess is progress or another value
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                QuecPythonOutput(line.decode(encoding='utf-8', errors='ignore'))
                line = line.decode(encoding='utf-8', errors='replace' if sys.version_info < (3, 5) else 'backslashreplace').rstrip()
                if dw_str in line:
                    TIMEMONITOR = line[line.find(dw_str)+len(dw_str):-1]
                    QuecPythonOutput("Progress : {}%".format(TIMEMONITOR))
                    
                    # when flasing is finished, kill task
                    if '"progress" : 100,' in line:
                        p = subprocess.Popen(r'taskkill /F /IM adownload.exe', shell=True)
                        QuecPythonOutput("Progress :  {}%".format(str(100)))
                        return

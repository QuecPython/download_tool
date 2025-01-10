# QuecPython Firmware Download Tool

[中文](README_ZH.MD) | English

## Overview

Integrate the firmware download component of QPYcom into a command-line tool.

Combine firmware download tools for different platforms into a dedicated QuecPython download tool, accessible via a unified command-line interface.

Support firmware in multiple file formats.

| platforms           | Firmware File Extensions | Does it require entering download mode | Command-line tool used  |
| -------------- | ------------ | -------------------- | ---------------------- |
| EC600U、EC200U | pac、bin     | no                   | CmdDloader.exe         |
| EC600N、EC600M | zip、bin     | yes                   | adownload.exe          |
| BG95           | mbn、bin     | no                   | QMulti_DL_CMD_V2.1.exe |
| EC800E、EC600E | binpkg、bin  | no                   | flashtoolcli1.exe      |
| FCM360W        | bin          | no                   | EswinFlashTool.exe     |
| BC25           | lod、bin     | no                   | QMulti_DL_CMD_V2.1.exe |
| EC200A         | blf、bin     | no                   | SWDConsole.exe         |
| FC41D          | bin          | no                   | bk_loader.exe          |

## Command-line 

```bash
QuecPythonDownload.exe -l -d com6 -b 115200 -f "firmware file name"
```

- -l: Enable raw tool burn log output. Used for debugging; this parameter can be omitted during normal use.
- -d: Device COM port. Use the burn port for burning, and the AT port for entering download mode.
- -b: Serial port baud rate.
- -f: Firmware package file name.


## Download Process

1.Distinguish the firmware download platform based on the firmware file extension. For .bin files, first extract them, and then use the son file in the extracted folder to identify the firmware platform.
2.Call the appropriate original factory command-line tool based on the firmware platform to enter download mode.
3.Parse the progress information returned by the different platform-specific download tools to obtain a unified download progress report.

## Compilation Process
(Provide details for the compilation process here.)

code folder

```
|-- QuecPythonDownload.py
|-- README.md
|-- exes
	|--aboot
	|--blf_tools
	|--Eigen
	|--FC41D
	|--FCM360W
	|--NB
	|--rda
```



Packaging Instructions to package, include QuecPythonDownload.py and all files in the dependent exes directory into a single executable file. The executable should run without relying on the environment.

How to Package Multiple Files and Folders Using PyInstaller
1. In the command line, enter:

```
pyi-makespec QuecPythonDownload.py  

```

This will generate a project configuration file. A new file, QuecPythonDownload.spec, will appear in the folder.

2. Open the QuecPythonDownload.spec file.

```python
   # -*- mode: python ; coding: utf-8 -*-
   
   
   block_cipher = None
   
   
   a = Analysis(
       ['QuecPythonDownload.py'],
       pathex=[],
       binaries=[],
       datas=[],
       hiddenimports=[],
       hookspath=[],
       hooksconfig={},
       runtime_hooks=[],
       excludes=[],
       win_no_prefer_redirects=False,
       win_private_assemblies=False,
       cipher=block_cipher,
       noarchive=False,
   )
   pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
   
   exe = EXE(
       pyz,
       a.scripts,
       [],
       exclude_binaries=True,
       name='QuecPythonDownload',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       console=True,
       disable_windowed_traceback=False,
       argv_emulation=False,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
   )
   coll = COLLECT(
       exe,
       a.binaries,
       a.zipfiles,
       a.datas,
       strip=False,
       upx=True,
       upx_exclude=[],
       name='QuecPythonDownload',
   )
   
```

3. Add all .py files to the first list element in a=Analysis(). If the files are in the same directory as QuecPythonDownload.py, simply use the file name. If they are located in a folder, include the relative path (or absolute path if preferred).

4. Place all non-.py files in the datas parameter of a=Analysis(). Each element in datas contains two parameters: the first is the path to the non-.py file, and the second is the folder name where the files will be stored. During packaging, the specified folder path will be used to locate and copy the required non-.py files.


```
    datas=[("C:\\****\\aboot.tar.gz", "exes")],
```

5. Finally, save the modified main.spec file. Similarly, enter the following command in the terminal: pyinstaller QuecPythonDownload.spec



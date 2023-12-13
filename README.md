# QuecPython固件下载工具

## 概述

整合QPYcom的固件下载部分为命令行工具

将不同平台的固件下载工具整合为QuecPython专用的下载工具，通过统一的命令行调用

支持多种文件格式的固件

| 型号           | 烧录文件后缀 | 是否需要进入下载模式 | 使用的命令行工具       |
| -------------- | ------------ | -------------------- | ---------------------- |
| EC600U、EC200U | pac、bin     | 否                   | CmdDloader.exe         |
| EC600N、EC600M | zip、bin     | 是                   | adownload.exe          |
| BG95           | mbn、bin     | 否                   | QMulti_DL_CMD_V2.1.exe |
| EC800E、EC600E | binpkg、bin  | 否                   | flashtoolcli1.exe      |
| FCM360W        | bin          | 否                   | EswinFlashTool.exe     |
| BC25           | lod、bin     | 否                   | QMulti_DL_CMD_V2.1.exe |
| EC200A         | blf、bin     | 否                   | SWDConsole.exe         |
| FC41D          | bin          | 否                   | bk_loader.exe          |

## 命令行格式

```bash
QuecPythonDownload.exe -d com6 -b 115200 -f "固件文件名"
```

## 下载流程

1. 根据固件文件后缀区分固件下载平台，如果是bin文件，先解压后根据解压后的文件夹中son文件区分固件平台
2. 根据固件平台调用不同的原厂命令行工具，进入下载状态
3. 再根据不同平台的下载工具返回的进度信息解析出下载进度，统一返回下载进度信息

## 编译流程

代码目录

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

打包需要将QuecPythonDownload.py和依赖的exes目录下所有文件打包成exe，并且执行不依赖环境

PyInstaller如何封装多个文件及文件夹

1. 在命令行窗口中输入：`pyi-makespec QuecPythonDownload.py`生成项目配置文件，这时候文件夹中会多出一个文件`QuecPythonDownload.spec`

2. 打开`QuecPythonDownload.spec`

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

3. 把所有的`.py`文件写到`a=Analysis()`中的首个列表元素中，如果文件和`QuecPythonDownload.py`在同一目录下，则直接写文件名，如果是在文件夹内，则需要加上绝对地址

4. 把所有的非`.py`文件放到`a=Analysis()`中的`datas`参数值中，`datas`的每个元素含两个参数，前一个是存放非`.py`文件的路径，后一个是存放的文件夹名称。在封装时，会根据这个文件夹路径搜索需要拷贝的非`.py`文件。

   ```
    datas=[(绝对路径, "exes")],
   ```





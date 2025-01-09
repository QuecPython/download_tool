import sys
import os
from utils import *
from qpy import QuecPyDownload


def main():
    import argparse
    cmd_parser = argparse.ArgumentParser(description="Download firmware on the QuecPython.")
    cmd_parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        default=False,
        help="Enable logging",
    )
    cmd_parser.add_argument(
        "-d",
        "--device",
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
        help="input QuecPython firmware file"
    )
    args = cmd_parser.parse_args()
    app_config['log'] = args.log
    # open the connection to the qpyoard
    try:
        QuecPythonOutput("SYS PATH: " + str(EXE_ABSOLUTE_PATH))
        if args.device is None or args.file is None:
            print("Please input the serial device and firmware file")
            sys.exit(1)
        else:
            print(args.device, args.baudrate, args.file)
            qpy = QuecPyDownload(args.device, args.baudrate, args.file)
    except QuecPyDownloadError as err:
        QuecPythonOutput(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
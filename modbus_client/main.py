# modbus_tool/main.py

import argparse
import sys
from .client import ModbusClient

def main():
    """程序主函数"""
    parser = argparse.ArgumentParser(description="A simple Modbus TCP command-line tool.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # 创建 'read' 命令
    parser_read = subparsers.add_parser("read", help="Read holding registers from a Modbus device.")
    parser_read.add_argument("--address", type=int, required=True, help="The starting address to read from.")
    parser_read.add_argument("--count", type=int, required=True, help="The number of registers to read.")

    # 创建 'write' 命令
    parser_write = subparsers.add_parser("write", help="Write a single value to a holding register.")
    parser_write.add_argument("--address", type=int, required=True, help="The address to write to.")
    parser_write.add_argument("--value", type=int, required=True, help="The value to write.")

    args = parser.parse_args()

    try:
        # 使用 'with' 语句，自动处理连接和关闭
        with ModbusClient() as client:
            if args.command == "read":
                values = client.read_holding_registers(args.address, args.count)
                if values is not None:
                    # 将结果打印到标准输出，供其他程序捕获
                    print(','.join(map(str, values)))
                    sys.exit(0) # 成功退出
                else:
                    sys.exit(1) # 失败退出

            elif args.command == "write":
                success = client.write_single_register(args.address, args.value)
                if success:
                    print("OK")
                    sys.exit(0)
                else:
                    sys.exit(1)

    except (ConnectionError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr) # 将错误信息打印到标准错误流
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
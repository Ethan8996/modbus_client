# modbus_tool/client.py

import logging
import os
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# 配置日志，便于调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModbusClient:
    """
    一个封装了pymodbus读写操作的Modbus TCP客户端。
    """
    def __init__(self):
        """
        初始化客户端，加载配置并创建实例。
        """
        load_dotenv()  # 从 .env 文件加载环境变量

        self.host = os.getenv('PLC_IP')
        self.port = int(os.getenv('PLC_PORT', 502)) # 提供默认端口

        if not self.host:
            raise ValueError("PLC_IP not found in .env file or environment variables.")

        logging.info(f"Initializing Modbus client for {self.host}:{self.port}")
        self.client = ModbusTcpClient(self.host, port=self.port)

    def connect(self):
        """连接到Modbus服务器"""
        logging.info("Connecting to Modbus server...")
        if not self.client.connect():
            logging.error("Failed to connect to Modbus server.")
            raise ConnectionError("Unable to connect to Modbus server.")
        logging.info("Connection successful.")

    def close(self):
        """关闭连接"""
        if self.client.is_socket_open():
            logging.info("Closing Modbus connection.")
            self.client.close()

    def read_holding_registers(self, address: int, count: int) -> list[int] | None:
        """
        读取保持寄存器。

        :param address: 起始地址
        :param count: 读取数量
        :return: 包含寄存器值的列表，如果失败则返回None
        """
        try:
            logging.info(f"Reading {count} holding registers from address {address}")
            response = self.client.read_holding_registers(address, count=count, device_id=1)

            if response.isError():
                logging.error(f"Modbus Error on read: {response}")
                return None

            logging.info(f"Read successful. Values: {response.registers}")
            return response.registers
        except ModbusException as e:
            logging.error(f"An exception occurred during read: {e}")
            return None

    def write_single_register(self, address: int, value: int) -> bool:
        """
        写入单个保持寄存器。

        :param address: 寄存器地址
        :param value: 要写入的值
        :return: 成功返回True，失败返回False
        """
        try:
            logging.info(f"Writing value {value} to address {address}")
            response = self.client.write_register(address, value, device_id=1)

            if response.isError():
                logging.error(f"Modbus Error on write: {response}")
                return False

            logging.info("Write successful.")
            return True
        except ModbusException as e:
            logging.error(f"An exception occurred during write: {e}")
            return False

    # 使用上下文管理器，可以确保连接被正确关闭，非常Pythonic！
    # 类似于Java的 try-with-resources
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
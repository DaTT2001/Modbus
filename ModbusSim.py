from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import random
from threading import Thread
import time

# Tạo Modbus datastore (Input Registers từ địa chỉ 100)
store = ModbusSlaveContext(
    ir=ModbusSequentialDataBlock(100, [0] * 16)  # 8 cặp nhiệt điện = 16 thanh ghi
)
context = ModbusServerContext(slaves=store, single=True)

def extract_temperatures(raw_data):
    print(raw_data)
    return raw_data[1::2]
# Hàm cập nhật giá trị khi có client đọc
def updating_writer(context):
    while True:
        values = []
        for _ in range(8):  # 8 cảm biến nhiệt
            temp = random.randint(500, 1000)  # Nhiệt độ thực tế khoảng 500 - 1000 độ C
            high, low = divmod(temp * 10, 65536)  # Chia thành 2 thanh ghi 16-bit
            values.extend([high, low])

        context[0].setValues(4, 100, values)  # Ghi vào Holding Registers (Function Code 3)
        temperature = [t/10 for t in extract_temperatures(values)]
        print(f"🔹 Cập nhật dữ liệu: {temperature}")  # Debug
        time.sleep(2)  # Cập nhật mỗi 2 giây

# Chạy thread cập nhật giá trị
thread = Thread(target=updating_writer, args=(context,))
thread.daemon = True
thread.start()

# Chạy server
print("🚀 Đang chạy Modbus TCP Server trên cổng 502...")
StartTcpServer(context, address=("0.0.0.0", 502))

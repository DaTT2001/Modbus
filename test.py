import time
import logging
from pymodbus.client import ModbusTcpClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_IP = "192.168.1.10"
PORT = 502
ADDRESS = 0  # Thanh ghi chứa tín hiệu 4-20 mA (cần xác định)
COUNT = 1    # Đọc 1 thanh ghi
SLAVE_ID = 1

client = ModbusTcpClient(SERVER_IP, port=PORT)
client.unit_id = SLAVE_ID

if client.connect():
    logger.info("✅ Kết nối thành công với Modbus TCP")

    try:
        while True:
            response = client.read_input_registers(address=ADDRESS, count=COUNT)
            if not hasattr(response, 'isError') or not response.isError():
                raw_value = response.registers[0]
                # Ánh xạ tuyến tính: mA = 0.000649 * Raw + 0.096
                current_mA = raw_value / 1500.0
                logger.info(f"✅ Dữ liệu thô: {raw_value}, Dòng điện: {current_mA:.3f} mA")
            else:
                logger.error(f"❌ Lỗi khi đọc Modbus: {response}")
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("🛑 Dừng chương trình")
    finally:
        client.close()
else:
    logger.error("❌ Không thể kết nối đến thiết bị Modbus TCP")
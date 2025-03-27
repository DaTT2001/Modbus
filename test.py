import time
import logging
from pymodbus.client import ModbusTcpClient
from datetime import datetime
from supabase import create_client, Client

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Thông tin Modbus Server
SERVER_IP = "192.168.1.10"
PORT = 502
ADDRESS = 0  # Thanh ghi bắt đầu chứa tín hiệu 4-20 mA
COUNT = 8  # Đọc 8 thanh ghi
SLAVE_ID = 1
TIMEOUT = 5  # Thời gian chờ (giây)

# Thông tin Supabase
SUPABASE_URL = "https://aliuuqjtebclmkvjuvuv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsaXV1cWp0ZWJjbG1rdmp1dnV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE1ODc0MzEsImV4cCI6MjA1NzE2MzQzMX0.plInkKJO8d8u-NQgzkyXxvU9FcnESWe6Cuk0Ec8PUcI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def connect_client():
    """Khởi tạo và kết nối đến Modbus Server, tự động thử lại nếu thất bại"""
    while True:
        try:
            client = ModbusTcpClient(SERVER_IP, port=PORT, timeout=TIMEOUT)
            client.unit_id = SLAVE_ID
            if client.connect():
                logger.info("✅ Kết nối thành công với Modbus TCP")
                return client
            else:
                logger.error("❌ Không thể kết nối đến thiết bị Modbus TCP, thử lại sau 5 giây...")
        except Exception as e:
            logger.error(f"⚠ Lỗi khi kết nối: {e}")
        time.sleep(5)


def save_to_supabase(raw_values):
    """Lưu dữ liệu vào Supabase"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    currents = [round(raw / 1500.0, 3) for raw in raw_values]  # Chuyển đổi tất cả giá trị thô thành mA

    data = {
        "timestamp": timestamp,
        "current_1": currents[0] if len(currents) > 0 else None,
        "current_2": currents[1] if len(currents) > 1 else None,
        "current_3": currents[2] if len(currents) > 2 else None,
        "current_4": currents[3] if len(currents) > 3 else None,
        "current_5": currents[4] if len(currents) > 4 else None,
        "current_6": currents[5] if len(currents) > 5 else None,
        # "current_7": currents[6] if len(currents) > 6 else None,
        # "current_8": currents[7] if len(currents) > 7 else None
    }

    try:
        response = supabase.table("modbus_data").insert(data).execute()  # Đổi tên bảng nếu cần
        if response.data:
            logger.info(f"✅ Dữ liệu đã lưu vào Supabase: {timestamp} - Currents: {currents}")
        else:
            logger.error(f"❌ Lỗi khi lưu vào Supabase: {response}")
    except Exception as e:
        logger.error(f"❌ Lỗi khi đẩy dữ liệu lên Supabase: {e}")


# Khởi tạo kết nối
client = connect_client()

try:
    while True:
        try:
            if not client.is_socket_open():
                logger.warning("⚠ Mất kết nối! Đang thử kết nối lại...")
                client.close()
                client = connect_client()

            response = client.read_input_registers(address=ADDRESS, count=COUNT)
            if hasattr(response, 'registers'):  # Kiểm tra xem có dữ liệu trả về không
                raw_values = response.registers
                currents = [round(raw / 1500.0, 3) for raw in raw_values]
                logger.info(f"✅ Dữ liệu thô: {raw_values}")
                logger.info(f"✅ Dòng điện (mA): {currents}")
                save_to_supabase(raw_values)
            else:
                logger.error(f"❌ Lỗi khi đọc Modbus: {response}")

        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình đọc dữ liệu: {e}")
            client.close()
            client = connect_client()

        time.sleep(1)

except KeyboardInterrupt:
    logger.info("🛑 Dừng chương trình")
finally:
    client.close()
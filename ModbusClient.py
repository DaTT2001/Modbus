import time
import matplotlib
from pymodbus.client import ModbusTcpClient
from datetime import datetime
from supabase import create_client, Client

matplotlib.rcParams["font.family"] = "DejaVu Sans"

# Thông tin Modbus Server
SERVER_IP = "127.0.0.1"
PORT = 502
ADDRESS = 100  # Địa chỉ bắt đầu đọc
COUNT = 16  # Số thanh ghi cần đọc (8 cặp)

# Thông tin Supabase
SUPABASE_URL = "https://aliuuqjtebclmkvjuvuv.supabase.co"  # URL Supabase của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsaXV1cWp0ZWJjbG1rdmp1dnV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE1ODc0MzEsImV4cCI6MjA1NzE2MzQzMX0.plInkKJO8d8u-NQgzkyXxvU9FcnESWe6Cuk0Ec8PUcI"  # Thay bằng key của bạn
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def connect_client():
    """ Tự động kết nối lại nếu mất kết nối """
    while True:
        try:
            client = ModbusTcpClient(SERVER_IP, port=PORT)
            if client.connect():
                print("✅ Kết nối Modbus Server thành công!")
                return client
            else:
                print("❌ Không thể kết nối, thử lại sau 5 giây...")
        except Exception as e:
            print(f"⚠ Lỗi kết nối: {e}")
        time.sleep(5)


def save_to_supabase(temperatures):
    """ Lưu dữ liệu vào Supabase """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tạo payload dữ liệu
    data = {
        "timestamp": timestamp,
        "sensor1_temperature": temperatures[0],
        "sensor2_temperature": temperatures[1],
        "sensor3_temperature": temperatures[2],
        "sensor4_temperature": temperatures[3],
        "sensor5_temperature": temperatures[4],
        "sensor6_temperature": temperatures[5]
    }

    # Đẩy dữ liệu lên Supabase
    response = supabase.table("t5").insert(data).execute()

    # Kiểm tra phản hồi từ Supabase
    if response.get("error"):
        print(f"❌ Lỗi khi lưu vào Supabase: {response['error']['message']}")
    else:
        print(f"✅ Dữ liệu đã lưu vào Supabase: {timestamp} {temperatures}")


def convert_registers_to_temperatures(registers):
    """ Chuyển đổi dữ liệu Modbus thành nhiệt độ thực tế """
    temperatures = []
    for i in range(0, COUNT, 2):  # Ghép 2 thanh ghi thành 1 nhiệt độ
        temp = registers[i + 1] / 10.0  # Lấy giá trị thực tế
        temperatures.append(temp)
    return temperatures


# Kết nối Modbus
client = connect_client()

try:
    while True:
        try:
            if not client.is_socket_open():
                print("⚠ Mất kết nối! Đang thử kết nối lại...")
                client.close()
                client = connect_client()

            response = client.read_input_registers(address=ADDRESS, count=COUNT)

            if response.isError():
                print(f"❌ Lỗi khi đọc dữ liệu! {response}")
            else:
                registers = response.registers
                temperatures = convert_registers_to_temperatures(registers)
                print(f"✅ Dữ liệu nhận được: {temperatures}")

                # Lưu vào Supabase
                save_to_supabase(temperatures)

        except Exception as e:
            print(f"❌ Lỗi khi đọc dữ liệu: {e}")
            client.close()
            client = connect_client()

        time.sleep(10)

except KeyboardInterrupt:
    print("🛑 Dừng client.")
finally:
    client.close()

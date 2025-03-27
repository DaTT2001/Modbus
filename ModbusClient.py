import time
import requests
from pymodbus.client import ModbusTcpClient
from datetime import datetime
from supabase import create_client, Client

# Thông tin Modbus Server
SERVER_IP = "192.168.1.11"
PORT = 502
ADDRESS = 0  # Địa chỉ bắt đầu đọc
COUNT = 8  # Số thanh ghi cần đọc

# Thông tin Supabase
SUPABASE_URL = "https://aliuuqjtebclmkvjuvuv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsaXV1cWp0ZWJjbG1rdmp1dnV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE1ODc0MzEsImV4cCI6MjA1NzE2MzQzMX0.plInkKJO8d8u-NQgzkyXxvU9FcnESWe6Cuk0Ec8PUcI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Danh sách API cần gửi dữ liệu
API_ENDPOINTS = [
    "http://192.168.10.87:8080/api/t4",
    "http://192.168.10.87:8081/api/v1/rIlIYYm0rizWGqkrhuQY/telemetry"
]
def connect_client():
    """Tự động kết nối lại nếu mất kết nối"""
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
    """Lưu dữ liệu vào Supabase"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": timestamp,
        "sensor1_temperature": temperatures[0],
        "sensor2_temperature": temperatures[1],
        "sensor3_temperature": temperatures[2],
        "sensor4_temperature": temperatures[3],
        "sensor5_temperature": temperatures[4],
        "sensor6_temperature": temperatures[5],
        "sensor7_temperature": temperatures[6],
        "sensor8_temperature": temperatures[7],
    }

    response = supabase.table("t4").insert(data).execute()

    if response.get("error"):
        print(f"❌ Lỗi khi lưu vào Supabase: {response['error']['message']}")
    else:
        print(f"✅ Dữ liệu đã lưu vào Supabase: {timestamp} {temperatures}")

# def send_to_api(temperatures):
#     """Gửi dữ liệu đến API"""
#     timestamp = datetime.now().isoformat()
#
#     payload = {
#         "timestamp": timestamp,
#         "sensor1": temperatures[0],
#         "sensor2": temperatures[1],
#         "sensor3": temperatures[2],
#         "sensor4": temperatures[3],
#         "sensor5": temperatures[4],
#         "sensor6": temperatures[5],
#         "sensor7": temperatures[6],
#         "sensor8": temperatures[7],
#     }
#
#     for url in API_ENDPOINTS:
#         try:
#             response = requests.post(url, json=payload, timeout=5)
#             if response.status_code == 200:
#                 print(f"✅ Gửi dữ liệu thành công đến {url}")
#             else:
#                 print(f"⚠ Lỗi gửi dữ liệu đến {url}: {response.status_code} - {response.text}")
#         except requests.exceptions.RequestException as e:
#             print(f"❌ Lỗi kết nối API {url}: {e}")
def send_to_api(temperatures):
    """ Gửi dữ liệu lên cả hai API """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": timestamp,
        "sensor1_temperature": temperatures[0],
        "sensor2_temperature": temperatures[1],
        "sensor3_temperature": temperatures[2],
        "sensor4_temperature": temperatures[3],
        "sensor5_temperature": temperatures[4],
        "sensor6_temperature": temperatures[5],
        "sensor7_temperature": temperatures[6],
        "sensor8_temperature": temperatures[7],
    }

    api_endpoints = [
        "http://192.168.10.87:8080/api/t4",
        "http://192.168.10.87:8081/api/v1/rIlIYYm0rizWGqkrhuQY/telemetry"
    ]

    for url in api_endpoints:
        try:
            response = requests.post(url, json=data, timeout=5)

            if response.status_code in [200, 201]:
                print(f"✅ Dữ liệu đã gửi thành công lên {url}")
            else:
                print(f"⚠ Cảnh báo: API {url} trả về mã {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Lỗi khi gửi dữ liệu lên {url}: {e}")
def convert_registers_to_temperatures(registers):
    """Chuyển đổi dữ liệu Modbus thành nhiệt độ thực tế"""
    return [reg / 10 for reg in registers]  # Chia 10 để lấy giá trị thực

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
                # Gửi lên các API
                send_to_api(temperatures)
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

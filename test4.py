import time
import requests  # Thêm thư viện này
from pymodbus.client import ModbusTcpClient
from datetime import datetime

# Thông tin Modbus Server
SERVER_IP = "192.168.1.11"
PORT = 502
ADDRESS = 0
COUNT = 8

# API Endpoint
API_URL = "http://192.168.10.87:8081/api/v1/hYUzKwCZuGwwgqi1Q7rQ/telemetry"

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

def send_to_api(temperatures):
    """ Gửi dữ liệu lên API """

    data = {
        "sensor1_temperature": temperatures[0],
        "sensor2_temperature": temperatures[1],
        "sensor3_temperature": temperatures[2],
        "sensor4_temperature": temperatures[3],
        "sensor5_temperature": temperatures[4],
        "sensor6_temperature": temperatures[5],
        "sensor7_temperature": temperatures[6],
        "sensor8_temperature": temperatures[7],
    }

    try:
        response = requests.post(API_URL, json=data, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✅ Dữ liệu đã gửi lên API: {temperatures}")
        else:
            print(f"⚠ Cảnh báo: API trả về mã {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Lỗi khi gửi dữ liệu lên API: {e}")


def convert_registers_to_temperatures(registers):
    """ Chuyển đổi dữ liệu Modbus thành nhiệt độ thực tế """
    temperatures = []
    for i in range(len(registers)):
        temp = registers[i] / 10  # Giả sử nhiệt độ cần chia 10
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

                # Gửi lên API
                send_to_api(temperatures)

        except Exception as e:
            print(f"❌ Lỗi khi đọc dữ liệu: {e}")
            client.close()
            client = connect_client()

        time.sleep(10)

except KeyboardInterrupt:
    print("🛑 Dừng client.")
finally:
    client.close()

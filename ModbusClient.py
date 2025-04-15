import time
import requests
from datetime import datetime
from pymodbus.client import ModbusTcpClient
import threading

# Cấu hình chung
PORT = 502
ADDRESS = 0
COUNT = 8

# Cấu hình server và API endpoints
CONFIG = {
    "client1": {
        "server_ip": "192.168.2.10",
        "api_endpoints": [
            "http://192.168.10.87:8080/api/g1",
            "http://192.168.10.87:8081/api/v1/mPnKodsGI66fyM8fBDNV/telemetry"
        ]
    },
    "client2": {
        "server_ip": "192.168.2.11",
        "api_endpoints": [
            "http://192.168.10.87:8080/api/g2",
            "http://192.168.10.87:8081/api/v1/CZTxzFBMcdV8wnZ8Lqsi/telemetry"
        ]
    },
    "client3": {
        "server_ip": "192.168.2.12",
        "api_endpoints": [
            "http://192.168.10.87:8080/api/g3",
            "http://192.168.10.87:8081/api/v1/hwm2dsgx8lkin2vv8c1s/telemetry"
        ]
    }
}

def connect_modbus_client(server_ip, client_name):
    """Kết nối đến Modbus TCP Server"""
    while True:
        try:
            client = ModbusTcpClient(server_ip, port=PORT)
            if client.connect():
                print(f"✅ [{client_name}] Đã kết nối Modbus thành công.")
                return client
            else:
                print(f"❌ [{client_name}] Kết nối thất bại. Thử lại sau 5 giây...")
        except Exception as e:
            print(f"⚠ [{client_name}] Lỗi kết nối Modbus: {e}")
        time.sleep(5)

def convert_registers_to_temperatures(registers):
    """Chuyển giá trị thanh ghi thành nhiệt độ thực tế"""
    return [reg / 10 for reg in registers]

def send_to_api(temperatures, api_endpoints, client_name):
    """Gửi dữ liệu nhiệt độ đến các API"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
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

    for url in api_endpoints:
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code in [200, 201]:
                print(f"✅ [{client_name}] Gửi thành công đến {url}")
            else:
                print(f"⚠ [{client_name}] API {url} trả về mã {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ [{client_name}] Lỗi khi gửi đến {url}: {e}")

def main_loop(server_ip, api_endpoints, client_name):
    """Vòng lặp chính cho mỗi client"""
    client = connect_modbus_client(server_ip, client_name)

    try:
        while True:
            try:
                if not client.is_socket_open():
                    print(f"⚠ [{client_name}] Mất kết nối. Đang thử lại...")
                    client.close()
                    client = connect_modbus_client(server_ip, client_name)

                response = client.read_input_registers(address=ADDRESS, count=COUNT)

                if response.isError():
                    print(f"❌ [{client_name}] Lỗi đọc thanh ghi: {response}")
                else:
                    registers = response.registers
                    temperatures = convert_registers_to_temperatures(registers)
                    print(f"✅ [{client_name}] Nhiệt độ đọc được: {temperatures}")
                    # send_to_api(temperatures, api_endpoints, client_name)
                    if client_name == "client3":
                        # Lấy giá trị trung bình của 7 cảm biến còn lại (bỏ qua index 1)
                        valid_values = [temp for i, temp in enumerate(temperatures) if i != 1]
                        average = sum(valid_values) / len(valid_values)
                        temperatures[1] = round(average, 1)  # Làm tròn 1 chữ số thập phân
                        print(f"⚠ [{client_name}] Thay thế sensor2_temperature bằng trung bình: {temperatures[1]}")

                    send_to_api(temperatures, api_endpoints, client_name)

            except Exception as e:
                print(f"❌ [{client_name}] Lỗi trong quá trình đọc/gửi: {e}")
                client.close()
                client = connect_modbus_client(server_ip, client_name)

            time.sleep(10)

    except KeyboardInterrupt:
        print(f"🛑 [{client_name}] Dừng chương trình.")
    finally:
        client.close()

if __name__ == "__main__":
    # Tạo danh sách các luồng
    threads = []

    # Tạo luồng cho từng client
    for client_name, config in CONFIG.items():
        thread = threading.Thread(
            target=main_loop,
            args=(config["server_ip"], config["api_endpoints"], client_name)
        )
        threads.append(thread)
        thread.start()

    # Chờ tất cả các luồng kết thúc (trong trường hợp này là khi người dùng nhấn Ctrl+C)
    for thread in threads:
        thread.join()
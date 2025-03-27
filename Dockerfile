# Sử dụng Python 3.10 (hoặc phiên bản phù hợp)
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Copy file vào container
COPY . .

# Cài đặt thư viện (nếu có requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Chạy script khi container khởi động
CMD ["python", "ModbusClient.py"]

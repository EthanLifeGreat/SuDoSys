import time


def generate_ssid():
    # 获取当前时间
    current_time = time.localtime()

    # 格式化时间为字符串，例如：20240730_1530
    time_str = time.strftime("%Y%m%d_%H%M", current_time)

    # 在时间字符串后添加一个随机部分以确保唯一性
    random_part = str(int(time.time() * 1000) % 1000)  # 获取当前时间戳的毫秒部分并取模

    # 生成 SSID
    ssid = f"SSID_{time_str}_{random_part}"
    return ssid

if __name__ == "__main__":

    # 生成 SSID
    ssid = generate_ssid()
    print("Generated SSID:", ssid)
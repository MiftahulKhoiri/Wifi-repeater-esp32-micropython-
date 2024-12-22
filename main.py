import network
import socket
import time
import wifi_config
import machine

#Konfigurasi Awal
SSID_REPEATER = "ESP32_Repeater"
PASSWORD_REPEATER = "esp32123"
CHANNEL = 6
MAX_ATTEMPTS = 5
TIMEOUT_CONNECTION = 10
LAMPU_PIN = 2

#Inisialisasi WiFi
wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

#Inisialisasi Lampu
lampu = machine.Pin(LAMPU_PIN, machine.Pin.OUT)

def hidupkan_lampu():
    lampu.value(1)

def matikan_lampu():
    lampu.value(0)

def berkedip_lampu():
    while True:
        lampu.value(1)
        time.sleep(0.5)
        lampu.value(0)
        time.sleep(0.5)

def start_repeater(ssid):
    wlan_ap.activa(False)
    wlan_ap.active(True)
    wlan_ap.config(essid=ssid, password=PASSWORD_REPEATER, channel=CHANNEL, authmode=4)
    print("Repeater aktif")
    import threading
    threading.Thread(target=berkedip_lampu).start()

def connect_wifi(ssid, password):
    wlan_sta.active(False)
    wlan_sta.active(True)
    wlan_sta.disconnect()
    attempts = 0
    start_time = time.time()
    while attempts < MAX_ATTEMPTS and time.time() - start_time < TIMEOUT_CONNECTION:
        try:
            wlan_sta.connect(ssid, password)
            time.sleep(1)
            if wlan_sta.isconnected():
                print(f"Terhubung ke {ssid}")
                wifi_config.save_config(ssid, password)
                simpan_data_wifi(ssid, password)
                start_repeater(f"{ssid}_Repeater")
                return
        except Exception as e:
            print(f"Kesalahan: {e}")
        attempts += 1
        time.sleep(2)
    print("Gagal menghubungkan WiFi, menjalankan mode AP")
    start_repeater(SSID_REPEATER)
    web_server()

def web_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 80))
    sock.listen(1)
    print("Web server aktif")
    ip = wlan_ap.ifconfig()[0]
    print(f"Alamat Web Server: http://{ip}:80/")
    while True:
        try:
            conn, addr = sock.accept()
            request = conn.recv(1024)
            if request:
                data = request.decode().split('&')
                if len(data) == 2:
                    ssid = data[0].split('ssid=')[1]
                    password = data[1].split('password=')[1]
                    print(f"WiFi Terpilih: {ssid}")
                    connect_wifi(ssid, password)
                    conn.sendall(b'OK')
                    conn.close()
                else:
                    print("Data tidak lengkap")
            else:
                print("Tidak ada data")
        except Exception as e:
            print(f"Kesalahan: {e}")

def simpan_data_wifi(ssid, password):
    with open("wifi_data.txt", "a") as f:
        f.write(f"SSID: {ssid}, Password: {password}\n")
    print("Data WiFi disimpan")

def main():
    hidupkan_lampu()
    config = wifi_config.load_config()
    if config:
        ssid = config['ssid']
        password = config['password']
        connect_wifi(ssid, password)
    else:
        start_repeater(SSID_REPEATER)
        web_server()

if __name__ == "__main__":
    main()
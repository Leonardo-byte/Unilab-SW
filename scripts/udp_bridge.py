# scripts/udp_bridge.py

import socket

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5005

FORWARD_HOST = "127.0.0.1"
FORWARD_PORT = 5006

BUFFER_SIZE = 4096


def main() -> None:
    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx.bind((LISTEN_HOST, LISTEN_PORT))

    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[UDP Bridge] Escuchando ESP32 en {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[UDP Bridge] Reenviando a {FORWARD_HOST}:{FORWARD_PORT}")

    while True:
        data, addr = rx.recvfrom(BUFFER_SIZE)
        print(f"[UDP Bridge] Desde {addr}: {data.decode(errors='ignore')}")
        tx.sendto(data, (FORWARD_HOST, FORWARD_PORT))


if __name__ == "__main__":
    main()
import socket
import threading

HOST = '127.0.0.1'
PORT = 8889

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"\n{message}")
            print("> ", end='', flush=True)
        except:
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"已连接到聊天服务器 {HOST}:{PORT}")
print("输入消息 (输入 'quit' 退出)")

receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
receive_thread.start()

while True:
    message = input("> ")
    if message.lower() == 'quit':
        break
    client_socket.send(message.encode('utf-8'))

client_socket.close()
print("已断开连接")

import socket
import threading

HOST = '127.0.0.1'
PORT = 8889

clients = []
lock = threading.Lock()

def handle_client(client_socket, client_address):
    print(f"新客户端连接: {client_address}")
    
    with lock:
        clients.append(client_socket)
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"收到来自 {client_address} 的消息: {message}")
            
            broadcast_message = f"[{client_address[0]}:{client_address[1]}] {message}"
            
            with lock:
                for client in clients:
                    if client != client_socket:
                        try:
                            client.send(broadcast_message.encode('utf-8'))
                        except:
                            pass
    except Exception as e:
        print(f"客户端 {client_address} 发生错误: {e}")
    finally:
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"客户端 {client_address} 已断开")

def broadcast_message(message):
    with lock:
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                pass

def server_input():
    while True:
        message = input()
        if message:
            broadcast_message(f"[服务器] {message}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"聊天服务器启动，监听 {HOST}:{PORT}")
print("等待客户端连接...")

input_thread = threading.Thread(target=server_input, daemon=True)
input_thread.start()

while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address),
        daemon=True
    )
    client_thread.start()

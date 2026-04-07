import socket

HOST = '127.0.0.1'
PORT = 8890

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"回声服务器启动，监听 {HOST}:{PORT}")
print("等待客户端连接... (按 Ctrl+C 停止服务器)")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"\n客户端 {client_address} 已连接")
        
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                print(f"收到: {data.decode('utf-8')}")
                client_socket.send(data)
                print(f"已回声发送")
        except Exception as e:
            print(f"错误: {e}")
        finally:
            client_socket.close()
            print(f"客户端 {client_address} 已断开")
except KeyboardInterrupt:
    print("\n服务器正在关闭...")
finally:
    server_socket.close()
    print("服务器已关闭")

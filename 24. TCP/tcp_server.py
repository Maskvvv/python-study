import socket

HOST = '127.0.0.1'
PORT = 8888

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"服务器启动，监听 {HOST}:{PORT}")
print("等待客户端连接...")

client_socket, client_address = server_socket.accept()
print(f"客户端 {client_address} 已连接")

while True:
    data = client_socket.recv(1024)
    if not data:
        break
    
    message = data.decode('utf-8')
    print(f"收到消息: {message}")
    
    response = f"服务器已收到: {message}"
    client_socket.send(response.encode('utf-8'))

client_socket.close()
server_socket.close()
print("服务器已关闭")

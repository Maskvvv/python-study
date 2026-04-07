import socket

HOST = '127.0.0.1'
PORT = 8888

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"已连接到服务器 {HOST}:{PORT}")
print("输入消息 (输入 'quit' 退出)")

while True:
    message = input("> ")
    if message.lower() == 'quit':
        break
    
    client_socket.send(message.encode('utf-8'))
    data = client_socket.recv(1024)
    response = data.decode('utf-8')
    print(f"服务器响应: {response}")

client_socket.close()
print("连接已关闭")

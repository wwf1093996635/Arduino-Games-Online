from socket import *
import threading
import os

def client_handler(client_socket, client_address):
    """
    接收各个客户端发来的数据，并原样返回
    :param client_socket:
    :param client_address:
    :return:
    """
    try:
        while True:
            # 接收客户端发来的数据，阻塞，直到有数据到来
            # 如果客户端关闭了连接，data是空字符串
            try:
                data = client_socket.recv(4096)
            except Exception:
                #handle ConnectionResetError
                data = ""
            if data:
                print('子线程 [{}]: 接收到消息 {}({} bytes) 来自 {}'.format(threading.current_thread().name, data, len(data), client_address))
                # 返回响应数据，将客户端发送来的数据原样返回
                client_socket.send("Server received your data:".encode()+data)
                print('子线程 [{}]: 发送 {} 至 {}'.format(threading.current_thread().name, data, client_address))
            else:
                print('子线程 [{}]: 客户端 {} 已断开！'.format(threading.current_thread().name, client_address))
                break
    finally:
        # 关闭为这个客户端服务的socket
        client_socket.close()

#HOST = '39.106.174.173'
HOST = ''
PORT =425
BUFSIZ = 1024
ADDRESS = (HOST, PORT)

# 创建监听socket
tcpServerSocket = socket(AF_INET, SOCK_STREAM)

print("主进程号:%d"%(os.getpid()))

# 绑定IP地址和固定端口
tcpServerSocket.bind(ADDRESS)
print("服务器启动，监听端口{}...".format(ADDRESS[1]))

# socket默认是主动连接，调用listen()函数将socket变为被动连接，这样就可以接收客户端连接了
tcpServerSocket.listen(5)

try:
    while True:
        print('主线程 [{}]: 服务器正在运行，等待客户端连接...'.format(threading.current_thread().name))

        # 主进程只用来负责监听新的客户连接
        # client_socket是专为这个客户端服务的socket，client_address是包含客户端IP和端口的元组
        client_socket, client_address = tcpServerSocket.accept()
        print('主线程 [{}]: 客户端 {} 已连接！'.format(threading.current_thread().name, client_address))

        # 为每个新的客户连接创建一个线程，用来处理客户数据
        client = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client.start()

        # 因为主线程与子线程共享client_socket，所以在主线程中不能关闭client_socket
        # client_socket.close()
finally:
    # 关闭监听socket，不再响应其它客户端连接
    tcpServerSocket.close()

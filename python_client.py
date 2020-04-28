from socket import *
import concurrent.futures as futures

HOST = 'wwf194.site'
#HOST = '39.106.174.173'
PORT =427

class TCPClient:
    def __init__(self, host='127.0.0.1', port=9000):
        self.HOST = host
        self.PORT = port
        self.BUFSIZ = 1024
        self.ADDRESS = (self.HOST, self.PORT)
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect(self.ADDRESS)

    def send(self, msg):
        """
        向服务器端发送信息
        :param msg:
        :return:
        """
        self.tcpClientSocket.send(msg.encode('utf-8'))

    def receive(self):
        try:
            while True:
                data = self.tcpClientSocket.recv(self.BUFSIZ)
                if not data:
                    break
                print("    (Just received from server：{})".format(data.decode('utf-8')))
        finally:
            print("连接已断开！")
            self.tcpClientSocket.close()

def main():
    ex = futures.ThreadPoolExecutor(max_workers=1)
    tc = TCPClient(host=HOST, port=PORT)
    ex.submit(tc.receive)

    while True:
        print("Input something to send to server(input exit to quit):", end='\n')
        data = input("")
        if(data=="exit"):
            tc.tcpClientSocket.close()
            break
        if not data:
            print("连接已断开！")
            tc.tcpClientSocket.close()
            break
        tc.send(data)
main()
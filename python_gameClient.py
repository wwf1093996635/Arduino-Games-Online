from socket import *
import concurrent.futures as futures
import serial
import random
import sys
import os
import time

HOST = 'wwf194.site'
#HOST = '39.106.174.173'
PORT =427

class TCPClient:
    def __init__(self, arduino, host='127.0.0.1', port=9000):
        self.HOST = host
        self.PORT = port
        self.BUFSIZ = 1024
        self.ADDRESS = (self.HOST, self.PORT)
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect(self.ADDRESS)
        self.arduino = arduino
        self.error=False
    def send(self, msg):
        '''
        向服务器端发送信息
        :param msg:
        :return:
        '''
        self.tcpClientSocket.send(msg)

    def receive(self):
        try:
            while True:
                data = self.tcpClientSocket.recv(self.BUFSIZ)
                if not data:
                    break
                data_str = data.decode('utf-8')
                print("    (Just received from server：{})".format(data_str))
                if(data_str=="abort,"):
                    print("服务器中断了本次游戏！即将关闭客户端...")
                    self.arduino.write(data)
                    self.tcpClientSocket.close()
                    time.sleep(10)
                    os._exit(0)
                elif(data_str=="win,"):
                    print("您赢了！即将关闭客户端...")
                    self.arduino.write(data)
                    self.tcpClientSocket.close()
                    time.sleep(10)
                    os._exit(0)
                elif(data_str=="lose,"):
                    print("您输了！即将关闭客户端...")
                    self.arduino.write(data)
                    self.tcpClientSocket.close()
                    time.sleep(10)
                    os._exit(0)                
                self.arduino.write(data)
        finally:
            print("与服务器的连接意外中断！即将关闭客户端...")
            self.tcpClientSocket.close()
            time.sleep(10)
            os._exit(0)

def main():
    sig = True
    while sig:
        print("input your arduino serial name(default: COM3):")
        serial_name = input()
        if(serial_name==""):
            serial_name = 'COM3'
        port_name = serial_name #arduino port name on your PC.
        try:
            arduino = serial.Serial(port_name, 115200, timeout=.1)
            sig = False
        except Exception:
            print("error: unable to establish connection with serial:" + serial_name)

    ex = futures.ThreadPoolExecutor(max_workers=1)
    try:
        tc = TCPClient(host=HOST, port=PORT, arduino=arduino)
        print("已连接至服务器!")
    except Exception:
        print("错误：无法连接服务器！即将关闭客户端...")
        time.sleep(10)
        os._exit(0)
    
    ex.submit(tc.receive)

    while True:
        while True:
            data = arduino.readline()
            if(str(data, encoding='utf-8')==""):
                continue
            else:
                break
        print("received from arduino:", end='')
        data_str = str(data, encoding='utf-8')
        tc.send(data)
        print(data_str)
        if(data_str=="abort,"):
            print("Arduino端终止了游戏！即将关闭客户顿...")
            try:
                tc.tcpClientSocket.close()
            except Exception:
                pass
            time.sleep(10)
            os._exit(0)
main()
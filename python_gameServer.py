from socket import *
import threading
import os
import random
import threading
import time
import traceback

class EinsteinChess_runner(threading.Thread):
    def __init__(self):
        super().__init__()
        self.red = None
        self.blue = None
        self.ready = False
        self.player_num = 0
        self.loc = None
        self.board = None
        self.red_chessmen = None
        self.blue_chessmen = None
        self.control = threading.Event()
        self.alarm = False
        self.is_waiting = False
        self.abort = False
        self.waiting = "red"
    def add_socket(self, socket):
        if(self.red is None):
            self.red = socket
            self.player_num += 1
            print("red player is ready.")
        elif(self.blue is None):
            self.blue = socket
            self.player_num += 1
            print("blue player is ready.")
        else:
            print("This runner already has 2 players.")
    
        if(self.player_num ==2):
            self.ready = True

    def check_message(self, side="", inst=""):
        abnormal_message = ["error,", "close,", "abort,"]
        if(side=="" and inst==""):
            #make sure the 2 TCP connections are still alive.
            while(True):
                m0 = self.red.get_message()
                m1 = self.blue.get_message()
                print("m0:%s m1:%s"%(m0, m1))
                if(m0 in abnormal_message or m1 in abnormal_message):
                    return "exit"
                if(m0 is None and m1 is None):
                    break
            return None
        elif(side=="red"):
            player = self.red
        elif(side=="blue"):
            player = self.blue
        else:
            return "invalid side:" + side
        message = []
        while(True):
            m = player.get_message()
            if(m is None):
                print("m is None.")
                break
            print("m:%s"%(m))
            if(m.split(',')[0]==inst):
                print(m.split(','))
                message.append(m)
            if(m in abnormal_message):
                print("receiver abnormal_message")
                return "exit"
        if(len(message)==1):
            message = message[0]
        print(message)
        return message
    def init_chessboard(self):
        self.loc = [0, 1, 2, 5, 6, 10, 24, 23, 22, 19, 18, 14]
        self.board = [
            [ 0, 1, 2,-1,-1],
            [ 3, 4,-1,-1,-1],
            [ 5,-1,-1,-1,11],
            [-1,-1,-1,10, 9],
            [-1,-1, 8, 7, 6]
        ]
        self.red_chessmen=[0,1,2,3,4,5]
        self.blue_chessmen=[6,7,8,9,10,11]
    def select_chessman(self, side="red"):
        if(side=="red"):
            return random.choice(self.red_chessmen)
        elif(side=="blue"):
            return random.choice(self.blue_chessmen)
        else:
            return "invalid side:%s"%(side)
    def loc2xy(self, loc):
        x = loc % 5
        if(x % 2 ==0):
            y = 4 - (loc/5)
        else:
            y = loc/5
        return x, y
    def move_chessman(self, chessman, loc, side="red"):
        if(loc<0 or loc>24):
            return "error: illegal loc"
        x, y = self.loc2xy(loc)
        if(side=="red"):
            chessmen = self.red_chessmen
        elif(side=="blue"):
            chessmen = self.blue_chessmen
        else:
            return "error: illegal side:" + side
        if(chessman in chessmen):
            if(loc in self.loc):
                index = self.loc.index(loc)
                print("index=%d"%(index))
                self.loc[index] = -1
                if(index in self.red_chessmen):
                    self.red_chessmen.remove(index)
                else:
                    self.blue_chessmen.remove(index)
            self.loc[chessman] = loc

            print(self.loc)
            print(self.red_chessmen)
            print(self.blue_chessmen)

            return "done"
        else:
            return "error: illegal chessman to move:" + str(chessman)

    def check_win(self):
        if(len(self.blue_chessmen)==0):
            return "red"
        elif(len(self.red_chessmen)==0):
            return "blue"
        elif(0 in self.loc[6:12]):
            return "blue"
        elif(24 in self.loc[0:6]):
            return "red"
        else:
            return "none"
    def generate_update_chessboard_inst(self):
        inst = "update,"
        for loc in self.loc:
            inst = inst + str(loc)
            inst = inst + ","
        print("generated update instruction:"+inst)
        return inst
    
    def run(self):
        try:
            if(self.player_num<2):
                return
            print("starting game")
            if(self.check_message() == "exit"):
                return
            self.init_chessboard()
            inst = self.generate_update_chessboard_inst()
            self.red.send(inst)
            self.blue.send(inst)
            
            side = "red"
            while(True):
                chessman = self.select_chessman(side=side)
                if(side=="red"):
                    self.red.send("move,%d,"%(chessman))
                else:
                    self.blue.send("move,%d,"%(chessman))
                
                if(self.alarm==True):
                    alarm_0 = alarm(self)
                    alarm_0.set_sleep_time(30)
                    alarm_0.start()
                self.waiting=side
                self.is_waiting=True
                self.control.wait()
                self.is_waiting=False
                self.control.clear()
                if(self.abort==True):
                    raise Exception
                if(self.alarm==True):
                    if(alarm_0.valid==True):
                        alarm_0.valid=False
                #print("ddd")
                message = self.check_message(side=side, inst="move")      
                #print("ccc")
                if(message == "exit"):
                    raise Exception
                if(isinstance(message, list)):
                    #print("aaa")
                    raise Exception
                #print("bbb")

                params = message.split(',')
                print(self.move_chessman(chessman=int(params[1]), loc=int(params[2]), side=side))
                
                win = self.check_win()
                if(win != "none"):
                    if(win=="red"):
                        self.red.send("win,")
                        self.blue.send("lose,")
                    else:
                        self.red.send("lose,")
                        self.blue.send("win,")
                    
                    print("ggg")
                    raise Exception

                print("fff")
                inst = self.generate_update_chessboard_inst()
                self.red.send(inst)
                self.blue.send(inst)

                if(side=="red"):
                    side="blue"
                    self.waiting="blue"
                else:
                    side="red"
                    self.waiting="red"
                #print("hhh")
        except Exception:
            traceback.print_exc()   
            try:
                if(self.red.is_closed==False):
                    self.red.close()
            except Exception:
                pass
            try:
                if(self.blue.is_closed==False):
                    self.blue.close()
            except Exception:
                pass
            return
        #print("kkk")
        return
class alarm(threading.Thread):
    def __init__(self, runner):
        super().__init__()
        self.time = 30
        self.runner = runner
        self.valid=True
    def run(self):
        time.sleep(30)
        if(self.valid==True):
            if(self.runner.control.isSet()==False):
                self.runner.control.set()
    def set_sleep_time(self, time):
        self.time = time
        self.valid=True
class client_handler():
    def __init__(self, client_socket, client_address, runner, name):
        self.client_socket = client_socket
        self.client_address = client_address
        self.messages = []
        self.pointer = 0
        self.runner = runner
        self.name = name
        self.other = None
        self.is_closed=False
    def set_other(self, other):
        self.other = other
    def handle(self, client_socket, client_address):
        try:
            while True:
                # 接收客户端发来的数据，阻塞，直到有数据到来
                # 如果客户端关闭了连接，data是空字符串
                try:
                    data = self.client_socket.recv(4096)
                except Exception:
                    self.add_message("error")
                if data:
                    print("kkk")
                    data = data.decode('utf-8')
                    print('子线程 [{}]: 接收到消息 {}({} bytes) 来自 {}'.format(threading.current_thread().name, data, len(data), self.client_address))
                    # 返回响应数据，将客户端发送来的数据原样返回
                    #client_socket.send("Server received your data:".encode()+data)
                    self.add_message(data)
                    if(self.runner.control.isSet()==False and self.runner.waiting==self.name and self.runner.is_waiting):
                        print("jjj")
                        self.runner.control.set()
                else:
                    self.add_message("error")
                    break
        except Exception:
            pass
        finally:
            print('断开 子线程 [{}]: 客户端 {}！'.format(threading.current_thread().name, self.client_address))
            self.add_message("close")
            try:
                self.close()
            except Exception:
                pass
            try:
                if(self.other is not None):
                    #print("ggg")
                    if(self.other.is_closed==False):
                        self.other.close()
            except Exception:
                pass
    def close(self):
        self.is_closed=True
        self.add_message("close")
        try:
            self.send("abort,")
        except Exception:
            pass
        try:
            self.client_socket.close()
            print("ccc")
            print('子线程 [{}]: 客户端 {} 已断开！'.format(threading.current_thread().name, self.client_address))
        except Exception:
            pass
        try:
            if(self.runner.control.isSet()==False and self.runner.is_waiting==True):
                print(self.runner.control.isSet())
                print(self.runner.is_waiting)
                self.runner.abort=True
                self.runner.control.set()
        except Exception:
            pass
        
    def send(self, data):
        try:
            self.client_socket.send(data.encode('utf-8'))
            print('子线程 [{}]: 发送 {} 至 {}'.format(threading.current_thread().name, data, self.client_address))
        except Exception:
            if(self.is_closed==False):
                self.close()
            if(self.other.is_closed==False):
                self.other.close()
            raise Exception
    def add_message(self, data):
        self.messages.append(data)
    def get_message(self):
        print(self.name + " messages:", end=' ')
        print(self.messages)
        if(self.pointer == (len(self.messages))):
            return None
        else:
            m = self.messages[self.pointer]
            self.pointer = self.pointer + 1
            return m

def main():
    #kill_process(424)

    #HOST = '39.106.174.173'
    HOST = ''
    PORT =427
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
            try:
                print('主线程 [{}]: 服务器正在运行，等待客户端连接...'.format(threading.current_thread().name))

                runner = EinsteinChess_runner()
                # 主进程只用来负责监听新的客户连接
                # client_socket是专为这个客户端服务的socket，client_address是包含客户端IP和端口的元组
                client_socket, client_address = tcpServerSocket.accept()
                print('主线程 [{}]: 客户端 {} 已连接！'.format(threading.current_thread().name, client_address))
                handlerA = client_handler(client_socket, client_address, runner=runner, name="red")
                client = threading.Thread(target=handlerA.handle, args=(client_socket, client_address))
                client.start()
                runner.add_socket(handlerA)
                handlerA.send("wait,")
                client_socket, client_address = tcpServerSocket.accept()
                print('主线程 [{}]: 客户端 {} 已连接！'.format(threading.current_thread().name, client_address))
                handlerB = client_handler(client_socket, client_address, runner=runner, name="blue")
                client = threading.Thread(target=handlerB.handle, args=(client_socket, client_address))
                client.start()
                runner.add_socket(handlerB)
                handlerA.set_other(handlerB)
                handlerB.set_other(handlerA)
                run = threading.Thread(target=runner.run, args=())
                run.start()
            except Exception:
                print("匹配玩家时出现错误")
    finally:
        # 关闭监听socket，不再响应其它客户端连接
        tcpServerSocket.close()

main()
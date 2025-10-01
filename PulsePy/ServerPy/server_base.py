# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:39:17 2020

@author: schli
"""

import socket, json
import numpy as np

class NDArrayEncoder(json.JSONEncoder):
        
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return obj.decode()
        return json.JSONEncoder.default(self, obj)

class Translator:
    
    def __init__(self, server, serial_driver):
        self.server=server
        self.serial_driver=serial_driver
    
    def call(self, cmd, conn):
        res=None
        if len(cmd['args'])==0 or\
        (len(cmd['args'])==1 and len(cmd['args'][0])==0)or\
        'args' not in cmd.keys():
            res=getattr(self.serial_driver, cmd['command'])(**cmd['kwargs'])
        else:
            res=getattr(self.serial_driver, cmd['command'])(*cmd['args'], **cmd['kwargs'])
        if res is not None:
            response=json.dumps(dict({'content':res}), cls=NDArrayEncoder)
            self.server.send_answer(conn, response, parsing=False)
        
class Generic_Server:
    
    def __init__(self, ip='127.0.0.1', port=11000, serial_driver=None, connected=True):
        self.ip=ip
        self.port=port
        self.interprete=Translator(self, serial_driver)
        if connected:
            self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.s.bind((self.ip, self.port))
                self.s.listen(10)
                self.connected=True
                print("server is connected")
                while self.connected:
                    conn, addr=self.s.accept()
                    raw_msglen = conn.recv(10)
                    if not raw_msglen:
                        print("No raw_msglen")
                        break
                    msglen = int(raw_msglen.decode(),16)
                    print('len of packet is {:}'.format(msglen))
                    data=self.receive_all(conn, msglen)
                    if data is not None:
                        self.interpreter(conn, data)
                    elif len(data)!=msglen:
                        print('the length and the data did not match')
            finally:
                self.s.close()
    
    def receive_all(self, sock, n):
        data = bytearray()
        i=1
        while len(data) < n:
            print('packet number {:}'.format(i))
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
            i+=1
        return data.decode()
    
    def parse(self, message, kwargs=None):
        b=message.find('(')
        res=dict()
        if b==-1:
            res['type']='command'
            res['command']=message
        else:
            res['type']='command'
            first_part=message[:b]
            res['command']=first_part
            last_part=message[b:]
            assert last_part.endswith(')') and last_part.startswith('(')
            last_part=last_part[1:-1]
            assert last_part.find('(')==-1 and last_part.find(')')==-1
            data=last_part.split(',')
            args=[]
            if kwargs is None:
                kwargs=dict()
                for i in range(len(data)):
                    data[i]=data[i].lstrip('"').rstrip('"')
                    if data[i].find('=')!=-1:
                        k,v=data[i].split('=')
                        kwargs[k]=v
                    else:
                        args.append(data[i])
            res['args']=args
            res['kwargs']=kwargs
        msg=json.dumps(res)
        #print(msg)
        return msg
    
    def send_answer(self, conn, message, parsing=True):
        if parsing:
            message=self.parse(message)
        conn.sendall(('{:010x}'.format(len(message))+message).encode())
    
    def interpreter(self, conn, message):
        cmd = json.loads(message)
        #cmd['kwargs']['connection']=conn
        self.interprete.call(cmd, conn)
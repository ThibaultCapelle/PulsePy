# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:49:55 2020

@author: schli
"""

import json, socket

class Generic_Client:
    
    def __init__(self, ip=None, port=None):
        self.ip=ip
        self.port=port
        
    def send(self,message):
        #print('len : {:010x}'.format(len(message)))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.sendall(('{:010x}'.format(len(message))+message).encode())
    
    def receive_all(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        i=1
        while len(data) < n:
            #print('packet number {:}'.format(i))
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
            i+=1
        return data  
        
    def ask(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.sendall(('{:010x}'.format(len(message))+message).encode())
            raw_msglen = s.recv(10)
            msglen = int(raw_msglen.decode(),16)
            #print(msglen)
            data=self.receive_all(s, msglen)
            return json.loads(data)['content']
    
    def parse(self, message, kwargs=None, **keyargs):
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
            kwargs.update(keyargs)
            res['args']=args
            res['kwargs']=kwargs
        msg=json.dumps(res)
        #print(msg)
        return msg
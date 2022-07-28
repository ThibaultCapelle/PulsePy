# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 17:46:43 2020

@author: QMPL
"""

import struct, mmap
import sys
from ServerPy.server_base import Generic_Server
from ServerPy.client_base import Generic_Client
import socket
h_name = socket.gethostname()
IP_address = socket.gethostbyname(h_name+'.local')


class Server(Generic_Server):
    
    def __init__(self, ip=IP_address, port=9000):
        super().__init__(ip=ip, port=port, serial_driver=Driver())

class Client(Generic_Client):
    
    def __init__(self, ip=None, port=9000):
        super().__init__(ip=ip, port=port)
    
    def write_reg(self, adress_base=None, offset=None, bitmask=None, val=None):
        if val is None:
            return self.ask(self.parse('write_reg()', adress_base=adress_base,
                                offset=offset, bitmask=bitmask, val=val))
        else:
            self.send(self.parse('write_reg()', adress_base=adress_base,
                                offset=offset, bitmask=bitmask, val=val))
    
    def set_continuous_waveform(self,  waveform=None, duration=None,
                                frequency=None):
        self.send(self.parse('set_continuous_waveform()', waveform=waveform,
                             duration=duration, frequency=frequency))
    
    @property
    def trigger_delay(self):
        return self.write_reg(0x40200000, 0x240)/125e6
    
    @trigger_delay.setter
    def trigger_delay(self, val):
        FPGA_val=int(val*125e6)
        self.write_reg(0x40200000, 0x240, val=FPGA_val)
        
    @property
    def TTL_frequency(self):
        return 125e6/9/self.write_reg(0x40200000, 0x248)
    
    @TTL_frequency.setter
    def TTL_frequency(self, val):
        FPGA_val=int(125e6/9/val)
        self.write_reg(0x40200000, 0x248, val=FPGA_val)
    
    @property
    def VIn0(self):
        return self.write_reg(0x40400000, 0x0)/1904*3.3
    
    @property
    def VIn1(self):
        res=self.write_reg(0x40400000, 0x4)/1904*3.3
        return res
    
    @property
    def VIn2(self):
        res=self.write_reg(0x40400000, 0x8)/1904*3.3
        return res
    
    @property
    def VIn3(self):
        res=self.write_reg(0x40400000, 0xc)/1904*3.3
        return res
    
    @property
    def clk_source(self):
        ext=self.write_reg(0x40200000, 0x254)
        if ext==0:
            return 'internal'
        else:
            selection=self.write_reg(0x40200000, 0x250)
            if selection==0:
                return 'external 125MHz'
            elif selection==1:
                return 'external 10MHz'
    
    @clk_source.setter
    def clk_source(self, val):
        if val=='internal':
            self.write_reg(0x40200000, 0x254, val=0)
        elif val=='external 125MHz':
            self.write_reg(0x40200000, 0x250, val=0)
            self.write_reg(0x40200000, 0x254, val=1)
        elif val=='external 125MHz':
            self.write_reg(0x40200000, 0x250, val=1)
            self.write_reg(0x40200000, 0x254, val=1)
    
    @property
    def use_digital_mult(self):
        return self.write_reg(0x40300000, 0x14)==1
    
    @use_digital_mult.setter
    def use_digital_mult(self, val):
        self.write_reg(0x40300000, 0x14, val=int(val))

class Driver:
    
    def __init__(self):
        pass
            
    def write_reg(self, adress_base=None, offset=None, bitmask=None, val=None):
        if bitmask is None:
            bitmask=0xFFFFFFFF
        strbit='{:b}'.format(bitmask)
        bitmask_offset=0
        while(strbit[-bitmask_offset-1]=='0'):
            bitmask_offset+=1
        with open('/dev/mem', 'w+') as f:
            mm=mmap.mmap(f.fileno(), 4096, offset=adress_base)
            if val is None:
                mm=mm[offset:offset+4]
                res=struct.unpack('<L', mm)[0]
                return (res & bitmask)>>bitmask_offset
            else:
                val = int(val) << bitmask_offset
                res=struct.unpack('<L', mm[offset:offset+4])[0]
                new = res & (~bitmask) | (int(val) & bitmask)
                mm[offset:offset+4]=struct.pack('<L', new)
        
            
        
if __name__=='__main__':
    if len(sys.argv)>1:
        if sys.argv[1]=='server':
            if len(sys.argv)==2:
                s=Server()
        elif sys.argv[1]=='client':
            s=Client()
    else:
        s=Client()

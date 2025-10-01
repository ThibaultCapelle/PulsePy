# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 16:32:15 2022

@author: Thibault
"""


import importlib_resources
from pyrpl import Pyrpl
from time import sleep
import os
from paramiko import SSHException
from scp import SCPException
from pyrpl.attributes import BoolRegister, FloatRegister, SelectRegister, SelectProperty, \
                             IntRegister, LongRegister, PhaseRegister, FrequencyRegister, FloatProperty

from pyrpl.redpitaya import RedPitaya
from pyrpl import hardware_modules as rp

class PulseRedPitaya(RedPitaya):
    
    cls_modules= [rp.HK, rp.AMS, rp.Scope, rp.Sampler, rp.Asg0, rp.Asg1] + \
                  [rp.Pwm] * 2 + [rp.Iq] * 3 + [rp.Pid] * 3 + [rp.Trig] + [ rp.IIR]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class PulsePy(Pyrpl):
    
    @staticmethod
    def update_fpga(self, filename=None):
        if filename is None:
            try:
                source = self.parameters['filename']
            except KeyError:
                source = None
        else:
            source=filename
        self.end()
        sleep(self.parameters['delay'])
        self.ssh.ask('rw')
        sleep(self.parameters['delay'])
        self.ssh.ask('mkdir ' + self.parameters['serverdirname'])
        sleep(self.parameters['delay'])
        if source is None or not os.path.isfile(source):
            if source is not None:
                self.logger.warning('Desired bitfile "%s" does not exist. Using default file.',
                                    source)
        if not os.path.isfile(source):
            raise IOError("Wrong filename",
              "The fpga bitfile was not found at the expected location. Try passing the arguments "
              "dirname=\"c://github//pyrpl//pyrpl//\" adapted to your installation directory of pyrpl "
              "and filename=\"red_pitaya.bin\"! Current dirname: "
              + self.parameters['dirname'] +
              " current filename: "+self.parameters['filename'])
        for i in range(3):
            try:
                self.ssh.scp.put(source,
                             os.path.join(self.parameters['serverdirname'],
                                          self.parameters['serverbinfilename']))
            except (SCPException, SSHException):
                # try again before failing
                self.start_ssh()
                sleep(self.parameters['delay'])
            else:
                break
        # kill all other servers to prevent reading while fpga is flashed
        self.end()
        self.ssh.ask('killall nginx')
        self.ssh.ask('systemctl stop redpitaya_nginx') # for 0.94 and higher
        self.ssh.ask('cat '
                 + os.path.join(self.parameters['serverdirname'], self.parameters['serverbinfilename'])
                 + ' > //dev//xdevcfg')
        sleep(self.parameters['delay'])
        self.ssh.ask('rm -f '+ os.path.join(self.parameters['serverdirname'], self.parameters['serverbinfilename']))
        self.ssh.ask("nginx -p //opt//www//")
        self.ssh.ask('systemctl start redpitaya_nginx')  # for 0.94 and higher #needs test
        sleep(self.parameters['delay'])
        self.ssh.ask('ro')
        
    
    
    def __init__(self, config=None, source=None, **kwargs):
        super().__init__(config=config, source=source, **kwargs)
        self.rp.update_fpga=PulsePy.update_fpga.__get__(self.rp)
        '''self.rp.asg0._frequency_divide_1 = IntRegister(0x348,
                                                       address=0x40200000,
                                                       doc="""The internal clock is divided by this quantity before being outputed to N2.
            """)'''
    
    

p=Pyrpl('pulse1')
#p.rp.update_fpga(filename=file)
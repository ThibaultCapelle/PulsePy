# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 16:32:15 2022

@author: Thibault
"""

import paramiko
from scp import SCPClient

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    'rp-f0847a.local',
    username='root',
    password='root',
    port=15000,
    timeout=0.5)
channel = ssh.invoke_shell()
channel.send('ls -l')
rres=channel.recv(10)
#stdin, stdout, stderr = ssh.exec_command('ls -l')
ssh.close()
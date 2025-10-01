# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 13:35:43 2022

@author: Thibault
"""

from pyrpl.server import Client
c=Client('rp-f0847a.local')
#%%
from pyrpl import Pyrpl
p=Pyrpl('trigger_delay')
#%%
p.rp.asg0.cycles_per_burst=1
#%%
import numpy as np
asg0=p.rp.asg0
asg0.offset=0
dat=np.zeros(asg0.data_length)
dat[1:1000]=np.array([1-np.exp(-i*0.001) for i in range(999)])
asg0.data=dat
import matplotlib.pylab as plt
#plt.plot(asg0.data)
plt.figure()
plt.plot(dat)
#%%
from pyrpl import Pyrpl
p2=Pyrpl('sync_test')

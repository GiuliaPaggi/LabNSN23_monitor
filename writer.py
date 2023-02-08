# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 10:22:03 2023

@author: Giulia Paggi
"""

import time

f = open("data_23Nov_1.txt", "r")
lines= f.readlines()
f.close()

output = open("File.txt", "w")

for i in range(0, len(lines)):
    string = "_ "+lines[i]
    print(string)
    output.write(string)
    output.flush()
    time.sleep(.13)
    
output.close()
    
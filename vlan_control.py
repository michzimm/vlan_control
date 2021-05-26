#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import json
from netmiko import ConnectHandler
from multiprocessing import Process, Queue
from datetime import datetime
#from rtp_devices import device_list as devices
import sys
import csv


def get_time():
    current_time = str(datetime.now())
    return current_time

def config_vlan(action, device, commands, output_q):
    output_dict = {}
    net_connect = ConnectHandler(**device)
    hostname = net_connect.base_prompt
    if device['device_type'] == "cisco_ios":
        net_connect.enable()
    net_connect.config_mode()
    output = ('#' * 80) + "\n"
    output += net_connect.send_config_set(commands) + "\n"
    output += ('#' * 80) + "\n"
    net_connect.exit_config_mode()
    net_connect.send_config_set(['copy running-config startup-config'])
    if device['device_type'] == "cisco_ios":
        net_connect.exit_enable_mode()
    net_connect.disconnect()
    output_dict[hostname] = output
    output_q.put(output_dict)


output_q = Queue(maxsize=20)
procs = []


while True:
    action = input("Would you like to add or remove a network? [ add|remove ]: ")
    if action in ("add","Add","ADD","remove","Remove","REMOVE"):
        break
    else:
        print ("Invalid option entered, please retry...")

while True:
    site = input("At which site would you like to perform the action? [ sjc|rtp ]: ")
    if site in ["sjc","SJC"]:
        from sjc_devices import device_list as devices
        break
    elif site in ("rtp","RTP"):
        from rtp_devices import device_list as devices
        break
    else:
        print ("Invalid option entered, please retry...")

while True:
    file_option = input("Would you like to perform the action on a single network or use a file for multiple networks? [ single|file ]: ")
    if file_option in ("single","Single","SINGLE"):
        vlan_file = ""
        break
    elif file_option in ("file","File","FILE"):
        vlan_file = input("Enter the name of the VLAN file: ")
        break
    else:
        print ("Invalid option entered, please retry...")


vlan_list = []

if not vlan_file:
    vlan_id = input('Enter VLAN ID: ')
    print(vlan_id)
    if action == "add":
        vlan_name = input('Enter VLAN NAME: ')
        vlan_list.append([vlan_id,vlan_name])
    else:
        vlan_list.append([vlan_id])

if vlan_file:
    with open("./vlan_files/"+vlan_file) as g:
        reader = csv.reader(g)
        vlan_list = list(reader)

for vlan in vlan_list:
    if action == "add":
        print("Adding VLAN " + vlan[0] +" to all devices...")
        commands = [ \
            '\n', \
            'vlan ' + vlan[0], \
            'name ' + vlan[1], \
            ]
    elif action == "remove":
        print("Removing VLAN " + vlan[0] + " from all devices...")
        commands = [ \
            '\n', \
            'no vlan ' + vlan[0], \
            ]
    for device in devices:
        my_proc = Process(target=config_vlan, args=(action, device, commands, output_q))
        my_proc.start()
        procs.append(my_proc)

    for a_proc in procs:
        a_proc.join()

    while not output_q.empty():
        my_dict = output_q.get()
        for k, val in my_dict.items():
            print(k)
            print(val)

    if action == "add":
        print("Done adding VLAN " + vlan[0] + " to all devices.")
    elif action == "remove":
        print("Done removing VLAN " + vlan[0] + " from all devices.")

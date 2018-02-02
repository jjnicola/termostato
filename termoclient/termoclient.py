#!/usr/bin/python

import sys, getopt
from telnetlib import Telnet as tn
import time
import sqlite3

VERSION = "Termostato Client v0.1"

def getlog(host):
    try:
        soc = tn(host)
        soc.write(("GTL:000%").encode('ascii'))
        dret = soc.read_until(b'S')
        soc.close()
        return dret
    except:
        return False
        
def initcontroler(host):
    try:
        soc = tn(host)
        soc.write(("0000000%").encode('ascii'))
        time.sleep (10)
        soc.close()
        return True
    except:
        return False

def savedata(dret, batch_id):
    #format temperature
    print (dret)
    temp = float(dret[:-3])
    print (temp)
    status = int(dret[5:6])
    print (status)
    #format timestamp
    taux = time.localtime()
    log_date = str(taux.tm_year)+"-"+str(taux.tm_mon)+"-"+str(taux.tm_mday)+" "+str(taux.tm_hour)+":"+str(taux.tm_min)+":"+str(taux.tm_sec)
            
    conn = sqlite3.connect('../termoweb/termodb.sqlite3')
    c = conn.cursor()
    data = "INSERT INTO polls_fermentationlog (log_date, density, dev_status, batch_id, temperature) VALUES ('" + log_date + "',1048, " + str(status) + "," + str(batch_id) + "," + str(temp) + ")"
    #print(data)
    c.execute(data)
    conn.commit()
    conn.close()
    
def help():
    print (VERSION)
    print ("")
    print ("\t-h <ip-address> | --host=<ip-address>              : IP address of the device.")
    print ("\t-n <new-batch-name> | --new-batch=<new-batch-name> : It creates a new Batch in the database with given name.")
    print ("\t-b <batch-id> | --batch-id=<batch-number>          : Batch's ID. Usefull to reconnect in case of problem and continuing loading.")
    print ("\t-s <> | --style=[0-8]                              : It change the current style on the device.")
    print ("\t-H | --help                                        : This help.")
    print ("\t-V | --version                                     : Show version.")
    print ("\t-v <> | --verbose                                  : Verbose enabled.")
    print ("")
    
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"h:n:b:s:HVv",["host=","new-batch=","style=","batch-id=", "help","verbose","version"])
    except getopt.GetoptError:
        print ('datawriter.py -H|--help for help.')
        sys.exit(2)

    verbose = False
    new_batch = False
    style = 0
    batch_id = False
    host = False
    for o, a in opts:
        if o in ("-H", "--help"):
            help ()
            sys.exit()
        elif o in ("-V", "--version"):
            print (VERSION)
            sys.exit()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--new-batch"):
            new_batch = a
        elif o in ("-s", "--style"):
            style = a
        elif o in ("-b", "--batch-id"):
            batch_id = a
        elif o in ("-h", "--host"):
            host = a

    if host is False or batch_id is False:
        print ("Error: run the program with a host and batch-id.")
        print ('datawriter.py -H|--help for more info.')
        sys.exit()
           
   
    if new_batch is not False:
        if batch_id == None:
            print ("ERROR: missing arguments");
            print ("ERROR: Use");
            print ("TODO: Check for a existent batch id and create batch")
            
        taux = time.localtime()
        log_date = str(taux.tm_year)+"-"+str(taux.tm_mon)+"-"+str(taux.tm_mday)+" "+str(taux.tm_hour)+":"+str(taux.tm_min)
        
        conn = sqlite3.connect('../termoweb/termodb.sqlite3')
        c = conn.cursor()
        data = "INSERT INTO polls_batchinfo VALUES ('1','"+chartname+"','colorada',"+log_date+")"
        c.execute(data)
        conn.commit()
        
    ret = initcontroler(host)
    while ret is False:
        print ("ERROR: It was not possible to init the controller")
        ret = initcontroler(host)
        
    while (1):
        data = getlog(host)
            
        if data is not False:
            savedata(data)
        
        time.sleep (10)
                

    
if __name__ == "__main__":
   main(sys.argv[1:])

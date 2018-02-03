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

def get_bid_from_bnumber(batch_number):

    conn = sqlite3.connect('../termoweb/termodb.sqlite3')
    c = conn.cursor()
    data = "select id from polls_batchinfo where batch_number = "+ str(batch_number)
    c.execute(data)
    return int(c.fetchone()[0])

def savedata(dret, batch_id):
    #format temperature
    temp = float(dret[:-3])
    status = int(dret[5:6])
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

def get_last_batch_number():

    conn = sqlite3.connect('../termoweb/termodb.sqlite3')
    c = conn.cursor()
    data = "select batch_number from polls_batchinfo order by batch_number desc limit 1"
    c.execute(data)
    return int(c.fetchone()[0])

def check_batch_number(bnumber):
    ret = None
    conn = sqlite3.connect('../termoweb/termodb.sqlite3')
    c = conn.cursor()
    data = "select batch_number from polls_batchinfo where batch_number = " +str(bnumber)
    c.execute(data)
    ret = c.fetchall()
    if not ret:
        return False
    else:
        return True

def create_new_batch (name, bnumber, style):
    taux = time.localtime()
    log_date = str(taux.tm_year)+"-"+str(taux.tm_mon)+"-"+str(taux.tm_mday)+" "+str(taux.tm_hour)+":"+str(taux.tm_min)

    conn = sqlite3.connect('../termoweb/termodb.sqlite3')
    c = conn.cursor()
    data = "INSERT INTO polls_batchinfo (batch_number, batch_name, batch_style, batch_date) VALUES ("+str(bnumber)+",'"+name+"','"+style+"','"+log_date+"')"
    c.execute(data)
    conn.commit()


def help():
    print (VERSION)
    print ("")
    print ("\t-h <ip-address> | --host=<ip-address>              : IP address of the device.")
    print ("\t-n <new-batch-name> | --new-batch=<new-batch-name> : It creates a new Batch in the database with given name.")
    print ("\t-b <batch-number> | --batch-number=<batch-number>  : Batch's number. Usefull to reconnect in case of problem and continuing loading, or the number for the new batch.")
    print ("\t-s <style-name> | --style=<style-name>             : It style name for the new batch .")
    print ("\t-H | --help                                        : This help.")
    print ("\t-V | --version                                     : Show version.")
    print ("\t-v | --verbose                                     : Verbose enabled.")
    print ("")

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"h:n:b:s:HVv",["host=","new-batch=","style=","batch-number=", "help","verbose","version"])
    except getopt.GetoptError:
        print ('Error in given arguments. Try datawriter.py -H|--help for help.')
        sys.exit(2)

    verbose = False
    new_batch = False
    style = False
    batch_number = False
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
        elif o in ("-b", "--batch-number"):
            batch_number = a
        elif o in ("-h", "--host"):
            host = a

    if host is False:
        print ("ERROR: I need the host name or an IP address.")
        print ("Remember to give a batch id or create a new batch.")
        print ("\ndatawriter.py -H|--help for more info.\n")
        sys.exit()

    if batch_number == False and new_batch is False:
        print ("ERROR: Missing arguments.");
        print ("Hint: Run the program with a batch id to add log data to the current batch:");
        print ("\tThe last batch id is " + str(get_last_batch_number()))
        print ("Or create a new batch.")
        print ("\nFor more info run the program with -H or --help option.\n")
        sys.exit()

    if batch_number is not False:
        isbatchid = check_batch_number(batch_number)

    if new_batch is not False:
        if batch_number is False:
            batch_number = get_last_batch_number() + 1
        elif isbatchid is True:
            print ("ERROR: the given batch number exist and it can not be aplied to a new batch.")
            sys.exit()

        if style is False:
            style = "default"
        print ("\nThe new batch will be created in the database with the following information:")
        print ("\tBatch ID:\t" + str(batch_number))
        print ("\tBatch Name:\t" + new_batch)
        print ("\tBatch Style:\t" + style)

        answer = ""
        while (answer not in ("y","n")):
            print ("Is this information right? (y/n)")
            answer = sys.stdin.read(1)

        if answer.lower() == "y":
            create_new_batch(new_batch, batch_number, style)
            print ("The new batch was created")
        elif answer.lower() == "n":
            print ("Batch creation aborted. Bye bye!")
            sys.exit()
    elif isbatchid is False:
        print ("ERROR: the given batch number does not exist. Please give a right one or create a new batch.")
        sys.exit()
    elif isbatchid is True:
        answer = ""
        while (answer not in ("y","n")):
            print ("Are you sure you want to add log entries to the batch number " + str(batch_number) +"? (y/n)")
            answer = sys.stdin.read(1)
        if answer.lower() == "n":
            print ("Bye bye!")
            sys.exit()

    print ("Starting")

    ret = initcontroler(host)
    while ret is False:
        print ("ERROR: It was not possible to init the controller")
        ret = initcontroler(host)

    while (1):
        data = getlog(host)

        batch_id = get_bid_from_bnumber(batch_number)
        if data is not False:
            savedata(data, batch_id)

        time.sleep (10)

if __name__ == "__main__":
   main(sys.argv[1:])

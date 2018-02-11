#!/usr/bin/python

import sys, getopt
import signal, os
import traceback
import time
from daemonize import Daemonize
import logging

import sqlite3
from telnetlib import Telnet as tn


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("/tmp/test.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]


VERSION = "Termostato Client v0.1"
pid = "/tmp/test.pid"
#batch_id = False
#host = False

class TermoComm():

    def NewConn(self, host):
        logger.debug("new telnet connection")

        try:
            soc = tn(host)
            return soc
        except EOFError as er:
            logger.debug ("Error OS in TermoComm Class: {0}".format(err))

    def GetLog(self, soc):
        try:
            soc.write(("GTL:000%").encode('ascii'))
            dret = soc.read_until(b'S')
            return dret
        except EOFError as er:
            logger.debug ("Error OS in TermoComm Class: {0}".format(err))
            return False

    def InitController(self, soc):
        try:
            soc.write(("0000000%").encode('ascii'))
            time.sleep (10)
            return True
        except EOFError as er:
            logger.debug ("Error OS in TermoComm Class: {0}".format(err))
            return False

    def CloseConn(self, soc):
        soc.close()

class TermoSql():

    def NewDB(self):
        logger.debug("new db")
        try:
            dbconn = sqlite3.connect('../termoweb/termodb.sqlite3')
            logger.debug("new db: "+str(dbconn))
            return dbconn
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])

    def CloseDB(self,dbconn):
        dbconn.close()

    def Getbidfrombnumber(self, dbconn ,batch_number):
        '''Get the batch id from the db using the batch number'''
        try:
            c = dbconn.cursor()
            data = "select id from polls_batchinfo where batch_number = "+ str(batch_number)
            c.execute(data)
            return int(c.fetchone()[0])
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])

    def SaveData(self, dbconn, dret, batch_id):
        try:
            temp = float(dret[:-3])
            status = int(dret[5:6])
            taux = time.localtime()
            log_date = (str(taux.tm_year)+"-"+str(taux.tm_mon)+"-"+
                       str(taux.tm_mday)+" "+str(taux.tm_hour)+
                       ":"+str(taux.tm_min)+":"+str(taux.tm_sec))
            c = dbconn.cursor()
            data = "INSERT INTO polls_fermentationlog(log_date, density, dev_status, batch_id, temperature) VALUES ('" + log_date + "',1048," + str(status) + "," + str(batch_id) + "," + str(temp) + ")"
            c.execute(data)
            dbconn.commit()
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])


    def GetLastBatchNumber(self,dbconn):

        try:
            c = dbconn.cursor()
            data = "select batch_number from polls_batchinfo order by batch_number desc limit 1"
            c.execute(data)
            return int(c.fetchone()[0])
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])

    def CheckBatchNumber(self, dbconn, bnumber):
        try:
            c = dbconn.cursor()
            data = "select batch_number from polls_batchinfo where batch_number = " +str(bnumber)
            c.execute(data)
            ret = c.fetchall()
            if not ret:
                return False
            else:
                return True
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])

    def CreateNewBatch (self, dbconn, name, bnumber, style):
        try:
            taux = time.localtime()
            log_date = str(taux.tm_year)+"-"+str(taux.tm_mon)+"-"+str(taux.tm_mday)+" "+str(taux.tm_hour)+":"+str(taux.tm_min)
            c = dbconn.cursor()
            data = "INSERT INTO polls_batchinfo (batch_number, batch_name, batch_style, batch_date) VALUES ("+str(bnumber)+",'"+name+"','"+style+"','"+log_date+"')"
            c.execute(data)
            dbconn.commit()
        except sqlite3.Error as e:
            logger.debug ("Error OS in TermoSql Class:", e.args[0])

def mainloop():
    logger.debug("main loop")
    host = "192.168.0.44"
    batch_number = 97
    logger.debug(host)
    #if host is False:
    #    logger.debug("No host")
    #    sys.exit(1)
    #if batch_number is False:
    #    logger.debug("No batch")
    #    sys.exit(1)

    soc = False
    while soc is False:
        try:
            logger.debug("trying to connect")

            newcontroller = TermoComm()
            soc = newcontroller.NewConn(host)
            logger.debug("new db")
            logger.debug("soc: "+ str(soc))

        except:
            logger.debug("ERROR: error en la clase TermoComm")

    ret = False
    while ret is False:
        try:
            ret = newcontroller.InitController(soc)
            logger.debug("controller initialized: ")
        except:
            logger.debug("ERROR: error en la clase TermoComm")

    logger.debug("Starting data logging.")

    dbconn = False
    while dbconn is False:
        try:
            sqlquery = TermoSql()
            dbconn = sqlquery.NewDB()
            logger.debug("Connected to the DB: " + str(dbconn))
            batch_id = sqlquery.Getbidfrombnumber(dbconn, batch_number)
            if batch_id is None:
                logger.debug("Impossible to find a batch_id for the batch number " + str(batch_number))
                sys.exit(1)
            else:
                logger.debug("Starting to log data for the batch number #"+str(batch_number)+" (id"+str(batch_id)+")")
        except:
            logger.debug("ERROR: Not possible to connect to the DB.")

    #Start Infinite loop
    while True:
        data = False
        try:
            data = newcontroller.GetLog(soc)
            logger.debug("Retrieved data: " + data)
        except:
            logger.debug("ERROR: Connection error. Not possible to retrive data.")

        try:
            if data is not False:
                sqlquery.SaveData(dbconn, data, batch_id)
        except:
            logger.debug("ERROR: Not possible to save data in the DB. Retrying in 10 seconds.")
        time.sleep (10)

def help():
    '''Print the help.'''
    print (VERSION)
    print ("")
    print ("\t-h <ip-address> | --host=<ip-address>              : IP address of the device.")
    print ("\t-n <new-batch-name> | --new-batch=<new-batch-name> : It creates a new Batch in the database with given name.")
    print ("\t-b <batch-number> | --batch-number=<batch-number>  : Batch's number. Usefull to reconnect in case of problem and continuing loading, or the number for the new batch.")
    print ("\t-s <style-name> | --style=<style-name>             : It style name for the new batch .")
    print ("\t-H | --help                                        : This help.")
    print ("\t-V | --version                                     : Show version.")
    print ("\t-v | --verbose                                     : Verbose enabled.")
    print ("\t-f | --foreground                                  : Not daemonize. Keep in foreground for debugging pourposes.")
    print ("")


def main(argv):

    try:
        opts, args = getopt.getopt(argv,"h:n:b:s:HVvf",["host=","new-batch=","style=","batch-number=", "help","verbose","version","foreground"])
    except getopt.GetoptError:
        print ('Error in given arguments. Try datawriter.py -H|--help for help.')
        sys.exit(2)

    verbose = False
    new_batch = False
    style = False
    batch_number = False
    host = False
    foreground = False
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
        elif o in ("-f", "--foreground"):
            foreground = True
            print ("The process will not be demonized for debugging pourposes.")

    if host is False:
        print ("ERROR: I need the host name or an IP address.")
        print ("Remember to give a batch id or create a new batch.")
        print ("\ndatawriter.py -H|--help for more info.\n")
        sys.exit()

    sqlquery = TermoSql()
    dbconn = sqlquery.NewDB()
    if batch_number is False and new_batch is False:
        print ("ERROR: Missing arguments.");
        print ("Hint: Run the program with a batch id to add log data to the current batch:");
        print ("\tThe last batch id is " + str(sqlquery.GetLastBatchNumber(dbconn)))
        print ("Or create a new batch.")
        print ("\nFor more info run the program with -H or --help option.\n")
        sys.exit()

    if batch_number is not False:
        isbatchid = sqlquery.CheckBatchNumber(dbconn, batch_number)

    if new_batch is not False:
        if batch_number is False:
            batch_number = sqlquery.GetLastBatchNumber(dbconn) + 1
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
            sqlquery.CreateNewBatch(dbconn, new_batch, batch_number, style)
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
    sqlquery.CloseDB(dbconn)
    if foreground is True:
        newdaemon = Daemonize(app="termoclient",
                              pid=pid,
                              action=mainloop,
                              keep_fds=keep_fds,
                              foreground=True, verbose=True,
                              chdir = os.getcwd())

    else:
        newdaemon = Daemonize(app="termoclient",
                              pid=pid,
                              action=mainloop,
                              keep_fds=keep_fds,
                              foreground=False, verbose=True,
                              chdir = os.getcwd())
    newdaemon.start()


if __name__ == "__main__":
   main(sys.argv[1:])

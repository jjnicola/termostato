#!/usr/bin/python

import sys, getopt
import signal, os
import socket
import select
import traceback
import time
from daemonize import Daemonize
import logging

import sqlite3
from telnetlib import Telnet as tn



VERSION = "Termostato Client v0.1"
pid = "/tmp/test1.pid"
server_address = '/tmp/termoclient.sock'

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

def mainloop(host, batch_number):

    logger.debug("main loop")
    logger.debug(host)

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

        # Make sure the socket does not already exist
        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise

    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    print >>sys.stderr, 'starting up on %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(5)
    read_list = [server_socket]

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

        # Check for client connection to set the device.
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is server_socket:
                client_socket, address = server_socket.accept()
                read_list.append(client_socket)
                print "Connection from", address
            else:
                data = s.recv(1024)
                if data:
                    print ("server recv: %s", data)
                    #s.send(data)
                else:
                    s.close()
                    read_list.remove(s)

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
    print ("\t-c <dev config> | --config=<dev-config>            : Set the device to a beer profile with predefined temperatures")
    print ("                                                       or a custom one. Also to reset the device.")
    print ("\t List of profiles: ")
    print ("\t\t 0 = MADURACION 0C")
    print ("\t\t 1 = LAGER 10C")
    print ("\t\t 2 = KOLSCH 15C")
    print ("\t\t 3 = SCOTTISH 16C")
    print ("\t\t 4 = ENGLISH 18C")
    print ("\t\t 5 = WEIZEN 19C")
    print ("\t\t 6 = BELGA 20C")
    print ("\t\t 7 = CUSTOM 0-25C")
    print ("")
    print ("\t\t Example 1: for a belga profile: --config STY:006")
    print ("\t\t Example 2: for a Maduration profile: --config STY:000")
    print ("\t\t Example 3: to reset de device: --config RST:000")
    print ("\t\t Example 4: for a custom Temp 18.5C: --config TMP:185")
    print ("")


def main(argv):

    try:
        opts, args = getopt.getopt(argv,"h:n:b:s:HVvfc:",["host=","new-batch=","style=","batch-number=", "help","verbose","version","foreground","config="])
    except getopt.GetoptError:
        print ('Error in given arguments. Try datawriter.py -H|--help for help.')
        sys.exit(2)

    verbose = False
    new_batch = False
    style = False
    batch_number = False
    host = False
    foreground = False
    dev_set = False
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
        elif o in ("-c", "--config"):
            dev_set = a

    if server == 0:
        if dev_set is True:
            print ("ERROR: Arguments needed to set the device.")
            print("If you think this is an error, look for a running process, socket file or pid file")
            sys.exit()

        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        print >>sys.stderr, 'connecting to %s' % server_address
        try:
            sock.connect(server_address)
        except socket.error, msg:
            print >>sys.stderr, msg
            sys.exit(1)

        try:
            # Send data
            message = 'This is the message.  It will be repeated.'
            print >>sys.stderr, 'sending "%s"' % dev_set
            sock.sendall(dev_set)

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                print >>sys.stderr, 'received "%s"' % data
        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()


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
                              action=None,
                              keep_fds=keep_fds,
                              foreground=True, verbose=True,
                              chdir = os.getcwd())

    else:
        newdaemon = Daemonize(app="termoclient",
                              pid=pid,
                              action=None,
                              keep_fds=keep_fds,
                              foreground=False, verbose=True,
                              chdir = os.getcwd())
    newdaemon.start()
    mainloop(host, batch_number)


if __name__ == "__main__":

    # Check if it is already running.
    if os.path.isfile(server_address):
        server = 1 #Becomes a server
    else:
        server = 0 #Becomes a client

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fh = logging.FileHandler("/tmp/test1.log", "w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]

    main(sys.argv[1:])

import argparse
import math
import time
import datetime
import mysql.connector

from pythonosc import dispatcher
from pythonosc import osc_server


def eeg_handler(unused_addr, args, ch1, ch2="", ch3="", ch4="", ch5=""):
    #print("EEG (uV) per channel: ", ch1, ch2, ch3, ch4, ch5)
    print( str(datetime.datetime.utcnow()), ch1, ch2, ch3, ch4, ch5)
    #print( str(datetime.datetime.utcnow()), ch1 )

alph = 0
beta = 0
gamm = 0
delt = 0
thet = 0
packet_counter = 0
timestamp = 0
cnx = mysql.connector.connect(user='root', database='brainwave_freq')
cursor = cnx.cursor()
add_entry = ("INSERT INTO bands (alpha, beta, gamma, delta, theta, timestamp) VALUES (%s, %s, %s, %s, %s, %s)" )

def init_freq_globals():
    global alph, beta, gamm, delt, thet, packet_counter, timestamp
    alph = 0
    beta = 0
    gamm = 0
    delt = 0
    thet = 0
    packet_counter = 5
    timestamp = 0

def freq_handler(unused_addr, args, ch1 ):
    global alph, beta, gamm, delt, thet, packet_counter, timestamp, cnx, cursor, add_entry
    if args[0] is 'alpha':
        # We expect alpha packet to arrive first
        init_freq_globals()
        alph = ch1
        timestamp = time.time()
        packet_counter -= 1
    elif args[0] is 'beta':
        beta = ch1
        packet_counter -=1
    elif args[0] is 'delta':
        delt = ch1
        packet_counter -=1
    elif args[0] is 'theta':
        thet = ch1
        packet_counter -=1
    elif args[0] is 'gamma':
        gamm = ch1
        packet_counter -=1
        if packet_counter is not 0:
            print( "Somehow a packet was dropped!" )
        #print( str(datetime.datetime.utcnow()), str('ABDTG'), alph, beta, delt, thet, gamm )
        #print( timestamp, alph, beta, delt, thet, gamm )
        data_entry = ( alph, beta, gamm, delt, thet, timestamp ) 
        cursor.execute( add_entry, data_entry )
        cnx.commit()
    else:
        print( "FAIL" )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.3",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=5000,
                        help="The port to listen on")
    parser.add_argument("--source",
                        #type=text,
                        default="/muse/eeg",
                        help="The Muse channel to listen for")
    args = parser.parse_args()

    # TODO: different channels have different # of parameters.

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/debug", print)
    # short-circuting user selected channels to bring you all freq bands all the time
    #dispatcher.map("{}".format(args.source), eeg_handler, "EEG")
    dispatcher.map("/muse/elements/alpha_absolute", freq_handler, "alpha")
    dispatcher.map("/muse/elements/beta_absolute",  freq_handler, "beta")
    dispatcher.map("/muse/elements/gamma_absolute", freq_handler, "gamma")
    dispatcher.map("/muse/elements/delta_absolute", freq_handler, "delta")
    dispatcher.map("/muse/elements/theta_absolute", freq_handler, "theta")

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

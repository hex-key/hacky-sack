from tinydb import TinyDB, Query

db = TinyDB("db.json")

db.insert({"func": "compliments", "data": []})
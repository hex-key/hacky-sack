from tinydb import TinyDB, Query

db = TinyDB("db.json")
query = Query()

def get_db(name:str):
    return db.get(query.func == name)
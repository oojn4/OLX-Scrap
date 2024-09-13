from pymongo import MongoClient
from dotenv import dotenv_values

# Setup MongoDB Connection
config = dotenv_values("../.env")
client = MongoClient( config["HOST_MONGO"],
                     username=config["USER_MONGO"],
                     password=config["PSWD_MONGO"],
                     authMechanism='SCRAM-SHA-256')
# Setup DB
mongo = client["olx"]
# Setup Collections
provinsi_collection = "olx_property_provinsi"
kabkot_collection   = "olx_property_kabkot"
kecamatan_collection= "olx_property_kecamatan"
property_collection = "olx_property"

def count_mongo(collection_name):
    collection = mongo[collection_name]
    return len(list(collection.find()))

def replace_collection(collection_name):
    collection = mongo[collection_name]
    collection.drop()

def insert_mongo(data,collection_name,replace=False):
    collection = mongo[collection_name]
    if replace:
        collection.drop() # recreate
    collection.insert_many(data)

def read_job(collection_name=kecamatan_collection):
    collection = mongo[collection_name]
    return collection.find()
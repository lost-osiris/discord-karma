from pymongo import MongoClient
from bot import Bot
import json

def get_config():
   target = open("config.json")
   config = json.load(target)
   return config

def setup_db(config):
   mongo_user = config['mongo-user']
   mongo_password = config['mongo-password']
   mongo_servers = config['mongo-servers']
   mongo_db = config['mongo-db']
   mongo_options = config['mongo-options']

   mongo_url = "mongodb://%s:%s@%s/%s?%s" % (mongo_user, mongo_password, ','.join(mongo_servers), mongo_db, mongo_options)

   return MongoClient(mongo_url, socketKeepAlive=True)[mongo_db]

if __name__ == "__main__":
   config = get_config()
   mongo = setup_db(config)
   token = config['token']

   bot = Bot(mongo, config)
   bot.run()

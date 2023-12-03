# (c) @AbirHasan2005

from config import Config
from helpers.databases.database import Database

db = Database(Config.DATABASE_URL, Config.SESSION_NAME)

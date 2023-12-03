# (c) @AbirHasan2005

from configs import Config
from helpers.database.database import Database

db = Database(Config.DATABASE_URL, Config.SESSION_NAME)

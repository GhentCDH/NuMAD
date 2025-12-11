from .config import DB_STRING

import sqlmodel

engine = sqlmodel.create_engine(DB_STRING)

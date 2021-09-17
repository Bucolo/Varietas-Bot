import asyncpg

import botconfig

class Database:
    def __init__(self):
        self.__version__ = "0.0.1"

    async def get_connection(self):
        return await asyncpg.connect(botconfig.PSQL_URI)

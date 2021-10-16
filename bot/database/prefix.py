class PrefixDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def get(self, guild):
        conn = await self.dbConnection.get_connection()
        x = await conn.fetchrow("SELECT prefix FROM prefix WHERE guild=$1", guild)
        await conn.close()
        return x

    async def add(self, guild, prefix):
        conn = await self.dbConnection.get_connection()
        await conn.execute("INSERT INTO prefix(guild, prefix) VALUES ($1, $2)", guild, prefix)
        await conn.close()
    
    async def update(self, guild, prefix):
        conn = await self.dbConnection.get_connection()
        await conn.execute("UPDATE prefix SET prefix=$1 WHERE guild=$2", prefix, guild)
        await conn.close()
    
    async def remove(self, guild):
        conn = await self.dbConnection.get_connection()
        await conn.execute("DELETE FROM prefix WHERE guild=$1", guild)
        await conn.close()
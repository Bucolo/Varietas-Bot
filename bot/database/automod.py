class AutoModDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def add(self, guild, word):
        conn = await self.dbConnection.get_connection()
        
        await conn.execute("INSERT INTO automod(guild, word) VALUES ($1, $2)", guild, word)
        await conn.close()
    
    async def get(self, guild):
        conn = await self.dbConnection.get_connection()
        
        x = await conn.fetch("SELECT word FROM automod WHERE guild=$1", guild)
        
        await conn.close()
        
        return x
    
    async def remove(self, guild, word):
        conn = await self.dbConnection.get_connection()
        
        await conn.execute("DELETE FROM automod WHERE word=$1 AND guild=$2", word, guild)
        await conn.close()

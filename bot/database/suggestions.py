class SuggestDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def get(self, guild):
        con = await self.dbConnection.get_connection()
        res = await con.fetch("SELECT channel FROM suggestions WHERE guild=$1", guild)
        await con.close()
        return res

    async def set(self, channel, guild):
        con = await self.dbConnection.get_connection()
        await con.execute("INSERT INTO suggestions (channel, guild) VALUES ($1, $2)", channel, guild)
        await con.close()

    async def delete(self, guild):
        con = await self.dbConnection.get_connection()
        await con.execute("DELETE FROM suggestions WHERE guild=$1", guild)
        await con.close()
    
    async def update(self, channel, guild):
        con = await self.dbConnection.get_connection()
        await con.execute("UPDATE suggestions SET channel = $1 WHERE guild = $2", channel, guild)
        await con.close()

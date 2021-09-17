class CasesDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
        
    async def get_muted_role(self, guild_id):
        db = await self.dbConnection.get_connection()
        muted_id = await db.fetch("SELECT muted_role FROM guild_config WHERE guild_id=$1", int(guild_id))
        await db.close()
        return int(muted_id[0][0])

    async def case_add(self, case_type, guild_id, user_id, reason, expiration_date):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO cases(case_type, guild_id, user_id, reason, expiration_date) "
                         "VALUES ($1, $2, $3, $4, $5)",
                         case_type, guild_id, user_id, reason, expiration_date)
        await db.close()
        
    

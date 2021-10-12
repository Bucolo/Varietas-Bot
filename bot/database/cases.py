import datetime

class CasesDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
        
    async def add_muted_role(self, guild_id, muted_id):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO guild_config(guild_id, muted_role) VALUES ($1, $2)", guild_id, muted_id)
        
    async def get_muted_role(self, guild_id):
        db = await self.dbConnection.get_connection()
        muted_id = await db.fetch("SELECT muted_role FROM guild_config WHERE guild_id=$1", int(guild_id))
        await db.close()
        return int(muted_id[0]["muted_role"])

    async def case_add(self, case_type, guild_id, user_id, reason, expiration_date):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO cases(case_type, guild_id, user_id, reason, expiration_date) "
                         "VALUES ($1, $2, $3, $4, $5)",
                         case_type, guild_id, user_id, reason, expiration_date)
        await db.close()
        
    async def case_remove(self, case_type, guild_id, user_id, reason, expiration_date):
        db = await self.dbConnection.get_connection()
        try:
            await db.execute("DELETE FROM cases WHERE case_type=$1 and guild_id=$2 and user_id=$3 and reason=$4 and expiration_date=$5",
                            case_type, guild_id, user_id, reason, expiration_date)
            await db.close()
        except Exception as e:
            print(e)
            return

    async def get(self, user_id, guild_id):
        db = await self.dbConnection.get_connection()
        res = await db.fetch(f"SELECT * FROM cases where user_id=$1 AND guild_id=$2", user_id, guild_id)
        await db.close()
        return res
        
    async def get_outdated(self):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT * FROM cases WHERE expiration_date <= $1", str(datetime.datetime.utcnow()))
            await db.close()
        except Exception as e:
            print(e)
            return None
        return x

    async def delete(self, guild_id):
        db = await self.dbConnection.get_connection()
        try:
            await db.execute("DELETE FROM cases WHERE guild_id = $1", guild_id)
        except Exception:
            return None

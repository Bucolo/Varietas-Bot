# CREATE TABLE log_config(
#   channel_logs bigint,
#   server_logs bigint,
#   member_logs bigint,
#   message_logs bigint,
#   voice_logs bigint,
#   guild bigint
# )

class EventDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def get(self, guild):
        db = await self.dbConnection.get_connection()
        res = await db.fetch("SELECT * FROM log_config WHERE guild=$1", guild)
        await db.close()
        return res

    async def add(self,
                  channel_logs=None,
                  server_logs=None,
                  member_logs=None,
                  user_logs=None,
                  message_logs=None,
                  voice_logs=None,
                  guild=None):
        if guild is None:
            raise SyntaxError("Cannot have guild equal to none")
        
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO log_config(channel_logs, server_logs, member_logs, user_logs, message_logs, voice_logs, guild) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                   channel_logs, server_logs, member_logs, user_logs, message_logs, voice_logs, guild)
        await db.close()
    
    async def update(self,
                  channel_logs=None,
                  server_logs=None,
                  member_logs=None,
                  user_logs=None,
                  message_logs=None,
                  voice_logs=None,
                  guild=None):
        if guild is None:
            raise SyntaxError("Cannot have guild equal to none")
        
        db = await self.dbConnection.get_connection()
        await db.execute("UPDATE log_config SET channel_logs=$1, server_logs=$2, member_logs=$3, user_logs=$4, message_logs=$5, voice_logs=$6 WHERE guild=$7",
                   channel_logs, server_logs, member_logs, user_logs, message_logs, voice_logs, guild)
        await db.close()

    async def remove(self, guild):
        db = await self.dbConnection.get_connection()
        await db.execute("DELETE FROM log_config WHERE guild=$1", guild)
        await db.close()

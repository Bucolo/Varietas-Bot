class TicketDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def add(self, guild_id, category, message_id, roles):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO ticketpanels(guild_id, category, message_id, roles) VALUES ($1, $2, $3, $4)", guild_id, category, message_id, roles)
        await db.close()

    async def get(self, message_id):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT category, roles FROM ticketpanels WHERE message_id=$1", message_id)
            await db.close()
        except:
            return []
        return x
    
    async def remove(self, message_id):
        db = await self.dbConnection.get_connection()
        await db.execute("DELETE FROM ticketpanels WHERE message_id=$1", message_id)
        await db.close()
        
    async def edit(self, attr, new_value):
        db = await self.dbConnection.get_connection()
        if attr.lower() == "category":
            attr = "category"
        elif attr.lower() == "messageid" or "message_id" or "message id":
            attr = "message_id"
        elif attr.lower() == "roles":
            attr = "roles"
        try:
            await db.execute(f"UPDATE ticketpanels SET {attr} = {new_value}")
            await db.close()
        except:
            return
        
    async def add_ticket(self, guild_id, channel_id, member):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO tickets(guild_id, channel_id, member) VALUES ($1, $2, $3)", guild_id, channel_id, member)
        await db.close()
        
    async def add_log_channel(self, chan_id, guild_id):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT * FROM log_config WHERE guild=$1", guild_id)
            if x == []:
                await db.execute("INSERT INTO log_config(guild, ticket_logs) VALUES ($1, $2)", guild_id, chan_id)
                await db.close()
                return
            await db.execute("UPDATE log_config SET ticket_logs = $1 WHERE guild = $2", chan_id, guild_id)
            await db.close()
        except Exception as e:
            print(e)
        
    async def get_log_channel(self, guild_id):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT ticket_logs FROM log_config WHERE guild=$1", guild_id)
            await db.close()
        except:
            return None
        return x
    
    async def get_member(self, chan_id):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT member FROM tickets WHERE channel_id=$1", chan_id)
            await db.close()
        except:
            return None
        return x
    
    async def delete_ticket(self, chan_id):
        db = await self.dbConnection.get_connection()
        try:
            await db.execute("DELETE FROM tickets WHERE channel_id=$1", chan_id)
        except:
            return
    

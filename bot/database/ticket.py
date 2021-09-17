class TicketDB:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection
    
    async def add(self, category, message_id, roles):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO tickets(category, message_id, roles) VALUES ($1, $2, $3)", category, message_id, roles)
        await db.close()

    async def get(self, message_id):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT category, roles FROM ticket WHERE message_id=$1", message_id)
            await db.close()
        except:
            return []
        return x
    
    async def remove(self, message_id):
        db = await self.dbConnection.get_connection()
        await db.execute("DELETE FROM tickets WHERE message_id=$1", message_id)
        await db.close()
    
    async def get_code(self, code):
        db = await self.dbConnection.get_connection()
        try:
            x = await db.fetch("SELECT * from ticket_validation WHERE code=$1", code)
            await db.close()
        except:
            return []

        return x
    
    async def set_code(self, status, code):
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO ticket_validation(code, \"status\") VALUES ($1, $2)", code, status)
        await db.close()

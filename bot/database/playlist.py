class DBPlaylist:
    def __init__(self, dbConnection):
        self.dbConnection = dbConnection

    async def add(self, user, name, title, link):
        """Add a song to a playlist"""
        db = await self.dbConnection.get_connection()
        await db.execute("INSERT INTO playlist(\"user\", name, title, link) VALUES ($1, $2, $3, $4)", user, name, title, link)
        await db.close()

    async def countSongs(self, user, name):
        db = await self.dbConnection.get_connection()
        res = await db.fetch("SELECT COUNT(*) FROM playlist WHERE \"user\"=$1 AND name=$2", user, name)
        res = len(res)
        await db.close()
        return res

    async def display(self, user, name):
        db = await self.dbConnection.get_connection()
        res = await db.fetch("SELECT * FROM playlist WHERE \"user\"=$1 AND name=$2", user, name)

        await db.close()

        return res

    async def remove(self, user, name, link):
        db = await self.dbConnection.get_connection()
        res = await db.execute("DELETE FROM playlist WHERE \"user\"=$1 AND name=$2 AND link=$3", user, name, link)

        await db.close()

import discord
import asyncio

class UserLocked(discord.ext.commands.CheckFailure):
    def __init__(self,message):
        super().__init__(message)

class UserLock:
    def __init__(self, user, error_message: str="You probably clicked on a button that is waiting for your answer, please cancel the operation before running a new command."):
        self.user = user
        self.error_message = error_message
        self.lock = asyncio.Lock()

    def __call__(self, bot):
        bot.add_user_lock(self)
        return self.lock

    def locked(self):
        return self.lock.locked()

    @property
    def error(self):
        return UserLocked(self.error_message)

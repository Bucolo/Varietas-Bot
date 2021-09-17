from tools.EmojiMan import Utils
import asyncio
import humanize
import datetime
from discord.ext import commands

class MissingManageEmojisPermission(commands.MissingPermissions):
	def __init__(self):
		super(Exception, self).__init__(
			f'{Utils.SUCCESS_EMOJIS[False]} '
			"Sorry, you don't have enough permissions to run this command. "
			'You and I both need the Manage Emojis permission.')

class EmoteManagerError(commands.CommandError):
	pass

class ImageProcessingTimeoutError(EmoteManagerError, asyncio.TimeoutError):
	pass

class ImageResizeTimeoutError(ImageProcessingTimeoutError):
	def __init__(self):
		super().__init__('Error: resizing the image took too long.')

class ImageConversionTimeoutError(ImageProcessingTimeoutError):
	def __init__(self):
		super().__init__('Error: converting the image to a GIF took too long.')

class HTTPException(EmoteManagerError):
	def __init__(self, status):
		super().__init__(f'URL error: server returned error code {status}')

class RateLimitedError(EmoteManagerError):
	def __init__(self, retry_at):
		if isinstance(retry_at, float):
			retry_at = datetime.datetime.fromtimestamp(retry_at, tz=datetime.timezone.utc)
		delta = humanize.naturaldelta(retry_at, when=datetime.datetime.now(tz=datetime.timezone.utc))
		super().__init__(f'Error: Discord told me to slow down! Please retry this command in {delta}.')

class EmoteNotFoundError(EmoteManagerError):
	def __init__(self, name):
		super().__init__(f'An emote called `{name}` does not exist in this server.')

class FileTooBigError(EmoteManagerError):
	def __init__(self, size, limit):
		self.size = size
		self.limit = limit

class InvalidFileError(EmoteManagerError):
	def __init__(self):
		super().__init__('Invalid file given.')

class InvalidImageError(InvalidFileError):
	def __init__(self):
		super(Exception, self).__init__('The image supplied was not a GIF, PNG, JPG, or WEBP file.')

class PermissionDeniedError(EmoteManagerError):
	def __init__(self, name):
		super().__init__(f"You're not authorized to modify `{name}`.")

class DiscordError(Exception):
	def __init__(self):
		super().__init__('Discord seems to be having issues right now, please try again later.')

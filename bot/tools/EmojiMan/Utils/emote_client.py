import sys
import json
import asyncio
import aiohttp
import platform
import datetime
import urllib.parse
from typing import Dict
from http import HTTPStatus
from discord import PartialEmoji
import tools.EmojiMan.Utils.image as image_Utils
from tools.EmojiMan.Utils.errors import RateLimitedError
from discord import HTTPException, Forbidden, NotFound, DiscordServerError
from tools.EmojiMan.data import config
from botconfig import TOKEN

GuildId = int

async def json_or_text(resp):
	text = await resp.text(encoding='utf-8')
	try:
		if resp.headers['content-type'] == 'application/json':
			return json.loads(text)
	except KeyError:
		pass

	return text

class EmoteClient:
	BASE_URL = 'https://discord.com/api/v7'
	HTTP_ERROR_CLASSES = {
		HTTPStatus.FORBIDDEN: Forbidden,
		HTTPStatus.NOT_FOUND: NotFound,
		HTTPStatus.SERVICE_UNAVAILABLE: DiscordServerError,
	}

	def __init__(self, bot):
		self.guild_rls: Dict[GuildId, float] = {}
		self.http = aiohttp.ClientSession(headers={
			'User-Agent': "EmoteManagerBot (https://github.com/iomintz/emote-manager-bot)" + ' ' + bot.http.user_agent,
			'Authorization': 'Bot ' + TOKEN,
			'X-Ratelimit-Precision': 'millisecond',
		})

	async def request(self, method, path, guild_id, **kwargs):
		self.check_rl(guild_id)

		headers = {}
		reason = kwargs.pop('reason', None)
		if reason:
			headers['X-Audit-Log-Reason'] = urllib.parse.quote(reason, safe='/ ')
		kwargs['headers'] = headers

		async with self.http.request(method, self.BASE_URL + path, **kwargs) as resp:
			if resp.status == HTTPStatus.TOO_MANY_REQUESTS:
				return await self._handle_rl(resp, method, path, guild_id, **kwargs)

			data = await json_or_text(resp)
			if resp.status in range(200, 300):
				return data

			error_cls = self.HTTP_ERROR_CLASSES.get(resp.status, HTTPException)
			raise error_cls(resp, data)

	def check_rl(self, guild_id):
		try:
			retry_at = self.guild_rls[guild_id]
		except KeyError:
			return

		now = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
		if retry_at < now:
			del self.guild_rls[guild_id]
			return

		raise RateLimitedError(retry_at)

	async def _handle_rl(self, resp, method, path, guild_id, **kwargs):
		retry_after = (await resp.json())['retry_after'] / 1000.0
		retry_at = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=retry_after)

		self.guild_rls[guild_id] = retry_at.timestamp()

		if retry_after < 10.0:
			await asyncio.sleep(retry_after)
			return await self.request(method, path, guild_id, **kwargs)

		raise RateLimitedError(retry_at)

	async def create(self, *, guild, name, image: bytes, role_ids=(), reason=None):
		data = await self.request(
			'POST', f'/guilds/{guild.id}/emojis',
			guild.id,
			json=dict(name=name, image=image_Utils.image_to_base64_url(image), roles=role_ids),
			reason=reason,
		)
		return PartialEmoji(animated=data.get('animated', False), name=data.get('name'), id=data.get('id'))

	async def __aenter__(self):
		self.http = await self.http.__aenter__()
		return self

	async def __aexit__(self, *excinfo):
		return await self.http.__aexit__(*excinfo)

	async def close(self):
		return await self.http.close()

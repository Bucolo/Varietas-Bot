import asyncio
import discord

def format_user(user, *, mention=False):
	if mention:
		return f'{user.mention} (@{user})'
	else:
		return f'@{user} ({user.id})'

def format_http_exception(exception: discord.HTTPException):
	return (
		f'{exception.response.reason} (status code: {exception.response.status}):'
		f'\n{exception.text}')

def strip_angle_brackets(string):
	if string.startswith('<') and string.endswith('>'):
		return string[1:-1]
	return string

async def gather_or_cancel(*awaitables, loop=None):
	gather_task = asyncio.gather(*awaitables, loop=loop)
	try:
		return await gather_task
	except asyncio.CancelledError:
		raise
	except:
		gather_task.cancel()
		raise

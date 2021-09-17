import functools
from discord.ext.commands import BadArgument

_emote_type_predicates = {
	'all': lambda _: True,
	'static': lambda e: not e.animated,
	'animated': lambda e: e.animated}

def emote_type_filter_default(command):
	old_callback = command.callback

	@functools.wraps(old_callback)
	async def callback(self, ctx, *args):
		image_type = args[-1]
		try:
			image_type = _emote_type_predicates[image_type]
		except KeyError:
			raise BadArgument(f'Invalid emote type. Specify one of "all", "static", or "animated".')
		return await old_callback(self, ctx, *args[:-1], image_type)

	command.callback = callback
	return command

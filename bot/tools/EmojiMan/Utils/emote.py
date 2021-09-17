import re

RE_EMOTE = re.compile(r'(:|;)(?P<name>\w{2,32})\1|(?P<newline>\n)', re.ASCII)

RE_CUSTOM_EMOTE = re.compile(r'<(?P<animated>a?):(?P<name>\w{2,32}):(?P<id>\d{17,})>', re.ASCII)

def url(id, *, animated: bool = False):
	extension = 'gif' if animated else 'png'
	return f'https://cdn.discordapp.com/emojis/{id}.{extension}?v=1'

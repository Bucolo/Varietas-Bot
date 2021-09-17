import asyncio
import cgi
import collections
import contextlib
import io
import json
import logging
import operator
import posixpath
import re
import traceback
import urllib.parse
import zipfile
import warnings
import weakref

import aiohttp
import discord
import humanize
from discord.ext import commands

import tools.EmojiMan.Utils as utils
import tools.EmojiMan.Utils.image as utils_image
from tools.EmojiMan.Utils import errors
from tools.EmojiMan.Utils.paginator import ListPaginator
from tools.EmojiMan.Utils.emote_client import EmoteClient
from tools.EmojiMan.Utils.converter import emote_type_filter_default

looger = logging.getLogger(__name__)
warnings.filterwarnings(
    'ignore',
    module='zipfile',
    category=UserWarning,
    message=r"^Duplicate name: .*$")


class UserCancelledError(commands.UserInputError):
    pass


class Emotes(commands.Cog):
    IMAGE_MIMETYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
    TAR_MIMETYPES = {'application/x-tar'}
    ZIP_MIMETYPES = {
        'application/zip',
        'application/octet-stream',
        'application/x-zip-compressed',
        'multipart/x-zip'}
    ARCHIVE_MIMETYPES = TAR_MIMETYPES | ZIP_MIMETYPES
    ZIP_OVERHEAD_BYTES = 30

    def __init__(self, bot):
        self.bot = bot

        connector = None
        socks5_url = self.bot.config.get('socks5_proxy_url')
        if socks5_url:
            from aiohttp_socks import SocksConnector
            connector = SocksConnector.from_url(socks5_url, rdns=True)

        self.http = aiohttp.ClientSession(
            loop=self.bot.loop,
            read_timeout=self.bot.config.get(
                'http_read_timeout',
                60),
            connector=connector if self.bot.config.get('use_socks5_for_all_connections') else None,
            headers={
                'User-Agent': self.bot.config['user_agent'] + ' ' + self.bot.http.user_agent})
        self.emote_client = EmoteClient(self.bot)
        with open("./tools/EmojiMan/data/ec-emotes-final.json") as f:
            self.ec_emotes = json.load(f)
        self.paginators = weakref.WeakSet()

    def cog_unload(self):
        async def close():
            await self.http.close()
            await self.emote_client.close()

            for paginator in self.paginators:
                await paginator.stop()

        self.bot.loop.create_task(close())

    public_commands = set()

    def public(command, public_commands=public_commands):
        public_commands.add(command.qualified_name)
        return command

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        if ctx.command.qualified_name in self.public_commands:
            return True
        if (
            not ctx.author.guild_permissions.manage_emojis
            or not ctx.guild.me.guild_permissions.manage_emojis
        ):
            raise errors.MissingManageEmojisPermission
        return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.EmoteManagerError):
            await ctx.send(error)
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f'{utils.SUCCESS_EMOJIS[False]} Sorry, this command may only be used in a server.')

    @commands.command()
    async def em_add(self, ctx, *, args):
        print(1)
        name, url = self.parse_add_command_args(ctx, args=args)
        print(name)
        print(url)
        print(2)
        async with ctx.typing():
            print(3)
            message = await self.add_safe(context=ctx, name=name, url=url)
            print(9)
        await ctx.send(message)

    @commands.command()
    async def em_add_these(self, ctx, *emotes):
        ran = False
        for match in re.finditer(utils.emote.RE_CUSTOM_EMOTE, ''.join(emotes)):
            ran = True
            animated, name, id = match.groups()
            image_url = utils.emote.url(id, animated=animated)
            async with ctx.typing():
                message = await self.add_safe(ctx, name, image_url)
                await ctx.send(message)
        if not ran:
            return await ctx.send('Error: no custom emotes were provided.')
        await ctx.message.add_reaction("✅")

    @classmethod
    def parse_add_command_args(cls, ctx, *, args):
        if ctx.message.attachments:
            return cls.parse_add_command_attachment(ctx, args)
        elif len(args) == 1:
            match = utils.emote.RE_CUSTOM_EMOTE.match(args[0])
            if match is None:
                raise commands.BadArgument(
                    'Error: I expected a custom emote as the first argument, '
                    'but I got something else. '
                    "If you're trying to add an emote using an image URL, "
                    'you need to provide a name as the first argument, like this:\n'
                    '`{}add NAME_HERE URL_HERE`'.format(ctx.prefix))
            else:
                animated, name, id = match.groups()
                url = utils.emote.url(id, animated=animated)
            return name, url
        elif len(args) >= 2:
            name = args[0]
            match = utils.emote.RE_CUSTOM_EMOTE.match(args[1])
            if match is None:
                url = utils.strip_angle_brackets(args[1])
            else:
                url = utils.emote.url(match['id'], animated=match['animated'])
            return name, url
        elif not args:
            raise commands.BadArgument(
                'Your message had no emotes and no name!')

    @classmethod
    def parse_add_command_attachment(cls, ctx, args):
        attachment = ctx.message.attachments[0]
        name = cls.format_emote_filename(
            ''.join(args) if args else attachment.filename)
        url = attachment.url
        return name, url

    @staticmethod
    def format_emote_filename(filename):
        left, sep, right = posixpath.splitext(filename)[0].rpartition('-')
        return (left or right).replace(' ', '')

    @commands.command(aliases=['emaddfromec'])
    async def em_add_from_ec(self, context, name, *names):
        if names:
            for name in (name,) + names:
                await context.invoke(self.add_from_ec, name)
                await context.message.add_reaction(utils.SUCCESS_EMOJIS[True])
                return
        try:
            emote = self.ec_emotes[name.strip(':').lower()]
        except KeyError:
            return await context.send("Emote not found in Emote Collector's database.")
        reason = (
            f'Added from Emote Collector by {utils.format_user(context.author)}. '
            f'Original emote author ID: {emote["author"]}')
        image_url = utils.emote.url(emote['id'], animated=emote['animated'])
        async with context.typing():
            message = await self.add_safe(context, name, image_url, reason=reason)
        await context.send(message)

    @public
    @emote_type_filter_default
    @commands.command()
    @commands.bot_has_permissions(attach_files=True)
    async def em_export(self, context, image_type='all'):
        emotes = list(filter(image_type, context.guild.emojis))
        if not emotes:
            raise commands.BadArgument(
                'No emotes of that type were found in this server.')
        async with context.typing():
            async for zip_file in self.archive_emotes(context, emotes):
                await context.send(file=zip_file)

    async def archive_emotes(self, context, emotes):
        filesize_limit = context.guild.filesize_limit
        discrims = collections.defaultdict(int)
        downloaded = collections.deque()

        async def download(emote):
            discrims[emote.name] += 1
            discrim = discrims[emote.name]
            if discrim == 1:
                name = emote.name
            else:
                name = f'{emote.name}-{discrim}'
                name = f'{name}.{"gif" if emote.animated else "png"}'
                data = await self.fetch_safe(str(emote.url), validate_headers=False)
            if isinstance(data, str):
                await context.send(f'{emote}: {data}')
                return
            est_zip_overhead = len(name) + self.ZIP_OVERHEAD_BYTES
            est_size_in_zip = est_zip_overhead + len(data)
            if est_size_in_zip >= filesize_limit:
                self.bot.loop.create_task(context.send(
                    f'{emote} could not be added because it alone would exceed the file size limit.'))
                return
            downloaded.append((name, emote.created_at, est_size_in_zip, data))
        await utils.gather_or_cancel(*map(download, emotes))
        count = 1
        while True:
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as zip:
                while True:
                    try:
                        item = downloaded.popleft()
                    except IndexError:
                        break
                    name, created_at, est_size, image_data = item
                    if out.tell() + est_size >= filesize_limit:
                        downloaded.appendleft(item)
                        break
                    zinfo = zipfile.ZipInfo(
                        name, date_time=created_at.timetuple()[:6])
                    zip.writestr(zinfo, image_data)
                if out.tell() == 0:
                    break
            out.seek(0)
            yield discord.File(out, f'emotes-{context.guild.id}-{count}.zip')
            count += 1

    @commands.command(
        aliases=[
            'add-zip',
            'add-tar',
            'add-from-zip',
            'add-from-tar'])
    async def em_import(self, context, url=None):
        if url and context.message.attachments:
            raise commands.BadArgument(
                'Either a URL or an attachment must be given, not both.')
        if not url and not context.message.attachments:
            raise commands.BadArgument('A URL or attachment must be given.')
        self.emote_client.check_rl(context.guild.id)
        url = url or context.message.attachments[0].url
        async with context.typing():
            archive = await self.fetch_safe(url, valid_mimetypes=self.ARCHIVE_MIMETYPES)
        if isinstance(archive, str):
            await context.send(archive)
            return
        await self.add_from_archive(context, archive)
        with contextlib.suppress(discord.HTTPException):
            await context.message.add_reaction(utils.SUCCESS_EMOJIS[True])

    async def add_from_archive(self, context, archive):
        limit = 50_000_000
        async for name, img, error in utils.archive.extract_async(io.BytesIO(archive), size_limit=limit):
            try:
                utils.image.mime_type_for_image(img)
            except errors.InvalidImageError:
                continue
            if error is None:
                name = self.format_emote_filename(posixpath.basename(name))
                async with context.typing():
                    message = await self.add_safe_bytes(context, name, img)
                await context.send(message)
                continue
            if isinstance(error, errors.FileTooBigError):
                await context.send(f'{name}: file too big. '
                                   f'The limit is {humanize.naturalsize(error.limit)} '
                                   f'but this file is {humanize.naturalsize(error.size)}.')
                continue
            await context.send(f'{name}: {error}')

    async def add_safe(self, context, name, url, *, reason=None):
        print(4)
        self.emote_client.check_rl(context.guild.id)
        print(5)
        try:
            image_data = await self.fetch_safe(url)
            print
            print(6)
        except errors.InvalidFileError:
            raise errors.InvalidImageError
        print(7)
        if isinstance(image_data, str):
            return image_data
        print(8)
        print(await self.add_safe_bytes(context, name, image_data, reason=reason))
        return await self.add_safe_bytes(context, name, image_data, reason=reason)

    async def fetch_safe(self, url, valid_mimetypes=None, *, validate_headers=False):
        try:
            return await self.fetch(url, valid_mimetypes=valid_mimetypes, validate_headers=validate_headers)
        except asyncio.TimeoutError:
            return 'Error: retrieving the image took too long.'
        except ValueError:
            return 'Error: Invalid URL.'
        except aiohttp.ClientResponseError as exc:
            raise errors.HTTPException(exc.status)

    async def add_safe_bytes(self, context, name, image_data: bytes, *, reason=None):
        print(10)
        counts = collections.Counter(
            map(operator.attrgetter('animated'), context.guild.emojis))
        print(11)
        if counts[False] >= context.guild.emoji_limit and counts[True] >= context.guild.emoji_limit:
            raise commands.UserInputError('This server is out of emote slots.')
        print(12)
        print(image_data)
        static = utils.image.mime_type_for_image(image_data) != 'image/gif'
        print(14)
        converted = False
        print(15)
        if static and counts[False] >= context.guild.emoji_limit:
            image_data = await utils.image.convert_to_gif_in_subprocess(image_data)
            converted = True
            print(16)
        try:
            emote = await self.create_emote_from_bytes(context, name, image_data, reason=reason)
            print(17)
        except discord.InvalidArgument:
            return discord.utils.escape_mentions(
                f'{name}: The file supplied was not a valid GIF, PNG, JPEG, or WEBP file.')
        except discord.HTTPException as ex:
            return discord.utils.escape_mentions(
                f'{name}: An error occurred while creating the the emote:\n' +
                utils.format_http_exception(ex))
        print(18)
        s = f'Emote {emote} successfully created'
        print(19)
        print(s + ' as a GIF.' if converted else s + '.')
        return s + ' as a GIF.' if converted else s + '.'

    async def fetch(self, url, valid_mimetypes=IMAGE_MIMETYPES, *, validate_headers=True):
        valid_mimetypes = valid_mimetypes or self.IMAGE_MIMETYPES

        def validate_headers(response):
            response.raise_for_status()
            mimetype, options = cgi.parse_header(
                response.headers.get('Content-Type', ''))
            if mimetype not in valid_mimetypes:
                raise errors.InvalidFileError

        async def validate(request):
            try:
                async with request as response:
                    validate_headers(response)
                    return await response.read()
            except aiohttp.ClientResponseError:
                raise
            except aiohttp.ClientError as exc:
                raise errors.EmoteManagerError(
                    f'An error occurred while retrieving the file: {exc}')
            if validate_headers:
                await validate(self.http.head(url, timeout=self.bot.config.get('http_head_timeout', 10)))
            return await validate(self.http.get(url))

    async def create_emote_from_bytes(self, context, name, image_data: bytes, *, reason=None):
        if len(image_data) > 256 * 1024:
            image_data = await utils.image.resize_in_subprocess(image_data)
        if reason is None:
            reason = 'Created by ' + utils.format_user(context.author)
            return await self.emote_client.create(guild=context.guild, name=name, image=image_data, reason=reason)

    @commands.command()
    async def em_remove(self, context, emote, *emotes):
        if not emotes:
            emote = await self.parse_emote(context, emote)
            await emote.delete(reason='Removed by ' + utils.format_user(context.author))
            await context.send(fr'Emote \:{emote.name}: successfully removed.')
        else:
            for emote in (emote,) + emotes:
                await context.invoke(self.remove, emote)
            with contextlib.suppress(discord.HTTPException):
                await context.message.add_reaction(utils.SUCCESS_EMOJIS[True])

    @commands.command(aliases=['mv'])
    async def em_rename(self, context, old, new_name):
        emote = await self.parse_emote(context, old)
        try:
            await emote.edit(name=new_name, reason=f'Renamed by {utils.format_user(context.author)}')
        except discord.HTTPException as ex:
            return await context.send('An error occurred while renaming the emote:\n' + utils.format_http_exception(ex))
        await context.send(fr'Emote successfully renamed to \:{new_name}:')

    @public
    @emote_type_filter_default
    @commands.command(aliases=['ls', 'dir'])
    async def em_list(self, context, image_type='all'):
        emotes = sorted(
            filter(
                image_type,
                context.guild.emojis),
            key=lambda e: e.name.lower())
        processed = []
        for emote in emotes:
            raw = str(emote).replace(':', r'\:')
            processed.append(f'{emote} {raw}')
        paginator = ListPaginator(context, processed)
        self.paginators.add(paginator)
        await paginator.begin()

    @public
    @commands.command(aliases=['status'])
    async def em_stats(self, context):
        emote_limit = context.guild.emoji_limit
        static_emotes = animated_emotes = total_emotes = 0
        for emote in context.guild.emojis:
            if emote.animated:
                animated_emotes += 1
            else:
                static_emotes += 1
            total_emotes += 1
        percent_static = round((static_emotes / emote_limit) * 100, 2)
        percent_animated = round((animated_emotes / emote_limit) * 100, 2)
        static_left = emote_limit - static_emotes
        animated_left = emote_limit - animated_emotes
        await context.send(f'Static emotes: **{static_emotes} / {emote_limit}** ({static_left} left, {percent_static}% full)\n'
                           f'Animated emotes: **{animated_emotes} / {emote_limit}** ({animated_left} left, {percent_animated}% full)\n'
                           f'Total: **{total_emotes} / {emote_limit * 2}**')

    @commands.command(aliases=["embiggen"])
    async def em_big(self, context, emote):
        emote = await self.parse_emote(context, emote, local=False)
        await context.send(f'{emote.name}: {emote.url}')

    async def parse_emote(self, context, name_or_emote, *, local=True):
        await asyncio.sleep(0)
        match = utils.emote.RE_CUSTOM_EMOTE.match(name_or_emote)
        if match:
            id = int(match['id'])
            if local:
                emote = discord.utils.get(context.guild.emojis, id=id)
            if emote:
                return emote
            else:
                return discord.PartialEmoji(animated=bool(match['animated']),
                                            name=match['name'],
                                            id=int(match['id']))
        name = name_or_emote
        return await self.disambiguate(context, name)

    async def disambiguate(self, context, name):
        name = name.strip(':')
        candidates = [e for e in context.guild.emojis if e.name.lower(
        ) == name.lower() and e.require_colons]
        if not candidates:
            raise errors.EmoteNotFoundError(name)
        if len(candidates) == 1:
            return candidates[0]
        message = [
            'Multiple emotes were found with that name. Which one do you mean?']
        for i, emote in enumerate(candidates, 1):
            message.append(fr'{i}. {emote} (\:{emote.name}:)')
        await context.send('\n'.join(message))

        def check(message):
            try:
                int(message.content)
            except ValueError:
                return False
            else:
                return message.author == context.author
        try:
            message = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            raise commands.UserInputError(
                'Sorry, you took too long. Try again.')
        return candidates[int(message.content) - 1]


def setup(bot):
    bot.add_cog(Emotes(bot))

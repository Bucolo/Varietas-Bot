import asyncio
import base64
import contextlib
import functools
import io
import logging
import signal
import sys
import typing

logger = logging.getLogger(__name__)

try:
	import wand.image
except (ImportError, OSError):
	logger.warn('Failed to import wand.image. Image manipulation functions will be unavailable.')
else:
	import wand.exceptions

from tools.EmojiMan.Utils import errors

def resize_until_small(image_data: io.BytesIO) -> None:
	max_resolution = 128
	image_size = size(image_data)
	if image_size <= 256 * 2**10:
		return
	try:
		with wand.image.Image(blob=image_data) as original_image:
			while True:
				logger.debug('image size too big (%s bytes)', image_size)
				logger.debug('attempting resize to at most%s*%s pixels', max_resolution, max_resolution)

				with original_image.clone() as resized:
					resized.transform(resize=f'{max_resolution}x{max_resolution}')
					image_size = len(resized.make_blob())
					if image_size <= 256 * 2**10 or max_resolution < 32:
						image_data.truncate(0)
						image_data.seek(0)
						resized.save(file=image_data)
						image_data.seek(0)
						break
				max_resolution //= 2
	except wand.exceptions.CoderError:
		raise errors.InvalidImageError

def convert_to_gif(image_data: io.BytesIO) -> None:
	try:
		with wand.image.Image(blob=image_data) as orig, orig.convert('gif') as converted:
			converted.sequence[0].delay = 0
			converted.sequence.append(wand.image.Image(width=1, height=1))
			image_data.truncate(0)
			image_data.seek(0)
			converted.save(file=image_data)
			image_data.seek(0)
	except wand.exceptions.CoderError:
		raise errors.InvalidImageError

def mime_type_for_image(data):
    print(13)
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        print(14)
        return 'image/png'
    if data.startswith(b'\xFF\xD8') and data.rstrip(b'\0').endswith(b'\xFF\xD9'):
        print(14)
        return 'image/jpeg'
    if data.startswith((b'GIF87a', b'GIF89a')):
        print(14)
        return 'image/gif'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        print(14)
        return 'image/webp'
    raise errors.InvalidImageError

def image_to_base64_url(data):
	fmt = 'data:{mime};base64,{data}'
	mime = mime_type_for_image(data)
	b64 = base64.b64encode(data).decode('ascii')
	return fmt.format(mime=mime, data=b64)

def main() -> typing.NoReturn:
	import sys
	if sys.argv[1] == 'resize':
		f = resize_until_small
	elif sys.argv[1] == 'convert':
		f = convert_to_gif
	else:
		sys.exit(1)
	data = io.BytesIO(sys.stdin.buffer.read())
	try:
		f(data)
	except errors.InvalidImageError:
		sys.exit(2)
	stdout_write = sys.stdout.buffer.write
	while True:
		buf = data.read(16 * 1024)
		if not buf:
			break
		stdout_write(buf)
	sys.exit(0)

async def process_image_in_subprocess(command_name, image_data: bytes):
	proc = await asyncio.create_subprocess_exec(
		sys.executable, '-m', __name__, command_name,
		stdin=asyncio.subprocess.PIPE,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE)
	try:
		image_data, err = await asyncio.wait_for(proc.communicate(image_data), timeout=float('inf'))
	except asyncio.TimeoutError:
		proc.send_signal(signal.SIGINT)
		raise errors.ImageResizeTimeoutError if command_name == 'resize' else errors.ImageConversionTimeoutError
	else:
		if proc.returncode == 2:
			raise errors.InvalidImageError
		if proc.returncode != 0:
			raise RuntimeError(err.decode('utf-8') + f'Return code: {proc.returncode}')
	return image_data

resize_in_subprocess = functools.partial(process_image_in_subprocess, 'resize')
convert_to_gif_in_subprocess = functools.partial(process_image_in_subprocess, 'convert')

def size(fp):
	with preserve_position(fp):
		fp.seek(0, io.SEEK_END)
		return fp.tell()

class preserve_position(contextlib.AbstractContextManager):
	def __init__(self, fp):
		self.fp = fp
		self.old_pos = fp.tell()

	def __exit__(self, *excinfo):
		self.fp.seek(self.old_pos)

if __name__ == '__main__':
	main()

import asyncio
import collections
import enum
import posixpath
import tarfile
import typing.io
import zipfile
from typing import Iterable, Tuple, Optional

from . import errors

ArchiveInfo = collections.namedtuple('ArchiveInfo', 'filename content error')

def extract(archive: typing.io.BinaryIO, *, size_limit=None) \
	-> Iterable[Tuple[str, Optional[bytes], Optional[BaseException]]]:

	try:
		yield from extract_zip(archive, size_limit=size_limit)
		return
	except zipfile.BadZipFile:
		pass
	finally:
		archive.seek(0)

	try:
		yield from extract_tar(archive, size_limit=size_limit)
	except tarfile.ReadError as exc:
		raise ValueError('not a valid zip or tar file') from exc
	finally:
		archive.seek(0)

def extract_zip(archive, *, size_limit=None):
	with zipfile.ZipFile(archive) as zip:
		members = [m for m in zip.infolist() if not m.is_dir()]
		for member in members:
			if size_limit is not None and member.file_size >= size_limit:
				yield ArchiveInfo(
					filename=member.filename,
					content=None,
					error=errors.FileTooBigError(member.file_size, size_limit))
				continue

			try:
				content = zip.open(member).read()
			except RuntimeError as exc:
				yield ArchiveInfo(filename=member.filename, content=None, error=exc)
			else:
				yield ArchiveInfo(filename=member.filename, content=content, error=None)

def extract_tar(archive, *, size_limit=None):
	with tarfile.open(fileobj=archive) as tar:
		members = [f for f in tar.getmembers() if f.isfile()]
		for member in members:
			if size_limit is not None and member.size >= size_limit:
				yield ArchiveInfo(
					filename=member.name,
					content=None,
					error=errors.FileTooBigError(member.size, size_limit))
				continue

			yield ArchiveInfo(member.name, content=tar.extractfile(member).read(), error=None)

async def extract_async(archive: typing.io.BinaryIO, size_limit=None):
	for x in extract(archive, size_limit=size_limit):
		yield await asyncio.sleep(0, x)

def main():
	import io
	import sys

	import humanize

	arc = io.BytesIO(sys.stdin.detach().read())
	for name, data, error in extract(arc):
		if error is not None:
			print(f'{name}: {error}')
			continue

		print(f'{name}: {humanize.naturalsize(len(data)):>10}')

if __name__ == '__main__':
	main()

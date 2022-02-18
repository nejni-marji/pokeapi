#!/usr/bin/env python3
import argparse, logging
from urllib.request import urlopen, Request
from urllib.parse import quote
from os.path import isfile, isdir
from os import mkdir
from xdg.BaseDirectory import xdg_cache_home

class PrefixError(Exception):
	pass

# if you arent on linux, you'll have to figure this out yourself. good luck
CACHE=xdg_cache_home + '/pokeapi'

# if cache dir does not exist, try to create it
if not isdir(CACHE):
	try:
		mkdir(CACHE)
	except FileExistsError:
		logging.critical('Unable to create cache, terminating')
	except:
		logging.critical('Unable to create cache (unknown error), terminating')

def get_raw(url):
	url_data = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
	url_data = url_data.read().decode()
	return url_data

def get_with_cache(url, prefix='', quiet=False, cache_mode='auto'):

	# prefix is used to check that URLs are from a given domain, and also to
	# shorten paths for the cache.
	logging.debug(f'url: {url}')
	logging.debug(f'prefix: {prefix}')

	if not url.startswith(prefix):
		raise PrefixError

	if cache_mode == 'ignore':
		url_data = get_raw(url)
		print(url_data)
		return

	cache_name = url.replace(prefix, '', 1)
	logging.debug(f'cache_name: {cache_name}')

	cache_path = CACHE + '/' + quote(cache_name, safe=[]) # safe means encode '/'
	logging.debug(f'cache_path: {cache_path}')

	if cache_mode == 'update':
		has_cache = False
	else:
		has_cache = isfile(cache_path)
	logging.debug(f'has_cache: {has_cache}')

	# right away, let's try to cache data if we need to
	if not has_cache:
		logging.info(f'Writing to cache for {cache_name}')
		url_data = get_raw(url)
		cache_file = open(cache_path, 'w')
		cache_file.write(url_data)
		cache_file.close()

	if not quiet:
		if not has_cache:
			print(url_data)
		else:
			logging.info(f'Reading from cache for {cache_name}')
			cache_file = open(cache_path, 'r')
			cache_data = cache_file.read()
			cache_file.close()
			print(cache_data)
	else:
		logging.info('Running in quiet mode')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-q', '--quiet', action='store_true')
	parser.add_argument('-c', '--cache', action='store',
			choices=['auto', 'update', 'ignore'], default='auto')
	parser.add_argument('url', action='store', type=str)
	args = parser.parse_args()

	FORMAT='{levelname}: {message}'
	LEVEL = ['WARNING', 'INFO', 'DEBUG', 0][args.verbose]
	logging.basicConfig(format=FORMAT, style='{', level=LEVEL)

	logging.debug(args)

	PREFIX = 'https://pokeapi.co/api/v2/'
	URL = args.url
	if not URL.startswith(PREFIX):
		logging.debug('URL does not start with prefix')
		URL = PREFIX + URL
	if not URL == PREFIX and URL.endswith('/'):
		logging.debug('URL is not PREFIX and ends with /')
		URL = URL[0:-1]
	if URL == PREFIX:
		URL += '/'

	get_with_cache(URL, PREFIX, args.quiet, args.cache)

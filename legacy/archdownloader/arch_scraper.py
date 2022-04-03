import argparse
import re
import urllib.request
import urllib.parse
import time

from bs4 import BeautifulSoup
from multiprocessing import Pool, Value
from pathlib import Path


arch_base_url = 'https://archlinux.org/'
github_base_url = 'https://github.com/'
github_raw_base_url = 'https://raw.githubusercontent.com/'


def scrape_arch_page(arch_pkgs_page_url):
	pkg_pages_list = []

	try:
		with urllib.request.urlopen(arch_pkgs_page_url) as pkg_list:
			soup = BeautifulSoup(pkg_list, 'html.parser')
			table = soup.table.tbody
			for row in table.find_all('tr'):
				for col in row.find_all('td'):
					if (col.find('a')):
						pkg_url = urllib.parse.urljoin(arch_base_url, col.a['href'])
						pkg_pages_list.append(pkg_url)
	except Exception as e:
		print(e)

	return pkg_pages_list


def scrape_pkg_page(pkg_url):
	try:
		with urllib.request.urlopen(pkg_url) as pkg_page:
			soup = BeautifulSoup(pkg_page, 'html.parser')
			github_url = soup.find('a', text=re.compile('Source Files'))['href']
			return urllib.parse.urljoin(github_base_url, github_url)
	except Exception as e:
		print(e)


def scrape_github_page(github_url):
	try:
		with urllib.request.urlopen(github_url) as github_page:
			soup = BeautifulSoup(github_page, 'html.parser')
			PKGBUILD_url = soup.find('a', title='PKGBUILD')['href']
			PKGBUILD_url = PKGBUILD_url.replace('blob/', '')
			return urllib.parse.urljoin(github_raw_base_url, PKGBUILD_url)
	except Exception as e:
		print(e)


def download_PKGBUILD(PKGBUILD_url):
	try:
		with urllib.request.urlopen(PKGBUILD_url) as PKGBUILD_src_page:
			soup = BeautifulSoup(PKGBUILD_src_page, 'html.parser')
			project_name = PKGBUILD_url.split('/')[-3]
			output_file_name = project_name + '.PKGBUILD'
			output_file_path = Path('PKGBUILD-list', output_file_name)
			with open(output_file_path, 'w+') as PKGBUILD_file:
				PKGBUILD_file.write(str(soup))
	except Exception as e:
		print(e)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-p', type = int,
		metavar = 'num_pages', help = 'maximum number of scraped web pages')
	parser.add_argument('num_pkgs', type = int,
		help = 'maximum number of PKGBUILD files')

	args = parser.parse_args()

	num_pkgs = 0
	num_pages = 0

	arch_pkgs_pages_list = []
	arch_pkgs_url = urllib.parse.urljoin(arch_base_url, 'packages/')

	# Get the maximum number of scrapable web pages from arch linux
	# packages page.
	if args.p == None:
		with urllib.request.urlopen(arch_pkgs_url) as pkg_list:
			soup = BeautifulSoup(pkg_list, 'html.parser')
			stats = soup.find('div', class_='pkglist-stats').p.string
			args.p = int(stats.split(' ')[-1].strip('.'))

	# Produce the list of scrapable web pages
	while num_pages < args.p:
		query = '?page=' + str(num_pages + 1) + '&'
		arch_url = urllib.parse.urljoin(arch_pkgs_url, query)
		arch_pkgs_pages_list.append(arch_url)
		num_pages += 1

	for arch_url in arch_pkgs_pages_list:
		if (num_pkgs < args.num_pkgs):
			pkg_pages_list = scrape_arch_page(arch_url)
			for pkg_url in pkg_pages_list:
				if (num_pkgs < args.num_pkgs):
					github_url = scrape_pkg_page(pkg_url)
					PKGBUILD_url = scrape_github_page(github_url)
					download_PKGBUILD(PKGBUILD_url)
					num_pkgs += 1
					print(f"downloaded PKGBUILD file for project: " +
						f"{PKGBUILD_url.split('/')[-3]}")

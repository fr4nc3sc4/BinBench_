from bs4 import BeautifulSoup
from urllib.request import urlopen
import json

# RETRIEVE PACKAGES AND LICENSES FROM WEBSITE

compiled_pkgs = []

f = open("out.txt", "r")
for x in f:
    if 'success' in x:
        split = x.split(' - success')[0]
        compiled_pkgs.append(split)       

pkg_dict = {}
license_dict = {}

archlinux_url = 'https://archlinux.org'
url = f'https://archlinux.org/packages/?sort=&repo=Core'
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

form = soup.find(id="pkglist-results-form")
tot_pages = int(form.p.text.split('of ')[1][0:1])

package_address = '/packages/core'

for page in range(1,tot_pages+1):

    url = f'https://archlinux.org/packages/?page={page}&repo=Core'
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find(id='pkglist-results')

    for link in results.find_all('a'):
        current_link =link.get('href')

        if package_address in current_link:
            pkg_url = archlinux_url + current_link
            pkg_name = current_link.split('/')[-2]  
        # filter only compiled packages
            if pkg_name in compiled_pkgs:
            
                pkg_page = urlopen(pkg_url)
                pkg_html = pkg_page.read().decode("utf-8")
                pkg_soup = BeautifulSoup(pkg_html, "html.parser")

                # license type:
                licenseText = pkg_soup.find(text='License(s):')
                th = licenseText.findPrevious('th')
                pkg_license = th.findNext('td')

                pkg_dict[pkg_name] = pkg_license.text


with open('pkgs.json', 'w+') as outfile:
    json.dump(pkg_dict, outfile, indent=2)


        
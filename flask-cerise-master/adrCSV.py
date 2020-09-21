import csv
import random
import urllib.error as urllib1
import urllib.request as urllib2

from bs4 import BeautifulSoup


def fonc(url, classe):
    global page

    # Defining the url of the site

    base_site = url

    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    req = urllib2.Request(base_site, headers=hdr)

    # Accessing the site page
    try:
        page = urllib2.urlopen(req)
    except urllib1.HTTPError as e:
        print(e.fp.read())

    # Parse the html using beutifulsoup

    soup = BeautifulSoup(page, 'html.parser')
    divs_tab = soup.find_all('div', class_=classe)

    # Create e beautifulsoup object from our list

    aa = BeautifulSoup(str(divs_tab), "html.parser")

    # Extract all links

    links = aa.find_all('a')

    # We obtained relative URLs
    # To obtain the absolute URL address we will use urljoin

    from urllib.parse import urljoin
    relative_urls = [link.get('href') for link in links]

    # Transforming to absolute path URLs
    full_urls = [urljoin(base_site, url) for url in relative_urls]

    # List to store states

    states = dict({})
    for state in divs_tab:
        states[str(state.text.strip())] = dict({})
    return [states, full_urls]


tableau = fonc("https://www.codepostalmonde.com/tunisia/", 'col-md-6 mb-2')
states = tableau[0]
with open('adresse.csv', mode='a', encoding="utf-8", newline='') as csv_file:  # enregistrement du dict dans adresse.csv
    fieldnames = ['adresse', 'code_postal', 'score']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for url, state, i in zip(tableau[1], states, range(24)):  # parcour sur les gouvernorats
        tab2 = fonc(url, 'col-md-4 mb-2')
        adresse = state
        score = random.randint(60, 100)
        # print(adresse)
        for tab, link in zip(tab2[0], tab2[1]):  # parcour sur chaque ville du gouvernorat
            adresse1 = adresse + ', ' + tab
            tab3 = fonc(link, 'col-md-6 mb-2')
            for adrfinal in tab3[0]:
                adr1 = adrfinal[0:len(adrfinal) - 5].strip()
                adr2 = adrfinal[len(adrfinal) - 5:len(adrfinal)].strip()
                adresse2 = adresse1 + ', ' + adr1
                data = {
                    "adresse": adresse2,
                    "code_postal": adr2,
                    'score': score
                }
                writer.writerow(data)
    csv_file.close()
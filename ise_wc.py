# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup	

ROOT_URL = "http://www.ise.ie"

def crawler():
	page = 1
	while page <= 2:		# crawl through all the pages we specify
		url = "http://www.ise.ie/Market-Data-Announcements/Companies/Price-changes/"	# page 1

		if page == 2:
			url = "http://www.ise.ie/Market-Data-Announcements/Companies/Price-changes/?ACTIVEGROUP=2&&type=CHANGEPRICE"	# page 2

		source_code = requests.get(url)		# get the page source
		plain_text = source_code.text 	

		soup = BeautifulSoup(plain_text, "html.parser")		# BS object with html parser

		i = 0

		for company_link in soup.find_all('td', 'equityName mDataGrid480'):		# class of each company name
			
			if (i % 2) == 0:			# every second one is "INSTRUMENT NAME" column on the web page, I dont want that...	

				for company in company_link.find_all('a'):

					href = ROOT_URL + company.get('href')
					title = company.string
					print(href)
					print(title)
					print()

			i += 1

		page = page + 1

	print("Finished!")

def main():
	crawler()

if __name__ == '__main__':
	main() 
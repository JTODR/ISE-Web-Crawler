# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup	

ROOT_URL = "http://www.ise.ie"


def crawler():
	page = 1
	
	while page <= 1:		# crawl through all the pages we specify
		url = "http://www.ise.ie/Market-Data-Announcements/Companies/Price-changes/"	# page 1

		if page == 2:
			url = url + "?ACTIVEGROUP=2&&type=CHANGEPRICE"	# page 2

		source_code = requests.get(url)		# get the page source
		plain_text = source_code.text 	

		soup = BeautifulSoup(plain_text, "html.parser")		# BS object with html parser
		
		i = 0

		for company_link in soup.find_all('td', 'equityName mDataGrid480'):		# class of each company name
			
			if (i % 2) == 0:			# every second one is "INSTRUMENT NAME" column on the web page, I dont want that...	

				for company in company_link.find_all('a'):

					company_href = ROOT_URL + company.get('href')
					company_title = company.string
					print(company_href)
					print(company_title)
					history_href = ROOT_URL + get_history_href(company_href)

					print(history_href)
			#break


			i += 1

		page = page + 1

	print("Finished!")

def get_history_href(username_url):
	source_code = requests.get(username_url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	company_history = soup.find('td', 'legendWidth210 d-lightGreyFont d-fontArial')
	company_link = company_history.find('a')
	history_href = company_link.get('href')

	return history_href

	


def main():
	crawler()

if __name__ == '__main__':
	main() 
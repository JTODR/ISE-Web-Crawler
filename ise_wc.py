# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup
import time	

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

					company_url = ROOT_URL + company.get('href')
					company_title = company.string
					print(company_title)
					history_url = ROOT_URL + get_history_href(company_url)

					get_share_price_history_table(history_url)

					time.sleep(3)		# give the program time to breathe...

			#break
			i += 1
		page = page + 1

	print("Finished!")


def get_share_price_history_table(history_href):
	source_code = requests.get(history_href)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	date_list = []
	share_price_list = []
	market_capital_list = []

	i = 0

	for row in soup.find_all('td', 'equityName'):
		if i % 3 == 0:
			date_list.append(row.string)

		elif i % 3 == 1:
			share_price = row.string
			share_price = "€" + share_price[:7]
			share_price_list.append(share_price)

		elif i % 3 == 2:
			market_capital = row.string + " MIL"
			market_capital_list.append(market_capital)

		i += 1

	print("DATE\t\tCLOSING PRICE\tMARKET CAPITAL (MIL)")

	for j in range(0, len(date_list[0])):		# print the date, share price and market capital row by row in 3 columns
		print(date_list[j] + "\t" + share_price_list[j] + "\t" + market_capital_list[j])	

	print()

def get_history_href(company_url):
	source_code = requests.get(company_url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	company_history = soup.find('td', 'legendWidth210 d-lightGreyFont d-fontArial')
	company_link = company_history.find('a')	# get the href for the "history" page of the company
	history_href = company_link.get('href')

	return history_href


def main():
	crawler()

if __name__ == '__main__':
	main() 
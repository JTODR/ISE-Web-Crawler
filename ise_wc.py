# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup
import time	
from company import Company

ROOT_URL = "http://www.ise.ie"
companies_list = []		# list of company objects

def crawler():

	for company in companies_list:

		company.get_history_href()
		company.get_share_price_history_table()		# get info from company's history webpage
		company.format_graph_data()	
		company.plot_graph()

		time.sleep(2)		# give the program time to breathe...

def get_all_companies():
	page = 1
	company_index = 1

	while page <= 2:
		url = "http://www.ise.ie/Market-Data-Announcements/Companies/Price-changes/"	# page 1

		if page == 2:
			url = url + "?ACTIVEGROUP=2&&type=CHANGEPRICE"	# page 2

		source_code = requests.get(url)		# get the page source
		plain_text = source_code.text 	

		soup = BeautifulSoup(plain_text, "html.parser")		# BS object with html parser
		
		i = 0
		for table_row in soup.find_all('td', 'equityName mDataGrid480'):		# class of each company name
			if (i % 2) == 0:			# every second one is "INSTRUMENT NAME" column on the web page, I dont want that...	
				for link in table_row.find_all('a'):

					company = Company(link.string, ROOT_URL + link.get('href'), company_index)		# create new company object
					companies_list.append(company)
					company_index = company_index + 1

			i = i + 1
		page = page + 1

def print_company_list():
	for company in companies_list:
		if company.index < 10:
			print(str(company.index) + '  - ' + company.name)
		else:
			print(str(company.index) + ' - ' + company.name)

def main():
	get_all_companies()
	print_company_list()
	crawler()

if __name__ == '__main__':
	main() 
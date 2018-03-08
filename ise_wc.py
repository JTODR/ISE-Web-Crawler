# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup
import time	
import company
from company import Company
import sys

ROOT_URL = "http://www.ise.ie"
companies_list = {}		# list of company objects

def crawler(index):

	if index != -1:
		companies_list[index].get_history_href()
		companies_list[index].get_share_price_history_table()		# get info from company's history webpage
		companies_list[index].format_graph_data()	
		companies_list[index].plot_graph()
		time.sleep(2)		# give the program time to breathe...

	elif index == -1:
		for key in companies_list:
			companies_list[key].get_history_href()
			companies_list[key].get_share_price_history_table()	
			companies_list[key].format_graph_data()	
			companies_list[key].plot_graph()
			time.sleep(2)		# give the program time to breathe...

def date_crawler(index, start_date, end_date):

	'''
	This function date_crawler takes in a company index, a start date DD-MM-YYY and an end date DD-MM-YYYY
	Returns a graph of the share price for the company between the start and end dates
	Web pages are limited to 30 results per page so it crawls through each page until it reaches the end date
	'''

	companies_list[index].get_history_href()

	#http://www.ise.ie/Market-Data-Announcements/Companies/Equity-History/?ACTIVEGROUP=1&&end_day=1&start_day=1&equity=2015025&end_year=2017&start_month=1&end_month=1&start_year=2018
	
	history_url_prefix = companies_list[index].history_url.split("equity=")[0]
	equity_number = companies_list[index].history_url.split("equity=")[1]

	active_group_num = 1

	dates_url = history_url_prefix \
	+ "ACTIVEGROUP=" + str(active_group_num) + "&" \
	+ "&end_day=" + end_date[0] + "&start_day=" + start_date[0] \
	+ "&equity=" + equity_number \
	+ "&end_year=" + end_date[2] + "&start_month=" + start_date[1]\
	+ "&end_month=" + end_date[1] + "&start_year=" + start_date[2]

	source_code = requests.get(dates_url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	price_history_pages = soup.find("td", "navigationPages")	# this gets the links to the pages of share prices
	number_pages = len(price_history_pages.findChildren())		# number_pages is the amount of pages we have to go through

	print()

	j = 1
	while j <= number_pages:

		if j > 1:
			new_prefix = dates_url.split("&&")[0]
			rest_of_date_url = dates_url.split("&&")[1]
			new_prefix = new_prefix[:(len(new_prefix)-1)]
			dates_url = new_prefix + str(j) + "&&" + rest_of_date_url
			#print(dates_url)
			source_code = requests.get(dates_url)
			plain_text = source_code.text
			soup = BeautifulSoup(plain_text, "html.parser")

		i = 0

		for row in soup.find_all('td', 'equityName'):
			if i % 3 == 0:
				companies_list[index].date_list.append(row.string)

			elif i % 3 == 1:
				if row.string == None:		# there are blank spaces for some share prices on the website... 
					share_price = ""
				else:
					share_price = row.string[:7]
				companies_list[index].share_price_list.append(share_price)

			elif i % 3 == 2:
				market_capital = row.string + " MIL"
				companies_list[index].market_capital_list.append(market_capital)

			i += 1
			
		complete_percentage = (j / number_pages)*100
		print(str(complete_percentage) + "% Complete...")
		j = j + 1

	companies_list[index].format_graph_data()	
	companies_list[index].plot_graph()

def get_all_companies():
	page = 1
	company_index = 1

	while page <= 2:
		url = "http://www.ise.ie/Market-Data-Announcements/Companies/Company-data/"

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
					companies_list[company_index] = company
					company_index = company_index + 1

			i = i + 1
		page = page + 1

def print_company_list():
	for key in companies_list:
		if companies_list[key].index < 10:
			print(str(companies_list[key].index) + '  - ' + companies_list[key].name )
		else:
			print(str(companies_list[key].index) + ' - ' + companies_list[key].name)

def main():
	get_all_companies()
	print("\nIrish Stock Exchange share price viewer\n")
	print_company_list()
	print()
	company.instructions()

	while True:

		invalid_input = True
		print(">>")
		user_input = sys.stdin.readline()

		if user_input < "56" and user_input > "0":
			#crawler(int(user_input))
			start_day = "1"
			start_month = "1"
			start_year = "2018"

			end_day = "1"
			end_month = "6"
			end_year = "2017"

			start_date = start_day + "-" + start_month + "-" + start_year
			end_date = end_day + "-" + end_month + "-" + end_year

			date_crawler(int(user_input), (start_day, start_month, start_year), (end_day, end_month, end_year))
			invalid_input = False
		elif "<ALL>" in user_input:
			crawler(-1)
			invalid_input = False
		elif "<COMPANIES>" in user_input:
			print_company_list()
			invalid_input = False
		elif invalid_input:
			print("\nInvalid Input...")
			company.instructions()

if __name__ == '__main__':
	main() 
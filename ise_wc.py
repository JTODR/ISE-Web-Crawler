# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup
import time	
import company
from company import Company
import sys

ROOT_URL = "http://www.ise.ie"
companies_list = {}		# list of company objects

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
			valid_date = False
			while valid_date == False:
				print("Enter a start date (DD/MM/YYYY)")
				start_date_string = sys.stdin.readline()
				print("Enter an end date (DD/MM/YYYY)")
				end_date_string = sys.stdin.readline()
				valid_date = company.check_valid_date(start_date_string, end_date_string)

			start_day = start_date_string.split('/')[0].lstrip('0')
			start_month = start_date_string.split('/')[1].lstrip('0')
			start_year = start_date_string.split('/')[2].lstrip('0')

			end_day = end_date_string.split('/')[0].lstrip('0')
			end_month = end_date_string.split('/')[1].lstrip('0')
			end_year = end_date_string.split('/')[2].lstrip('0')

			print("Retrieving data for " + companies_list[int(user_input)].name + " for dates " + start_date_string + " - " + end_date_string)

			Company.date_crawler(int(user_input), (start_day, start_month, start_year), (end_day, end_month, end_year), companies_list)
			invalid_input = False
		elif "<ALL>" in user_input:
			company.crawler(-1)
			invalid_input = False
		elif "<COMPANIES>" in user_input:
			print_company_list()
			invalid_input = False
		elif invalid_input:
			print("\nInvalid Input...")
			company.instructions()

if __name__ == '__main__':
	main() 
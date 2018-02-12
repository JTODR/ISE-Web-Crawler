# Web Crawler to crawl Irish Stock Exchange share prices over a certain period 

import requests
from bs4 import BeautifulSoup
import time	
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout

ROOT_URL = "http://www.ise.ie"
companies_list = []		# list of company objects

graph_xaxis_layout = dict(
        title='Date',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )

graph_yaxis_layout = dict(
        title='Share Price (€)',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )

class Company:
	def __init__(self, name, url):
		self.name = name
		self.url = url
		self.date_list = []
		self.share_price_list = []
		self.market_capital_list = []


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

		for table_row in soup.find_all('td', 'equityName mDataGrid480'):		# class of each company name
			
			if (i % 2) == 0:			# every second one is "INSTRUMENT NAME" column on the web page, I dont want that...	

				for link in table_row.find_all('a'):

					company = Company(link.string, ROOT_URL + link.get('href'))		# create new company object

					print(company.name)
					history_url = ROOT_URL + get_history_href(company)

					get_share_price_history_table(history_url, company)		# get info from company's history webpage

					companies_list.append(company)		# append to global list of companies

					format_data(company)	
					plot_graph(company)

					time.sleep(2)		# give the program time to breathe...

			#break

			i += 1
		page = page + 1

	print("Finished!")


def get_share_price_history_table(history_href, company):
	source_code = requests.get(history_href)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	i = 0

	for row in soup.find_all('td', 'equityName'):
		if i % 3 == 0:
			company.date_list.append(row.string)

		elif i % 3 == 1:
			share_price = row.string[:7]
			company.share_price_list.append(share_price)

		elif i % 3 == 2:
			market_capital = row.string + " MIL"
			company.market_capital_list.append(market_capital)

		i += 1

def format_data(company):

	# reverse the lists for plotting as graph
	company.date_list = company.date_list[::-1]
	company.share_price_list = company.share_price_list[::-1]
	company.market_capital_list = company.market_capital_list[::-1]

	print("DATE\t\tCLOSING PRICE (€)\tMARKET CAPITAL (MIL)")

	for j in range(0, len(company.date_list[0])):		# print the date, share price and market capital row by row in 3 columns
		print(company.date_list[j] + "\t" + company.share_price_list[j] + "\t\t\t" + company.market_capital_list[j])	

	print()

def plot_graph(company):
	
	# Create a trace  - used to create date for the plot
	trace = go.Scatter(
	    x = company.date_list,
	    y = company.share_price_list
	)

	data = [trace]

	layout = go.Layout( title= company.name, xaxis= graph_xaxis_layout, yaxis= graph_yaxis_layout)	
	fig = go.Figure(data=data, layout=layout)

	plotly.offline.plot(fig, filename='share_price_vs_date.html')

def get_history_href(company):
	source_code = requests.get(company.url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text, "html.parser")

	company_history = soup.find('td', 'legendWidth210 d-lightGreyFont d-fontArial')
	company_link = company_history.find('a')	
	history_href = company_link.get('href')		# get the href for the "history" page of the company

	return history_href


def main():
	crawler()

if __name__ == '__main__':
	main() 
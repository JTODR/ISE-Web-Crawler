import requests
from bs4 import BeautifulSoup
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout
from datetime import date


ROOT_URL = "http://www.ise.ie"

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
	def __init__(self, name, url, index):
		self.name = name
		self.url = url
		self.index = index
		self.history_url = ROOT_URL		# initialise to ROOT URL
		self.date_list = []
		self.share_price_list = []
		self.market_capital_list = []

	def get_share_price_history_table(self):
		source_code = requests.get(self.history_url)
		plain_text = source_code.text
		soup = BeautifulSoup(plain_text, "html.parser")

		i = 0

		for row in soup.find_all('td', 'equityName'):
			if i % 3 == 0:
				self.date_list.append(row.string)

			elif i % 3 == 1:
				share_price = row.string[:7]
				self.share_price_list.append(share_price)

			elif i % 3 == 2:
				market_capital = row.string + " MIL"
				self.market_capital_list.append(market_capital)

			i += 1

	def format_graph_data(self):

		# reverse the lists for plotting as graph
		self.date_list = self.date_list[::-1]
		self.share_price_list = self.share_price_list[::-1]
		self.market_capital_list = self.market_capital_list[::-1]

		print("\n")
		print_breaker()
		print("\t\t\t" + self.name)
		print_breaker()

		print("DATE\t\tCLOSING PRICE (€)\tMARKET CAPITAL (MIL)")

		for j in range(0, len(self.date_list[0])):		# print the date, share price and market capital row by row in 3 columns
			print(self.date_list[j] + "\t" + self.share_price_list[j] + "\t\t\t" + self.market_capital_list[j])	

		print()

	def plot_graph(self):
		
		# Create a trace  - used to create date for the plot
		trace = go.Scatter(
		    x = self.date_list,
		    y = self.share_price_list
		)

		data = [trace]

		layout = go.Layout( title= self.name, xaxis= graph_xaxis_layout, yaxis= graph_yaxis_layout)	
		fig = go.Figure(data=data, layout=layout)

		plotly.offline.plot(fig, filename='share_price_vs_date.html')

	def get_history_href(self):
		source_code = requests.get(self.url)
		plain_text = source_code.text
		soup = BeautifulSoup(plain_text, "html.parser")

		company_history = soup.find('td', 'legendWidth210 d-lightGreyFont d-fontArial')
		company_link = company_history.find('a')	
		history_href = company_link.get('href')		# get the href for the "history" page of the company
		self.history_url += history_href

	def date_crawler(index, start_date, end_date, companies_list):

		'''
		This function date_crawler takes in a company index, a start date DD-MM-YYY and an end date DD-MM-YYYY
		Displays a graph of the share price for the company between the start and end dates
		Web pages are limited to 30 results per page so it crawls through each page until it reaches the end date
		'''

		companies_list[index].get_history_href()

		#http://www.ise.ie/Market-Data-Announcements/Companies/Equity-History/?ACTIVEGROUP=1&&end_day=4&start_day=1&equity=2015070&end_year=2017&start_month=1&end_month=4&start_year=2018

		history_url_prefix = companies_list[index].history_url.split("equity=")[0]
		equity_number = companies_list[index].history_url.split("equity=")[1]

		active_group_num = 1

		# some weird thing going on with their URL, the start and end date figures are flipped...
		dates_url = history_url_prefix \
		+ "ACTIVEGROUP=" + str(active_group_num) + "&" \
		+ "&end_day=" + start_date[0] + "&start_day=" + end_date[0] \
		+ "&equity=" + equity_number \
		+ "&end_year=" + start_date[2] + "&start_month=" + end_date[1]\
		+ "&end_month=" + start_date[1] + "&start_year=" + end_date[2]
		
		print(dates_url)

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

def print_breaker():
	print("--------------------------------------------------------------------")

def instructions():
	print_breaker()
	print("Instructions")
	print_breaker()
	print("<COMPANIES> - shows a list of all company names on the ISE")
	print("<number from 1-56> - shows the share price history for that company")
	print("<ALL> - shows every company share price sequentially")
	print_breaker()
	print("\n")

def check_valid_date(start_date_string, end_date_string):

	if 	start_date_string[2] == '//' or start_date_string[5] == '//' or \
		end_date_string[2] == '//' or end_date_string[5] == '//' or \
		len(start_date_string) != 11 or len(end_date_string) != 11:
		
		print("\nInvalid date entered...")
		return False

	f_date = date(int(start_date_string.split('/')[2].lstrip('0')), int(start_date_string.split('/')[1].lstrip('0')), int(start_date_string.split('/')[0].lstrip('0')))
	l_date = date(int(end_date_string.split('/')[2].lstrip('0')), int(end_date_string.split('/')[1].lstrip('0')), int(end_date_string.split('/')[0].lstrip('0')))
	delta = l_date - f_date
	print(delta.days)
	if delta.days <= 365:
		return True
	else:
		print("Start and end date cannot be more than 1 year apart... Enter new dates")
		return False

def crawler(index):

	if index == -1:
		companies_list[index].get_history_href()
		companies_list[index].get_share_price_history_table()		# get info from company's history webpage
		companies_list[index].format_graph_data()	
		companies_list[index].plot_graph()
		time.sleep(2)		# give the program time to breathe...
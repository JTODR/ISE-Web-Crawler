import requests
from bs4 import BeautifulSoup
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout

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

		print("\n------------------------------------------------------")
		print("\t\t\t" + self.name)
		print("------------------------------------------------------")

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
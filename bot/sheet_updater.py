import gspread
from oauth2client.service_account import ServiceAccountCredentials
import API as Cobi
import json
import subprocess


def supervisor_status(processname):
    p = subprocess.Popen(['supervisorctl', 'status ' + processname],
                         stdout=subprocess.PIPE, universal_newlines=True)
    response = p.communicate()[0]
    print(response)
    l_response = response.split()
    if str(l_response[2]) == "pid":
        return [str(l_response[1]), l_response[5]]
    else:
        return [str(l_response[1]), str(l_response[2]) + " " + str(l_response[3]) + " " + str(l_response[4]) + " " + str(l_response[5])]


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    './credentials/CHTB-2b1a68fd04ff.json', scope)

gc = gspread.authorize(credentials)

CHTB = gc.open("CHTB")

# Dashboard sheet (Parameters, Balance and Supervisor)
Dashboard = CHTB.get_worksheet(0)

# First the Balances
BTC_Balance = float(Cobi.get_BTC_balance())
USDT_Balance = float(Cobi.get_USDT_balance())
BTC_Price = (float(Cobi.get_ask_price(
    Cobi.basic_trading_pairs_ids[0])['price']) +
    float(Cobi.get_bid_price(
        Cobi.basic_trading_pairs_ids[0])['price']))/2
Calculated = (BTC_Price * BTC_Balance) + USDT_Balance
Cells_value = [round(USDT_Balance, 2), BTC_Balance,
               BTC_Price, round(Calculated, 2)]

cell_list = Dashboard.range('B3:E3')
i = 0
for cell in cell_list:
    cell.value = Cells_value[i]
    i += 1

Dashboard.update_cells(cell_list)

# Then the parameters
f = open("parameters.json", "r")
if f.mode == 'r':
    content = f.read()
f.close()
d = json.loads(content)
Dashboard.update_acell('B4', d['PM1'])
Dashboard.update_acell('B5', d['PM2'])

# Last supervisor status
adjust = supervisor_status('adjust')
scraper = supervisor_status('scraper')
strategy = supervisor_status('strategy')
trader = supervisor_status('trader')
Dashboard.update_acell('B7', adjust[0])
Dashboard.update_acell('B8', scraper[0])
Dashboard.update_acell('B9', strategy[0])
Dashboard.update_acell('B10', trader[0])
Dashboard.update_acell('C7', adjust[1])
Dashboard.update_acell('C8', scraper[1])
Dashboard.update_acell('C9', strategy[1])
Dashboard.update_acell('C10', trader[1])

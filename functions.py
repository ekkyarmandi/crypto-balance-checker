# selenium libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

# data manipulation libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json

headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

def render_html(url):
    req = requests.get(url,headers=headers)
    page = BeautifulSoup(req.content,"html.parser")
    return page

def find_table(page):
    for div in page.find_all("div",{"class":"MuiPaper-root"}):
        try:
            h3 = div.find("h3")
            if h3.get_text() in ["Wallet"]:
                table = div.find("table")
                return table
        except: pass
    return None

def find_tokens(table):
    try:
        balances = {}
        for row in table.find("tbody").find_all("tr"):
            td = row.find_all("td")
            symbol = td[0].get_text().strip()
            balance = td[1].get_text().strip()
            balances.update({symbol:balance})
        return balances
    except: return None

def replace_dot(variable):
    if "." in variable: return variable.strip(".")
    else: return variable.strip()
    
class BalanceChecker():

    # open the browser
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service("chromedriver.exe")
    browser = Chrome(service=service,options=options)
    browser.set_window_position(-10000,0)

    # consume the CSV file
    def __init__(self,csv_file):
        self.apis = self.df2dict(csv_file)

    # converting csv file into dictionary
    def df2dict(self,csv_file):
        '''
        Converting CSV into Dictinary
        :param csv_file: str -> path of the csv file
        :return apis: dict -> converted data
        '''
        data = pd.read_csv(csv_file)
        data.set_index("WEBSITE",inplace=True)
        apis = {}
        for key in data.index.unique():
            api = data.loc[key,"API"]
            if type(api) != str:
                api = api.unique()[0]
            coins = data.loc[key]
            try:
                coins = coins.groupby("ADDRESS")['hoi'].agg(",".join).to_dict()
            except:
                coins = coins.to_dict()
                coins = {coins['ADDRESS']:coins['hoi']}
            entities = {
                "api": api,
                "source": coins
            }
            apis.update({key:entities})
        return apis

    def get_balance(self,website,api,address):
        '''
        Finding coin balance based on website name and token address.
        :param website: str -> as the logic branch value
        :param api: str -> api end point for retriving the data using requests method
        :param address: str -> token address
        :return tokens: dict -> filtered tokens according to custom coin symbol
        '''

        tokens = {}
        if website == "https://explore.vechain.org/":
            page = render_html(api+address)
            page = page.find_all("div",{"class":"row no-gutters"})[1:]
            for row in page:
                content = row.find_all("div")[-1].find_all("small")[0]
                content = content.text.strip().split(" ")
                new_token = {content[1]:float(content[0].replace(",",""))}
                tokens.update(new_token)

        elif website == "https://polkadot.subscan.io/":
            payload = {"key":address,"page":0,"row":1}
            data = requests.post(api, headers=headers, data=json.dumps(payload)).json()
            new_token = {"DOT":float(data['data']['account']['balance'])}
            tokens.update(new_token)

        elif website == "https://ww7.etherscan.io/":
            with requests.Session() as session:
                r = session.get(api + address, headers=headers)
                soups = BeautifulSoup(r.text,"html.parser")
                table = soups.find("table",{"id":"mytable"})
                for row in table.find("tbody").find_all("tr"):
                    td = row.find_all("td")
                    token_name = replace_dot(td[1].text)
                    balance = replace_dot(td[3].text)
                    new_token = {
                        token_name:float(balance)
                    }
                    tokens.update(new_token)

        elif website == "https://algoexplorer.io/":
            data = requests.get(api+address,headers=headers).json()
            amount = str(data['amount'])
            decimals = amount[-6:]
            amount = amount.replace(decimals,"."+decimals)
            new_token = {
                "ALGO":float(amount)
            }
            tokens.update(new_token)

        elif website == "https://siastats.info/":
            data = requests.get(api+address,headers=headers).json()[1]
            balance = str(data['balanceSc'])
            balance = balance.replace("e+32","e+8")
            balance = eval(balance)
            new_token = {
                "SC":balance
            }
            tokens.update(new_token)

        elif website == "https://xrpscan.com/":
            with requests.Session() as session:
                r = session.get(api+address,headers=headers)
                r = session.get(api+address,headers=headers)
                data = r.json()
                balance = data['initial_balance']
                new_token = {
                    "XRP":balance
                }
                tokens.update(new_token)

        elif website == "https://hash-hash.info/":
            try:
                data = requests.get(api.format(address.split(".")[-1]),headers=headers).json()
                balance = data['balance']/1e8
                new_token = {
                    "HBAR":balance
                }
                tokens.update(new_token)
            except: pass

        elif website == "https://explorer.elrond.com/":
            data = requests.get(api+address,headers=headers).json()
            balance = float(data['balance'])/1e18
            new_token = {
                "EGLD":balance
            }
            tokens.update(new_token)

        elif website == "https://explorer.helium.com/":
            data = requests.get(api+address,headers=headers).json()
            balance = (data['data']['staked_balance'] + data['data']['balance']) / 1e8
            new_token = {
                "HNT":balance
            }
            tokens.update(new_token)

        elif website == "https://apeboard.finance/":        
            self.browser.get(api+address)
            try:
                xpath = '//*[@id="__next"]/div[2]/div[3]/div[1]/div[5]'
                WebDriverWait(self.browser,10).until(EC.visibility_of_element_located((By.XPATH,xpath)))
                page = BeautifulSoup(self.browser.page_source,"html.parser")
                table = find_table(page)
                new_tokens = find_tokens(table)
                tokens.update(new_tokens)
            except: pass
            self.browser.quit()

        return tokens
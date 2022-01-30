# import functions and necessary library
from functions import BalanceChecker
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import time, os

# import colorama libraries
from colorama import init, Fore, Style
init()

# timestamp the start
start = time.time()

# assign the balance checker object
bc = BalanceChecker("Explorers V3.csv")

# check all the address balance
tokens = []
today = datetime.now().strftime("%d/%m/%Y")
for website in tqdm(bc.apis,"Get Balance"):
    api = bc.apis[website]['api']
    for address,symbols in bc.apis[website]['source'].items():
        new_tokens = bc.get_balance(website,api,address)
        for symbol in symbols.split(","):
            try: balance = new_tokens[symbol]
            except: balance = 0
            token = {
                "SCRAPING DATE": today,
                "TOKEN": symbol,
                "ADDRESS": address,
                "BALANCE": balance
            }
            tokens.append(token)

# Concate to existing file
outputfile = "Token Table.csv"
if os.path.exists(outputfile):
    old_data = pd.read_csv(outputfile)
    results = pd.DataFrame(tokens)
    results = pd.concat([old_data,results])
    results.to_csv(outputfile,index=False)
else:
    results = pd.DataFrame(tokens)
    results.to_csv(outputfile,index=False)

# printout the time elapse
print(Fore.GREEN + "Done in {:.2f} sec".format(time.time()-start) + Style.RESET_ALL)

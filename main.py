# import functions and necessary library
from datetime import datetime
from tqdm import tqdm
import functions as fun
import pandas as pd
import time

# import colorama libraries
from colorama import init, Fore, Style
init()

def print_green(text):
    print(Fore.GREEN + str(text) + Style.RESET_ALL)

# timestamp the start
start = time.time()

# scraping the Crypto Explorer
tokens = []
apis = fun.df2dict("Explorers V3.csv")
today = datetime.now().strftime("%d/%m/%Y")
for website in tqdm(apis,"Get Balance"):
    api = apis[website]['api']
    for address,symbols in apis[website]['source'].items():
        new_tokens = fun.get_balance(website,api,address)
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

# convert data into dataframe
outputfile = "Token Table.csv"
old_data = pd.read_csv(outputfile)
results = pd.DataFrame(tokens)
results = pd.concat([old_data,results])
results.to_csv(outputfile,index=False)

# printout the elapse time
print_green("Done in {:.2f} sec".format(time.time()-start))
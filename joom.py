import sys
import requests
from colorama import Fore, init
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

init(autoreset=True)

shape = Fore.RED + "[" + Fore.GREEN + "+" + Fore.RED + "] "

print("""\033[1m

Made By @linuxdebain
    channel  t.me/Opensource3

""")

def CMS_detector(host):
    host = host.strip() 
    if not (host.startswith("http://") or host.startswith("https://")):
        host = "http://" + host

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        response = requests.get(host, headers=headers, timeout=10)  # Added timeout
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        generator_meta = soup.find('meta', attrs={'name': 'generator'})
        
        if generator_meta and 'content' in generator_meta.attrs:
            content = generator_meta['content']
            if 'Joomla! - Open Source Content Management' in content:
                print('\033[1m' + shape + host + Fore.RED + " CMS : " + Fore.GREEN + "[ Joomla ]" + "\n")
            else:
                print('\033[1m' + shape + host + Fore.RED + " CMS : " + Fore.GREEN + " Other CMS detected, not Joomla" + "\n")
        else:
            print('\033[1m' + shape + host + Fore.GREEN + " No CMS detected" + "\n")
            
    except requests.exceptions.RequestException as e:
        print('\033[1m' + shape + f" An error occurred with : " + Fore.RED + host + Fore.GREEN + {e})

def main(file_name):
    try:
        with open(file_name, "r") as file:
            targets = file.readlines()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_host = {executor.submit(CMS_detector, url): url.strip() for url in targets}
            for future in as_completed(future_to_host):
                future.result() 
        
    except FileNotFoundError:
        print('\033[1m' + shape + Fore.RED + "No such file or directory" + "\n")
    except IndexError:
        print('\033[1m' + shape + Fore.GREEN + "Usage: python3 " + sys.argv[0] + " list.txt" + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print('\033[1m' + shape + Fore.GREEN + "Usage: python3 " + sys.argv[0] + " list.txt" + "\n")

import requests
import urllib3
import time
import concurrent.futures
import os
import uuid
import ctypes
from random import choice
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path
import threading

file_path = "promos.txt"
file_path_obj = Path(file_path)
if not file_path_obj.exists():
    file_path_obj.touch()
os.system('cls' if os.name == 'nt' else 'clear')

class Counter:
    count = 0

class PromoGenerator:
    red = '\x1b[31m(-)\x1b[0m'
    blue = '\x1b[34m(+)\x1b[0m'
    green = '\x1b[32m(+)\x1b[0m'
    yellow = '\x1b[33m(!)\x1b[0m'

    def __init__(self, proxies=None):
        self.proxies = proxies
        self.current_proxy = None

    def create_session(self, proxy=None):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if proxy:
            proxy_url = f"http://{proxy}"
            manager = urllib3.ProxyManager(proxy_url)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            session.proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
        return session

    def generate_promo(self):
        if self.proxies:
            self.current_proxy = choice(self.proxies)
            session = self.create_session(proxy=self.current_proxy)

            url = "https://api.discord.gx.games/v1/direct-fulfillment"
            headers = {
                "Content-Type": "application/json",
                "Sec-Ch-Ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0 (Edition GX-CN)",
            }

            data = {
                "partnerUserId": str(uuid.uuid4())
            }

            try:
                response = session.post(url, json=data, headers=headers, timeout=5)

                if response.status_code == 200:
                    token = response.json().get('token')
                    if token:
                        with threading.Lock():
                            Counter.count += 1
                            ctypes.windll.kernel32.SetConsoleTitleW(
                                f"プロモNitro Generator| Generated : {Counter.count}")
                            link = f"https://discord.com/billing/partner-promotions/1180231712274387115/{token}"
                            with open("promos.txt", "a") as f:
                                f.write(f"{link}\n")
                            print(f"{self.get_timestamp()} {self.green} Generated Promo Link : {link}")

                            # Remove used proxy from the list
                            self.proxies.remove(self.current_proxy)
                            with open("proxies.txt", "w") as proxy_file:
                                proxy_file.write("\n".join(self.proxies))
                elif response.status_code == 429:
                    print(f"{self.get_timestamp()} {self.yellow} 429 Error")
                    self.change_proxy()
                else:
                    print(f"{self.get_timestamp()} {self.red} Request failed : {response.status_code}")

                    # Remove invalid or unusable proxy from the list
                    self.proxies.remove(self.current_proxy)
                    with open("proxies.txt", "w") as proxy_file:
                        proxy_file.write("\n".join(self.proxies))

                    self.change_proxy()
            except Exception as e:
                print(f"{self.get_timestamp()} {self.red} Request Failed : {e}")

                # Remove invalid or unusable proxy from the list
                self.proxies.remove(self.current_proxy)
                with open("proxies.txt", "w") as proxy_file:
                    proxy_file.write("\n".join(self.proxies))

                self.change_proxy()
            finally:
                # Close the session after generating the promo link
                session.close()
        else:
            print(f"{self.get_timestamp()} {self.red} No more proxies available.")
            os._exit(0)

    def change_proxy(self):
        if self.proxies:
            print(f"{self.get_timestamp()} {self.yellow} Changed Proxy to: {self.current_proxy}")
        else:
            print(f"{self.get_timestamp()} {self.red} No more proxies available.")
            os._exit(0)

    @staticmethod
    def get_timestamp():
        time_idk = time.strftime('%H:%M:%S')
        return f'[\x1b[90m{time_idk}\x1b[0m]'

class PromoManager:
    def __init__(self):
        while True:
            try:
                self.num_threads = int(input(f"{PromoGenerator.get_timestamp()} {PromoGenerator.blue} Enter Number Of Threads : "))
                if self.num_threads > 0:
                    break
                else:
                    print("Number of threads must be greater than 0.")
            except ValueError:
                print("Please enter a valid integer.")

        with open("proxies.txt") as f:
            self.proxies = f.read().splitlines()

    def start_gen(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = {executor.submit(self.generate_promo): i for i in range(self.num_threads)}
            try:
                concurrent.futures.wait(futures)
            except KeyboardInterrupt:
                for future in concurrent.futures.as_completed(futures):
                    future.result()

    def generate_promo(self):
        generator = PromoGenerator(proxies=self.proxies)
        while True:
            try:
                generator.generate_promo()
            except Exception as e:
                print(f"{generator.get_timestamp()} {generator.red} Thread failed : {e}")

if __name__ == "__main__":
    manager = PromoManager()
    manager.start_gen()

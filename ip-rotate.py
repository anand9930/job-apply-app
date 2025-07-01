from stem import Signal
from stem.control import Controller
import time
import requests

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def get_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='anand')  # Set this in your torrc!
        controller.signal(Signal.NEWNYM)

def get_ip():
    try:
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        print("Current IP:", r.json()['origin'])
    except Exception as e:
        print("Request failed:", e)

# Change IP and check
get_ip()
get_new_ip()
time.sleep(5)  # wait for circuit change
get_ip()
get_new_ip()
time.sleep(5)
get_ip()
get_new_ip()
time.sleep(5) 
get_ip()
get_new_ip()
time.sleep(5) 


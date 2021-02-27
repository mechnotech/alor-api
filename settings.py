from dotenv import load_dotenv
import os

load_dotenv()

LOGGING = True
DEVMODE = True
TTL_JWT_TOKEN = 60
USERNAME = os.getenv('ALOR_USERNAME')
EXCHANGE = 'MOEX'
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
URL_OAUTH = f'https://oauth{"dev" if DEVMODE else ""}.alor.ru'
URL_API = f'https://api{"dev" if DEVMODE else ""}.alor.ru'


OIL = ['BRH1', 'BRJ1', 'BRK1', 'BRM1', 'BRN1', 'BRQ1',
       'BRU1', 'BRV1', 'BRX1', 'BRZ1', 'BRF2', 'BRG2'
       ]
RTC = ['RIH1', 'RIM1', 'RIU1', 'RIZ1', 'RIH2', 'RIM2', 'RIU2', 'RIZ2']
USD = ['SiH1', 'SiM1', 'SiU1', 'SiZ1', 'SiH2', 'SiM2', 'SiU2', 'SiZ2']
EU = ['EuH1', 'EuM1', 'EuU1', 'EuZ1', 'EuH2', 'EuM2']
GOLD = ['GDH1', 'GDM1', 'GDU1', 'GDZ1']
FUTURES_SET = GOLD + EU + USD + RTC + OIL

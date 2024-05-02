import time
from loguru import logger
from web3 import Web3
from colorama import Fore
from sys import stderr
import random
import json
from tqdm import trange
import telebot
import requests
import aiohttp

from settings import decimal_places, RETRY_COUNT, delay_wallets, value_eth, delay_transactions

ERC20_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"_l2Bridge","type":"address"},{"internalType":"address","name":"_l1Token","type":"address"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint8","name":"decimals","type":"uint8"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"Blacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newBlacklister","type":"address"}],"name":"BlacklisterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_account","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"pauser","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousPauser","type":"address"},{"indexed":true,"internalType":"address","name":"newPauser","type":"address"}],"name":"PauserChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"UnBlacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"pauser","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"blacklister","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"changeOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isBlacklisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"l1Token","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"l2Bridge","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pauser","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"setPauser","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"_interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"unBlacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newBlacklister","type":"address"}],"name":"updateBlacklister","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")
waiting_gas = 100                                                   # макс значение газа при котором будет работать скрипт

number_wallets = 0
SUCCESS = '✅ '
FAILED = '⚠️ '
ERROR = '❌ '

send_list = ''

RPC = {
    'Ethereum': 'https://rpc.ankr.com/eth',
    'Optimism': 'https://rpc.ankr.com/optimism',
    'BSC': '',
    'Gnosis': '',
    'Polygon': '',
    'Fantom': '',
    'Arbitrum': 'https://arbitrum-one-rpc.publicnode.com',
    'Avalanche': '',
    'zkSync': 'https://zksync-era.rpc.thirdweb.com',
    'zkEVM': 'https://rpc.ankr.com/polygon_zkevm',
    'Zora': '',
    'Scroll': 'https://1rpc.io/scroll',
    'Linea': 'https://linea.decubate.com',
    'zkFair': 'https://42766.rpc.thirdweb.com',
    'Mode': 'https://1rpc.io/mode',
    'Base': 'https://base.meowrpc.com',
}

SCANS = {
    'Ethereum': 'https://etherscan.io/tx/',
    'Optimism': 'https://optimistic.etherscan.io/tx/',
    'BSC': 'https://bscscan.com/tx/',
    'Gnosis': 'https://gnosisscan.io/tx/',
    'Polygon': 'https://polygonscan.com/tx/',
    'Fantom': 'https://ftmscan.com/tx/',
    'Arbitrum': 'https://arbiscan.io/tx/',
    'Avalanche': 'https://snowtrace.io/tx/',
    'zkSync': 'https://explorer.zksync.io/tx/',
    'zkEVM': 'https://zkevm.polygonscan.com/tx/',
    'Zora': 'https://explorer.zora.energy/tx/',
    'Scroll': 'https://scrollscan.com/tx/',
    'Linea': 'https://etherscan.io/tx/',
    'zkFair': 'https://scan.zkfair.io/tx/',
    'Mode': 'https://explorer.mode.network/tx/',
    'Base': 'https://basescan.org/tx/',
}

CHAIN_IDS = {
    'Ethereum': 1,
    'Optimism': 10,
    'BSC': 56,
    'Gnosis': 100,
    'Polygon': 137,
    'Fantom': 250,
    'Arbitrum': 42161,
    'Avalanche': 43114,
    'zkSync': 324,
    'zkEVM': 1101,
    'Zora': 7777777,
    'Scroll': 534352,
    'Linea': 59144,
    'zkFair': 42766,
    'Mode': 34443,
    'Base': 8453,

}

CHAIN_NAMES = {
    1: 'Ethereum',
    10: 'Optimism',
    56: 'BSC',
    100: 'Gnosis',
    137: 'Polygon',
    250: 'Fantom',
    42161: 'Arbitrum',
    43114: 'Avalanche',
    1313161554: 'Aurora',
    324: 'zkSync',
    1101: 'zkEVM',
    7777777: 'Zora',
    534352: 'Scroll',
    59144: 'Linea',
    42766: 'zkFair',
    34443: 'Mode',
    8453: 'Base',
}


class Account:
    def __init__(self, id, private_key, proxy, rpc):
        self.private_key = private_key
        self.proxy = proxy
        self.id = id
        self.ChainName = rpc

        if self.proxy != None:
            self.w3 = Web3(Web3.HTTPProvider(RPC[rpc], request_kwargs={"proxies": {'https': "http://" + self.proxy, 'http': "http://" + self.proxy}}))
        else:
            self.w3 = Web3(Web3.HTTPProvider(RPC[rpc]))
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.scan = SCANS[CHAIN_NAMES[self.w3.eth.chain_id]]

    def change_network(self, new_rpc):
        self.ChainName = new_rpc
        if self.proxy != None:
            self.w3 = Web3(Web3.HTTPProvider(RPC[new_rpc], request_kwargs={
                "proxies": {'https': "http://" + self.proxy, 'http': "http://" + self.proxy}}))
        else:
            self.w3 = Web3(Web3.HTTPProvider(RPC[new_rpc]))
        self.scan = SCANS[CHAIN_NAMES[self.w3.eth.chain_id]]

    def wait_balance(self, value, rpc):
        x = 0
        self.w3 = Web3(Web3.HTTPProvider(RPC[rpc]))
        while x < 4:
            balance = self.get_balance()
            if balance["balance_wei"] >= value * 0.8:
                logger.info(f'Balance: {"{:0.9f}".format(balance["balance"])} {balance["symbol"]}')
                print()
                return True
            else:
                logger.info(f'Balance: {"{:0.9f}".format(balance["balance"])} {balance["symbol"]} wait deposit...')
                time.sleep(45)
                x += 1
        return False

    def get_value(self):
        if type(value_eth[0]) == str:
            percent = round(random.uniform(float(value_eth[0]), float(value_eth[1])), decimal_places) / 100
            balance = self.get_balance()
            balance_eth = balance['balance'] * percent
            balance_wei = int(balance['balance_wei'] * percent)
            return balance_eth, balance_wei

        else:
            balance_eth = round(random.uniform(value_eth[0], value_eth[1]), decimal_places)
            balance_wei = int(self.w3.to_wei(balance_eth, 'ether'))
            return balance_eth, balance_wei

    def get_contract(self, contract_address, abi=None):
        contract_address = Web3.to_checksum_address(contract_address)

        if abi is None:
            abi = ERC20_ABI

        contract = self.w3.eth.contract(address=contract_address, abi=abi)

        return contract

    def get_balance(self, contract_address: str = 'native'):
        if contract_address == 'native':
            balance_wei = self.w3.eth.get_balance(self.address)
            balance_eth = balance_wei / 10 ** 18
            return {"balance_wei": balance_wei, "balance": balance_eth, "symbol": 'ETH', "decimal": 18}

        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.get_contract(contract_address)

        symbol = contract.functions.symbol().call()
        decimal = contract.functions.decimals().call()
        balance_wei = contract.functions.balanceOf(self.address).call()

        balance = balance_wei / 10 ** decimal

        return {"balance_wei": balance_wei, "balance": balance, "symbol": symbol, "decimal": decimal}

    def check_allowance(self, token_address, contract_address):
        token_address = Web3.to_checksum_address(token_address)
        contract_address = Web3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        amount_approved = contract.functions.allowance(self.address, contract_address).call()

        return amount_approved

    def approve(self, amount, token_address, contract_address):
        global send_list
        send_list = ''
        token_address = Web3.to_checksum_address(token_address)
        contract_address = Web3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)

        allowance_amount = self.check_allowance(token_address, contract_address)

        if amount > allowance_amount or amount == 0:

            approve_amount = 2 ** 128

            tx_data = get_tx_data_withABI(self)

            transaction = contract.functions.approve(
                contract_address,
                approve_amount
            ).build_transaction(tx_data)

            txstatus, tx_hash = sign_and_send_transaction(self, transaction)

            balance_dict = Account.get_balance(self, token_address)
            if txstatus == 1:
                logger.success(f'Token: Approve {approve_amount} {balance_dict["symbol"]} : {self.scan + tx_hash}')
                send_list += (f'\n{SUCCESS}Token: Approve {approve_amount} {balance_dict["symbol"]} - [tx hash]({self.scan + tx_hash})')
                return send_list

            else:
                logger.error(f'Token: Approve {approve_amount} {balance_dict["symbol"]} : {self.scan + tx_hash}')
                send_list += (f'\n{FAILED}Token: Approve {approve_amount} {balance_dict["symbol"]} - [tx hash]({self.scan + tx_hash})')
                return send_list

    def get_decimals(self, token_address):
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(token_address), abi=ERC20_ABI)
        return contract.functions.decimals().call()

def retry(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries <= RETRY_COUNT:
            try:
                time.sleep(15)
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                time.sleep(10)
                retries += 1

    return wrapper

def sleeping_between_wallets():
    x = random.randint(delay_wallets[0], delay_wallets[1])
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep...', ncols=50, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

def sleeping_between_transactions():
    x = random.randint(delay_transactions[0], delay_transactions[1])
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep between transaction...', ncols=65, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

def get_token_price(from_token, to_token):
    from_token, to_token = from_token.upper(), to_token.upper()
    result_dict = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={from_token}{to_token}').json()
    if 'msg' in result_dict and 'Invalid symbol' in result_dict['msg']:
        result_dict = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={to_token}{from_token}').json()
    return float(result_dict['price'])

def get_min_to_amount(from_token: str, to_token: str, decimals: float = 0.5):
    token_price = get_token_price(from_token, to_token)
    return token_price * (1 - decimals / 100)

@retry
def send_message(bot_token, bot_id, send_list):
    try:
        str_send = [i for i in send_list if i is not None]
        str_send_without_none = '\n'.join(str_send)
        bot = telebot.TeleBot(bot_token)
        bot.send_message(bot_id, str_send_without_none, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as error:
        logger.error(error)

@retry
def check_gas(func):
    def wrapper(*args, **kwargs):
        wait_gas()
        return func(*args, **kwargs)
    return wrapper

@retry
def wait_gas():
    try:
        rpc_url_eth = Web3(Web3.HTTPProvider('https://rpc.flashbots.net'))
        gas = rpc_url_eth.to_wei(waiting_gas, 'gwei')
        while True:
            gasPrice = int(rpc_url_eth.eth.gas_price)
            if gasPrice < gas:
                logger.success(f"GWEI is normal | current: {gasPrice} < {gas}")
                break
            logger.info(f'Waiting {waiting_gas} Gwei. Actual: {round(rpc_url_eth.from_wei(gasPrice, "gwei"), 1)} Gwei')
            time.sleep(120)
    except:
        wait_gas()

def convert_to(number, base, upper=False):
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    if base > len(digits): return None
    result = ''
    while number > 0:
        result = digits[number % base] + result
        number //= base
    return result.upper() if upper else result

def intro(wallets):
    print()
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    #input('Press ENTER: ')

    print()
    print(f'| {Fore.LIGHTGREEN_EX}deBridge{Fore.RESET} |'.center(100, '='))
    print('\n')

def outro():
    for i in trange(3, desc=f'{Fore.LIGHTBLACK_EX}End process...', ncols=50, bar_format='{desc} {percentage:3.0f}%'):
        time.sleep(1)
    print(f'{Fore.RESET}\n')
    print(f'| {Fore.LIGHTGREEN_EX}END{Fore.RESET} |'.center(100, '='))
    print()
    print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))

def add_gas_limit(transaction, rpc_url):
    try:
        gasLimit = rpc_url.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.2))
    except:
        transaction['gas'] = random.randint(380000, 420000)
    return transaction

def get_tx_data_withABI(self, value=0):
    tx_data = {
        "from": self.address,
        "gasPrice": int(self.w3.eth.gas_price * 1.05),
        "nonce": self.w3.eth.get_transaction_count(self.address),
        "value": value,
    }
    return tx_data

def get_tx_data(self, to, value=0, data=None):
    tx_data = {
        "chainId": self.w3.eth.chain_id,
        "from": self.address,
        "to": self.w3.to_checksum_address(to),
        "gasPrice": int(self.w3.eth.gas_price * 1.05),
        "nonce": self.w3.eth.get_transaction_count(self.address),
        "value": value,
        "gas": 0,
    }
    if data != None:
        tx_data["data"] = data

    return tx_data

def sign_and_send_transaction(self, transaction, gas=None):
    if gas == None:
        gas = int(self.w3.eth.estimate_gas(transaction) * 1.2)

    transaction.update({"gas": gas})

    signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)

    tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    time.sleep(12)

    txstatus = self.w3.eth.wait_for_transaction_receipt(tx_hash).status

    tx_hash = self.w3.to_hex(tx_hash)

    return txstatus, tx_hash

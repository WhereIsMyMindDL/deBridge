import time
import json
from pyuseragents import random as random_ua
from requests import Session
import random
import ccxt
from loguru import logger
import requests

from settings import count_bridge, amount, symbolWithdraw, decimal_places, transfer_subaccount, API, network_list, stay_eth, referralCode
from help import Account, retry, sign_and_send_transaction, sleeping_between_transactions, SUCCESS, FAILED, get_tx_data_withABI, get_tx_data, get_min_to_amount, CHAIN_IDS


send_list = ''

switch_cex = "okx"
proxy_server = ""
proxies = {
  "http": proxy_server,
  "https": proxy_server,
}


class deBridge(Account):
    def __init__(self, id, private_key, proxy, rpc):
        super().__init__(id=id, private_key=private_key, proxy=proxy, rpc=rpc)
        self.session = Session()
        self.session.headers['user-agent'] = random_ua()
        self.proxy = proxy
        if self.proxy != None:
            self.session.proxies.update({'http': self.proxy, 'https': self.proxy})
        else:
            logger.warning('You are not using proxy')



    @retry
    def create_and_send_tx(self):
            global send_list
            balance_eth, balance_wei = self.get_value()
            balance_wei_without_fee = balance_wei - 1200000000000000

            dstChainName = random.choice(network_list)
            while dstChainName == self.ChainName:
                dstChainName = random.choice(network_list)

            dstChainId = CHAIN_IDS[dstChainName]

            params = {
                'srcChainId': self.w3.eth.chain_id,
                'srcChainTokenIn': '0x0000000000000000000000000000000000000000',
                'srcChainTokenInAmount': balance_wei_without_fee,
                'dstChainId': dstChainId,
                'dstChainTokenOut': '0x0000000000000000000000000000000000000000',
                'dstChainTokenOutRecipient': self.address,
                'senderAddress': self.address,
                'srcChainOrderAuthorityAddress': self.address,
                'referralCode': referralCode,
                'srcChainRefundAddress': self.address,
                'dstChainOrderAuthorityAddress': self.address,
                'enableEstimate': 'false',
                'prependOperatingExpenses': 'true',
                'additionalTakerRewardBps': '0',
                'deBridgeApp': 'DESWAP',
                'ptp': 'false',
            }

            response = requests.get('https://deswap.debridge.finance/v1.0/dln/order/create-tx', params=params).json()
            # print(json.dumps(response, indent=4))

            data = response['tx']['data']
            value = int(response['tx']['value'])
            to = response['tx']['to']

            userpoints = response['userPoints']
            logger.info(f'Текущее количество поинтов: {userpoints}')

            tx_data = get_tx_data(self, to=to, value=value, data=data)
            logger.info(f'deBridge: Send {"{:0.9f}".format(balance_eth)} ETH from {self.ChainName} to {dstChainName}')
            txstatus, tx_hash = sign_and_send_transaction(self, tx_data)

            if txstatus == 1:
                logger.success(f'deBridge: Send {"{:0.9f}".format(balance_eth)} ETH from {self.ChainName} to {dstChainName} : {self.scan + tx_hash}')
                send_list += (f'\n{SUCCESS}deBridge: Send {"{:0.9f}".format(balance_eth)} ETH from {self.ChainName} to {dstChainName} - [tx hash]({self.scan + tx_hash})')
                self.wait_balance(balance_wei_without_fee, dstChainName)
                self.change_network(dstChainName)
                return dstChainName
            else:
                logger.error(f'deBridge: Send {"{:0.9f}".format(balance_eth)} ETH from {self.ChainName} to {dstChainName} : {self.scan + tx_hash}')
                send_list += (f'\n{FAILED}deBridge: Send {"{:0.9f}".format(balance_eth)} ETH from {self.ChainName} to {dstChainName} - [tx hash]({self.scan + tx_hash})')
                deBridge.create_and_send_tx(self)

    def main(self):
        global send_list
        send_list = ''
        print(self.ChainName)
        counts = random.randint(count_bridge[0], count_bridge[1])
        for i in range(counts):
            dstChainName = deBridge.create_and_send_tx(self)
            sleeping_between_transactions()

        return send_list, dstChainName

class Okex(Account):
    def __init__(self, id, private_key, proxy, rpc):
        super().__init__(id=id, private_key=private_key, proxy=proxy, rpc=rpc)
        self.rpc = rpc

    @retry
    def deposit_to_okex(self, addressokx):
        stay_eth_in_network = round(random.uniform(stay_eth[0], stay_eth[1]), decimal_places)
        value_in_eth = self.get_balance()["balance"] - stay_eth_in_network
        value_in_wei = int(self.w3.to_wei(value_in_eth, "ether"))

        transaction = get_tx_data(self, self.w3.to_checksum_address(addressokx), value=value_in_wei)

        logger.info(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc}...')
        txstatus, tx_hash = sign_and_send_transaction(self, transaction)

        if txstatus == 1:
            logger.success(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc} : {self.scan + tx_hash}')
            return (
                f'\n{SUCCESS}OKx: Deposit {"{:0.4f}".format(value_in_eth)} ETH from {self.rpc} - [tx hash]({self.scan + tx_hash})')
        else:
            logger.error(f'OKx: Deposit {"{:0.9f}".format(value_in_eth)} ETH from {self.rpc} : {self.scan + tx_hash}')
            return (f'\n{FAILED}OKx: Deposit {"{:0.4f}".format(value_in_eth)} ETH from {self.rpc} - failed')

    def withdraw_from_okex(self):

        if transfer_subaccount:
            Okex.transfer_from_subaccount(self)
            print()
        delay = [3, 5]
        amount_to_withdrawal = round(random.uniform(amount[0], amount[1]), decimal_places)
        Okex.okx_withdraw(self, self.address, amount_to_withdrawal, 1)
        # Okex.choose_cex(self.address, amount_to_withdrawal, 1)
        time.sleep(random.randint(delay[0], delay[1]))
        self.wait_balance(int(self.w3.to_wei(amount_to_withdrawal, 'ether') * 0.8), rpc=self.rpc)
        sleeping_between_transactions()
        return (f'\n{SUCCESS}OKx: Withdraw {"{:0.4f}".format(amount_to_withdrawal)} ETH')

    def transfer_from_subaccount(self):
        exchange = ccxt.okx({
            'apiKey': API.okx_apikey,
            'secret': API.okx_apisecret,
            'password': API.okx_passphrase,
            'enableRateLimit': True,
            'proxies': proxies,
        })

        list_sub = exchange.private_get_users_subaccount_list()
        for sub_data in list_sub['data']:
            name_sub = sub_data['subAcct']
            balance = exchange.private_get_asset_subaccount_balances({'subAcct': name_sub, 'ccy': symbolWithdraw})
            sub_balance = balance['data'][0]['bal']
            logger.info(f'OKx: {name_sub} balance : {sub_balance} {symbolWithdraw}')
            if float(sub_balance) > 0:
                transfer = exchange.private_post_asset_transfer(
                    {"ccy": symbolWithdraw, "amt": str(sub_balance), "from": '6', "to": '6', "type": "2",
                     "subAcct": name_sub})
                logger.success(f'OKx: transfer to main {sub_balance} {symbolWithdraw}')
            else:
                continue
        time.sleep(15)
        return True

    def okx_withdraw(self, address, amount_to_withdrawal, wallet_number):
        exchange = ccxt.okx({
            'apiKey': API.okx_apikey,
            'secret': API.okx_apisecret,
            'password': API.okx_passphrase,
            'enableRateLimit': True,
            'proxies': proxies,
        })

        try:
            chainName = symbolWithdraw + "-" + self.ChainName
            fee = Okex.get_withdrawal_fee(symbolWithdraw, chainName)
            exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
                              params={
                                  "toAddress": address,
                                  "chainName": chainName,
                                  "dest": 4,
                                  "fee": fee,
                                  "pwd": '-',
                                  "amt": amount_to_withdrawal,
                                  "network": self.ChainName
                              }
                              )
            logger.success(f'OKx: Вывел {amount_to_withdrawal} {symbolWithdraw}')
            return amount_to_withdrawal
        except Exception as error:
            logger.error(f'OKx: Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error}')

    def get_withdrawal_fee(symbolWithdraw, chainName):
        exchange = ccxt.okx({
            'apiKey': API.okx_apikey,
            'secret': API.okx_apisecret,
            'password': API.okx_passphrase,
            'enableRateLimit': True,
            'proxies': proxies,
        })
        currencies = exchange.fetch_currencies()
        if chainName == 'Arbitrum':
            chainName = 'Arbitrum One'

        for currency in currencies:
            if currency == symbolWithdraw:
                currency_info = currencies[currency]
                network_info = currency_info.get('networks', None)
                if network_info:
                    for network in network_info:
                        network_data = network_info[network]
                        network_id = network_data['id']
                        if network_id == chainName:
                            withdrawal_fee = currency_info['networks'][network]['fee']
                            if withdrawal_fee == 0:
                                return 0
                            else:
                                return withdrawal_fee
        raise ValueError(f"не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")




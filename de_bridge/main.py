import time

from loguru import logger
import random

from help import Account, send_message, sleeping_between_wallets, intro, outro
from settings import bot_status, shuffle, bot_id, bot_token, rotes_modules, network_list
from module import Okex, deBridge




def main():
    with open('proxies.txt', 'r') as file:  # login:password@ip:port в файл proxy.txt
        proxies = [row.strip() for row in file]
    with open('wallets.txt', 'r') as file:
        wallets = [row.strip() for row in file]
    send_list = []
    intro(wallets)
    count_wallets = len(wallets)

    if len(proxies) == 0:
        proxies = [None] * len(wallets)
    if len(proxies) != len(wallets):
        logger.error('Proxies count doesn\'t match wallets count. Add proxies or leave proxies file empty')
        return

    data = [(wallets[i], proxies[i]) for i in range(len(wallets))]
    dstChainName = ''
    if shuffle:
        random.shuffle(data)

    for idx, (wallet, proxy) in enumerate(data, start=1):
        if ':' in wallet:
            private_key, addressokx = wallet.split(':')[0], wallet.split(':')[1]
        else:
            private_key = wallet
            addressokx = None
        from_network = random.choice(network_list)
        account = Account(idx, private_key, proxy, from_network)
        print(f'{idx}/{count_wallets} : {account.address}\n')
        send_list.append(f'{account.id}/{count_wallets} : [{account.address}]({"https://debank.com/profile/" + account.address})')

        try:

            for module in rotes_modules:
                if module[0] == 'Okex_withdrawal':
                    send_list.append(Okex(id=account.id, private_key=account.private_key, proxy=account.proxy, rpc=from_network).withdraw_from_okex())
                elif module[0] == 'Okex_deposit':
                    if addressokx != None:
                        send_list.append(Okex(account.id, account.private_key, account.proxy, dstChainName).deposit_to_okex(addressokx))
                    else:
                        logger.info(f'Не найден адрес депозита...')
                else:
                    send_listt, dstChainName = globals()[module[0]](id=account.id, private_key=account.private_key, proxy=account.proxy, rpc=from_network).main()
                    send_list.append(send_listt)

        except Exception as e:
            logger.error(f'{idx}/{count_wallets} Failed: {str(e)}')
            sleeping_between_wallets()

        if bot_status == True:
            if account.id == count_wallets:
                send_list.append(f'\nSubscribe: https://t.me/CryptoMindYep')
            send_message(bot_token, bot_id, send_list)
            send_list.clear()

        if idx != count_wallets:
            sleeping_between_wallets()
            print()


    outro()
main()
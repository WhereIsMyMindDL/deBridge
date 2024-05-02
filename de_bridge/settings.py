
# ===================================== options ===================================== #

#------main-options------#
shuffle = True                                                      # True / False. если нужно перемешать кошельки
decimal_places = 7                                                  # количество знаков, после запятой для генерации случайных чисел
value_eth = ['93', '97']                                            # минимальное и максимальное кол-во ETH для свапов и ликвы, в ковычках ("90") можно указать процент
delay_wallets = [20, 50]                                            # минимальная и максимальная задержка между кошельками
delay_transactions = [3, 4]                                         # минимальная и максимальная задержка между транзакциями
RETRY_COUNT = 2                                                     # кол-во попыток при возникновении ошибок

#----deBridge-options----#
count_bridge = [3, 4]                                               # количество бриджей
network_list = ['Base', 'Arbitrum', 'Optimism', 'Linea']            # используемые сети для всех модулей: Base | Arbitrum | Optimism | Linea | Ethereum
stay_eth = [0.000067, 0.000071]                                     # сколько оставлять эфира в сети перед депозитом на биржу (учитывайте комиссию), Okex_deposit
referralCode = 21389                                                # рефкод

#------okex-options------#
symbolWithdraw = "ETH"                                              # символ токена, не менять, нахуя вам другой токен
amount = [0.019, 0.020]                                             # минимальная и максимальная сумма на вывод
transfer_subaccount = True                                          # перевод эфира с суббакков на мейн, используется в Okex_withdrawal

class API:
    # okx API
    okx_apikey = ""
    okx_apisecret = ""
    okx_passphrase = ""

#------bot-options------#
bot_status = False                                                  # True / False
bot_token  = ''                                                     # telegram bot token
bot_id     = 0                                                      # telegram id

''' Modules: Okex_withdrawal, deBridge, Okex_deposit '''

rotes_modules = [
            ['Okex_withdrawal'],
            ['deBridge'],
            ['Okex_deposit'],
]

# =================================== end-options =================================== #



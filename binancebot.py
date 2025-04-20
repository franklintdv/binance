import math
import telebot
from datetime import datetime
from binance.client import Client
from math import ceil, floor

# Inicializando o cliente da biblioteca python-binance
api_key = ''
api_secret = ''
client = Client(api_key, api_secret)

# Insira os dados necessários para rodar o bot do Telegram
token = ""
chat_id = 
bot = telebot.TeleBot(token)

Print('Robô iniciado!')

try:
    #BTCBRL
    #Obtendo o saldo BRL.
    get_quote = client.get_asset_balance(asset='BRL')['free']
    quote_size = round(float(get_quote), 8)
    #Obtendo o saldo BTC.
    get_base = client.get_asset_balance(asset='BTC')['free']
    base_size = round(float(get_base), 8)
    # Obtendo o preço atual do BTC/BRL
    ticker = client.get_ticker(symbol="BTCBRL")
    preco = float(ticker['lastPrice'])
    # Obtendo o preço médio de compra.
    with open("preco_medio.txt", 'r') as arquivo:
        preco_medio = arquivo.read()
        preco_medio = float(preco_medio)
    with open("grid_value.txt", 'r') as arquivo:
        grid_value = arquivo.read()
        grid_value = float(grid_value)
    if base_size * preco > quote_size * 1.01 and preco > preco_medio:
        quantidade = float(format(math.ceil(grid_value/preco * 100000) / 100000, '.5f'))
        quantidade = format(quantidade, '.5f')
        ordem = client.order_market_sell(symbol="BTCBRL", quantity=quantidade)
        # Atualizando o valor do grid:
        grid_value = round(grid_value + 0.01, 2)
        with open("grid_value.txt", 'w') as arquivo:
            arquivo.write(str(grid_value))
        # Mensagem do Telegram
        msg = "Venda de " + str(quantidade) + "BTC realizada."
        print(msg)
        bot.send_message(chat_id, msg)
    else:
        # Recuperar o total investido.
        with open("total_invested_btc.txt", 'r') as arquivo:
            total_invested_btc = arquivo.read()
            total_invested_btc = float(total_invested_btc)
        # Recuperar o tamanho da última ordem de compra
        with open("total_qty_btc.txt", 'r') as arquivo:
            total_qty_btc = arquivo.read()
            total_qty_btc = float(total_qty_btc)
        # Calculando a quantidade de BTC para comprar
        quantidade = float(format(math.ceil(grid_value/preco * 100000) / 100000, '.5f'))
        quantidade = format(quantidade, '.5f')
        # Executando a ordem de compra
        ordem = client.order_market_buy(symbol="BTCBRL", quantity=quantidade)
        quantidade = float(quantidade)
        total_invested_btc = round(total_invested_btc + (preco * quantidade), 8)
        with open("total_invested_btc.txt", 'w') as arquivo:
            arquivo.write(str(total_invested_btc))
        total_qty_btc = round(total_qty_btc + quantidade, 8)
        with open("total_qty_btc.txt", 'w') as arquivo:
            arquivo.write(str(total_qty_btc))
        preco_medio = round(total_invested_btc / total_qty_btc, 0)
        with open("preco_medio.txt", 'w') as arquivo:
            arquivo.write(str(preco_medio))
        # Atualizando o valor do grid:
        grid_value = round(grid_value + 0.01, 2)
        with open("grid_value.txt", 'w') as arquivo:
            arquivo.write(str(grid_value))
        # Mensagem do Telegram
        quantidade = format(quantidade, '.5f')
        msg = "Compra diária de " + str(quantidade) + "BTC realizada." + "\n" + "Preço Médio " + str(preco_medio)
        print(msg)
        bot.send_message(chat_id, msg)

except Exception as e:
    print(f"Erro: {e}")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    msg = "Erro, na compra DCA do dia."
    print(msg)
    bot.send_message(chat_id, msg)

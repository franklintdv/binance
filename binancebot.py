import time
import math
import telebot
import csv
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

# Função para verificar se a última operação foi uma compra ou venda.
def is_last_trade_sell(par):
    trades = client.get_my_trades(symbol=par, limit=1)
    if trades:
        return trades[0]['isBuyer'] == False
    return False

print('Robô iniciado!')

# BTCBRL
# Intervalo de Grids do part BTCBRL.
with open('custom_intervals.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    custom_intervals = [float(row[0]) for row in reader]

# Recuperar último preço da ordem de compra:
with open("last_buy_price_btc.txt", 'r') as arquivo:
    last_buy_price_btc = arquivo.read()
    last_buy_price_btc = float(last_buy_price_btc)

# Recuperar último preço da ordem de venda:
with open("last_sell_price_btc.txt", 'r') as arquivo:
    last_sell_price_btc = arquivo.read()
    last_sell_price_btc = float(last_sell_price_btc)

# Recuperar último quantidade de compra.
with open("last_qty_btc.txt", 'r') as arquivo:
    last_qty_btc = arquivo.read()
    last_qty_btc = float(last_qty_btc)

# Recuperar o total investido.
with open("total_invested_btc.txt", 'r') as arquivo:
    total_invested_btc = arquivo.read()
    total_invested_btc = float(total_invested_btc)

# Recuperar o tamanho da última ordem de compra
with open("total_qty_btc.txt", 'r') as arquivo:
    total_qty_btc = arquivo.read()
    total_qty_btc = float(total_qty_btc)

# Recuperar preco medio compra
with open("preco_medio_btc.txt", 'r') as arquivo:
    preco_medio_btc = arquivo.read()
    preco_medio_btc = float(preco_medio_btc)

with open("grid_value.txt", 'r') as arquivo:
    grid_value = arquivo.read()
    grid_value = float(grid_value)

# Variável para armazenar a data da última compra DCA
ultima_compra = None

# Inicar grids
while True:
    try:
        # BTCBRL
        symbol = 'BTCBRL'
        base =  'BTC'
        quote = 'BRL'
        # Verifica a quantidade de ordens abertas
        open_orders = client.get_open_orders(symbol=symbol)
        if len(open_orders) < 2:
        # Cancela ordens abertas
            for order in open_orders:
                client.cancel_order(symbol=symbol, orderId=order['orderId'])
            # Obtém saldo em caixa e saldo emprestado.
            get_quote = client.get_asset_balance(asset=quote)['free']
            quote_size = round(float(get_quote), 8)
            get_base = client.get_asset_balance(asset=base)['free']
            base_size = round(float(get_base), 8)
            if quote_size >= grid_value * 2:
                # Verifica o benchmark e se a última ordem foi de compra ou venda:
                if is_last_trade_sell('BTCBRL'):
                    last_trade_price = last_sell_price_btc
                    grid_value = round(grid_value + 0.01, 2)
                    with open("grid_value.txt", 'w') as arquivo:
                        arquivo.write(str(grid_value))
                else:
                    last_trade_price = last_buy_price_btc
                    total_invested_btc = total_invested_btc + (last_buy_price_btc * last_qty_btc)
                    with open("total_invested_btc.txt", 'w') as arquivo:
                        arquivo.write(str(total_invested_btc))
                    total_qty_btc = total_qty_btc + last_qty_btc
                    with open("total_qty_btc.txt", 'w') as arquivo:
                        arquivo.write(str(total_qty_btc))
                    preco_medio_btc = round(total_invested_btc / total_qty_btc, 2)
                    with open("preco_medio_btc.txt", 'w') as arquivo:
                        arquivo.write(str(preco_medio_btc))
                # Obtém o preço da operação de venda
                higher_prices = [p for p in custom_intervals if p > last_trade_price]
                sell_price = min(higher_prices) if higher_prices else None
                sell_price = float(sell_price)
                last_sell_price_btc = sell_price
                if sell_price < preco_medio_btc:
                    higher_prices = [p for p in custom_intervals if p > preco_medio_btc]
                    sell_price = min(higher_prices) if higher_prices else None
                    sell_price = float(sell_price)
                # Calcular o tamanho do grid
                grid_size = float(format(math.ceil(grid_value/sell_price * 100000) / 100000, '.5f'))
                # Define a quantidade da operação
                sell_quantity = format(grid_size, '.5f')
                with open("last_sell_price_btc.txt", 'w') as arquivo:
                    arquivo.write(str(last_sell_price_btc))
                # Colocar ordem de venda no book se o saldo estiver em ordem.
                try:
                    sell_order = client.order_limit_sell(symbol=symbol, quantity=sell_quantity, price=sell_price)
                except:
                    msg = "Erro ao colocar ordem de venda."
                    print(msg)
                    bot.send_message(chat_id, msg)
                # Calcular o preço de compra
                lower_prices = [p for p in custom_intervals if p < last_trade_price]
                buy_price = max(lower_prices) if lower_prices else None
                buy_price = float(buy_price)
                last_buy_price_btc = buy_price
                # Calcular o tamanho do grid
                grid_size = float(format(math.ceil(grid_value/buy_price * 100000) / 100000, '.5f'))
                # Definir quantidade da compra
                buy_quantity = format(grid_size, '.5f')
                with open("last_qty_btc.txt", 'w') as arquivo:
                    arquivo.write(str(buy_quantity))
                with open("last_buy_price_btc.txt", 'w') as arquivo:
                    arquivo.write(str(last_buy_price_btc))
                # Colocar ordem de compra no book se o saldo estiver em ordem.
                try:
                    buy_order = client.order_limit_buy(symbol=symbol, quantity=buy_quantity, price=buy_price)
                except:
                    msg = "Erro ao colocar ordem de compra."
                    print(msg)
                    bot.send_message(chat_id, msg)
                # Mensagem do Telegram
                msg = "Saldo atual " + str(get_quote) + quote + "\n" + "Saldo atual " + str(get_base) + base + "\n" + "Valor do Grid " + str(grid_value) + "\n" + "Compra em " + str(buy_price) + "\n" + "Venda em " + str(sell_price) + "\n" + "Preço Médio " + str(preco_medio_btc)
                print(msg)
                bot.send_message(chat_id, msg)
                time.sleep(60)
            else:
                # Mensagem do Telegram
                msg = "Saldo insuficiente para continuar com o grid."
                print(msg)
                bot.send_message(chat_id, msg)
                time.sleep(3600)
        else:
            time.sleep(60)

    except Exception as e:
            print(f"Erro: {e}")
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(current_time)
            msg = "Erro, verifique se está tudo ok com o par " + symbol
            print(msg)
            bot.send_message(chat_id, msg)
            time.sleep(60)

    try:
        agora = datetime.now()
        hoje = agora.date()
        if ultima_compra != hoje:
            get_quote = client.get_asset_balance(asset='BRL')['free']
            quote_size = round(float(get_quote), 8)
            if quote_size >= grid_value * 100:
                # Obtendo o preço atual do BTC/BRL
                ticker = client.get_ticker(symbol="BTCBRL")
                preco_btc = float(ticker['lastPrice'])
                # Calculando a quantidade de BTC a comprar
                quantidade_btc = float(format(math.ceil(10/preco_btc * 100000) / 100000, '.5f'))
                quantidade_btc = format(quantidade_btc, '.5f')
                # Executando a ordem de compra
                ordem = client.order_market_buy(symbol="BTCBRL", quantity=quantidade_btc)
                # Atualizando a data da última compra
                ultima_compra = hoje
                total_invested_btc = total_invested_btc + (preco_btc * float(quantidade_btc))
                with open("total_invested_btc.txt", 'w') as arquivo:
                    arquivo.write(str(total_invested_btc))
                total_qty_btc = total_qty_btc + float(quantidade_btc)
                with open("total_qty_btc.txt", 'w') as arquivo:
                    arquivo.write(str(total_qty_btc))
                preco_medio_btc = round(total_invested_btc / total_qty_btc, 2)
                with open("preco_medio_btc.txt", 'w') as arquivo:
                    arquivo.write(str(preco_medio_btc))
                # Mensagem do Telegram
                msg = "Compra diária de " + str(quantidade_btc) + "BTC" + "\n" +  "Preço Médio " + str(preco_medio_btc)
                print(msg)
                bot.send_message(chat_id, msg)
                time.sleep(60)
            else:
                ultima_compra = hoje
                # Mensagem do Telegram
                msg = "Saldo insuficiente para realizar a compra diária."
                print(msg)
                bot.send_message(chat_id, msg)
                time.sleep(60)


    except Exception as e:
            print(f"Erro: {e}")
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(current_time)
            msg = "Erro, na compra DCA do par BTC/BRL."
            print(msg)
            bot.send_message(chat_id, msg)
            time.sleep(60)

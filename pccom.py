import json
import datetime
import time
import requests
import schedule

start_time = time.time()
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}
base_url = 'https://www.pccomponentes.com/ajax_nc/articles/price_and_availability?idArticle='
card_url = 'https://www.pccomponentes.com/cart/addItem/'
time = time

with open("items.json") as items:
    items = json.load(items)
num_items = len(items["items"])


def get_items():
    # Get list of urls from file:
    for i in range(num_items):
        scanstock(items["items"][i]["id"], items["items"][i]["stock"], items["items"][i]["nombre"], i)
        time.sleep(1)

    # TIEMPO EN FUNCIONAMIENTO
    elapsed_time = int(time.time() - start_time)
    elapsed_time = str(datetime.timedelta(seconds=elapsed_time))
    print(elapsed_time + " en funcionamiento")


def scanstock(item_id, localStock, nombre, i):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    try:
        response = requests.get(base_url + item_id, headers=headers)
    except requests.HTTPError:
        print("[------------ Error de conexión ------------]")
        return

    response = response.json()
    webStock = int(response["availability"]["realStock"])
    precio = response["priceIntegerPart"]

    if webStock > 0:
        print("hay stock de " + nombre)
        if localStock == 0:
            items["items"][i]["stock"] = 1
            if int(precio) < 850:
                print('[' + current_time + "] COMPRA!!!: " + nombre + " | " + precio + "€")
                telegram_bot_sendtext(
                    nombre
                    + "\n"
                    + "Precio: " + precio + "€     |    AÑADE AL CARRO!!!"
                    + "\n"
                    + card_url + item_id
                )
            else:
                print('[' + current_time + "] Precio excesivo de: " + nombre + " | " + precio + "€")
        else:
            print("Hay stock pero no enviamos mensaje: " + nombre + " | " + precio + "€")
    else:
        print('[' + current_time + "] No hay stock de: " + nombre + " | " + precio + "€")
        items["items"][i]["stock"] = 0
    print("Actualizo items.json ][", end=" ")
    with open('items.json', 'w') as outfile:
        json.dump(items, outfile, indent=1)
        outfile.close()
    print("items.json Actualizado ][", end=" ")


def telegram_bot_sendtext(bot_message):
    ## REEMPLAZAR CON LOS DATOS NECESARIOS ##
    bot_token = 'YOUR_TELEGRAM_TOKEN'
    bot_chatID = 'YOUR_TELEGRAM_CHAT_ID'
    #########################################

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


get_items()
schedule.every(2).seconds.do(get_items)

while True:
    schedule.run_pending()
    time.sleep(5)

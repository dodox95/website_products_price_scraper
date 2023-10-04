def clear_file_contents(file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        pass

clear_file_contents('my_products.csv')
clear_file_contents('comparison.csv')
clear_file_contents('products.csv')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from decouple import config

import csv
import time
from woocommerce import API
import json

wcapi = API(
    url=config('WOOCOMMERCE_URL'),
    consumer_key=config('WOOCOMMERCE_CONSUMER_KEY'),
    consumer_secret=config('WOOCOMMERCE_CONSUMER_SECRET'),
    wp_api=True,
    version="wc/v3",
    query_string_auth=True,
    timeout=15
)


def login(driver):
    # przejście do strony logowania
    driver.get(config('GERMANIAMINT_LOGIN_URL'))
    
    # znalezienie pól do wpisania loginu i hasła oraz przycisku "Zaloguj"
    login_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email")))
    password_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "passwd")))
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "SubmitLogin")))

    # wpisanie loginu i hasła
    login_field.send_keys(config('GERMANIAMINT_LOGIN_EMAIL'))
    password_field.send_keys(config('GERMANIAMINT_LOGIN_PASSWORD'))

    # kliknięcie przycisku "Zaloguj"
    driver.execute_script("arguments[0].click();", login_button)

def save_new_products(germania_products_data, my_products_data):
    new_products = []

    for germania_product in germania_products_data:
        found = False
        for my_product in my_products_data:
            if germania_product['name'] == my_product['name']:
                found = True
                break

        if not found and germania_product['name'].strip():
            new_products.append(germania_product)

    write_product_data_to_csv(new_products, 'new_products.csv')
    return new_products



def get_product_data(driver):
    # przekierowanie do strony z listą produktów
    driver.get(config('GERMANIAMINT_LOGIN_URL'))
    # poczekanie na załadowanie tabeli z produktami
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "prices-table")))

    # pobranie wszystkich wierszy tabeli z produktami
    product_rows = driver.find_elements(By.XPATH, '//table[@class="prices-table"]/tbody/tr')

    products = []

    scrap_gold_products = False
    for row in product_rows:
        if '<h3>ZŁOTO</h3>' in row.get_attribute('outerHTML'):
            scrap_gold_products = True
        elif '<h3>PLATYNA I PALLAD</h3>' in row.get_attribute('outerHTML'):
            scrap_gold_products = False
        elif scrap_gold_products and 'data-manufacturer-id' in row.get_attribute('outerHTML'):
            # pobranie nazwy produktu, ceny i stanu magazynowego
            name = row.find_element(By.CLASS_NAME, 'name').text
            price = row.find_element(By.CLASS_NAME, 'price').text
            stock = row.find_element(By.CLASS_NAME, 'stock').text

            # usunięcie jednostki "zł" i spacji z ceny
            price = price.replace(" zł", "").replace(" ", "")

            # usunięcie "amp;" z nazwy produktu
            name = name.replace("&amp;", "&")

            # sprawdzenie, czy wartość ceny nie jest pusta
            if price.strip():
                # dodanie 5% marży do ceny
                price_float = float(price.replace(',', '.'))  # konwersja tekstu na liczbę zmiennoprzecinkową
                price_with_margin = price_float * 1.05  # dodanie 5% marży
                price_with_margin_str = f"{price_with_margin:.2f}"  # konwersja liczby zmiennoprzecinkowej na tekst bez jednostki "zł"
            else:
                price_with_margin_str = ""

            products.append({'name': name, 'price': price_with_margin_str, 'stock': stock})

    return products




# Dodaj kod funkcji add_new_products_to_woocommerce:
"""def add_new_products_to_woocommerce(germania_products_data, my_products_data):
    next_sku = 223  # Ustawienie początkowego SKU dla nowych produktów
    new_products_added = 0

    for germania_product in germania_products_data:
        found = False
        for my_product in my_products_data:
            if germania_product['name'] == my_product['name']:
                found = True
                break

        if not found and germania_product['name'].strip():
            new_product_data = {
                "name": germania_product['name'],
                "sku": str(next_sku),
                "regular_price": germania_product['price'],
                "stock_quantity": germania_product['stock'],
                "status": "publish",
                "manage_stock": True  # Włącz zarządzanie stanem magazynowym
            }

            try:
                wcapi.post("products", new_product_data).json()
                new_products_added += 1
                next_sku += 1
            except Exception as e:
                print(f"Błąd podczas dodawania nowego produktu {germania_product['name']}: {e}")

    if new_products_added > 0:
        print(f"Dodano {new_products_added} nowych produktów.")
    else:
        print("Nie znaleziono nowych produktów do dodania.")"""



def get_my_products_data():
    products = []
    page = 1
    while True:
        try:
            response = wcapi.get("products", params={'per_page': 100, 'page': page}).json()
        except Exception as e:
            print(f"Błąd podczas pobierania produktów z WooCommerce: {e}")
            break

        if response:  # jeśli odpowiedź nie jest pusta
            for product in response:
                sku = product["sku"]
                name = product["name"]
                price = product["regular_price"]
                stock = product["stock_quantity"]

                # usunięcie "amp;" z nazwy produktu
                name = name.replace("&amp;", "&")

                products.append({'sku': sku, 'name': name, 'price': price, 'stock': stock})
            page += 1
        else:
            break

    return products



def write_product_data_to_csv(products_data, file_name):
    # Wyczyść plik CSV przed zapisem nowych danych
    with open(file_name, 'w', encoding='utf-8') as csv_file:
        pass

    # Zapisz nowe dane do pliku CSV
    with open(file_name, 'a', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['sku', 'name', 'price', 'stock']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='|', quoting=csv.QUOTE_NONE, quotechar="", escapechar="")

        writer.writeheader()
        for product_data in products_data:
            writer.writerow(product_data)



def compare_products(my_products_data, germania_products_data):
    comparison_data = []
    for germania_product in germania_products_data:
        for my_product in my_products_data:
            if germania_product['name'] == my_product['name']:
                comparison_data.append({
                    'sku': my_product['sku'],
                    'name': my_product['name'],
                    'price': germania_product['price'],
                    'stock': germania_product['stock']
                })
    return comparison_data


# zaktualizuj produkty w WooCommerce
def update_woocommerce_products(products_data):
    updated_products = 0
    for product_data in products_data:
        try:
            # Wyszukaj produkt w WooCommerce po SKU
            search_results = wcapi.get(f"products?sku={product_data['sku']}").json()

            if search_results:  # jeśli produkt został znaleziony
                product = search_results[0]  # przyjmujemy, że pierwszy wynik wyszukiwania to szukany produkt
                product_id = product["id"]

                # Aktualizacja ceny i stanu magazynowego produktu
                wcapi.put(f"products/{product_id}", {
                    "regular_price": product_data["price"],
                    "stock_quantity": product_data["stock"]
                }).json()
                updated_products += 1

            else:
                print(f"Produkt {product_data['name']} nie został znaleziony w sklepie WooCommerce.")
        except Exception as e:
            print(f"Błąd podczas aktualizacji produktu {product_data['name']}: {e}")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Ceny zaktualizowane! Zaktualizowano {updated_products} produktów. Czas aktualizacji: {current_time}")

#last_new_product_addition_time = time.time()

def disable_unlisted_products_in_woocommerce(germania_products_data, my_products_data):
    disabled_products = 0
    for my_product in my_products_data:
        found = False
        for germania_product in germania_products_data:
            if my_product['name'] == germania_product['name']:
                found = True
                break

        if not found:
            try:
                search_results = wcapi.get(f"products?sku={my_product['sku']}").json()

                if search_results:
                    product = search_results[0]
                    product_id = product["id"]

                    wcapi.put(f"products/{product_id}", {
                        "stock_quantity": 0  # Ustaw stan magazynowy na 0
                    }).json()
                    disabled_products += 1
                else:
                    print(f"Produkt {my_product['name']} nie został znaleziony w sklepie WooCommerce.")
            except Exception as e:
                print(f"Błąd podczas aktualizacji stanu magazynowego produktu {my_product['name']}: {e}")

    print(f"Zaktualizowano stan magazynowy produktów. Wyłączono {disabled_products} produktów.")

#last_new_product_addition_time = time.time()


while True:
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)

    login(driver)

    try:
        # poczekanie na załadowanie strony po zalogowaniu
        WebDriverWait(driver, 10).until(EC.url_changes("https://b2b.germaniamint.com/pl/logowanie"))

    except TimeoutException:
        print("TimeoutException: Nie udało się zalogować.")
        driver.quit()
        time.sleep(60)  # odczekaj 1 minutę przed ponowną próbą
        continue

    germania_products_data = get_product_data(driver)
    write_product_data_to_csv(germania_products_data, 'products.csv')

    my_products_data = get_my_products_data()
    write_product_data_to_csv(my_products_data, 'my_products.csv')

    """current_time = time.time()
    if current_time - last_new_product_addition_time > 604800:  # 604800 sekund to 7 dni
        add_new_products_to_woocommerce(germania_products_data, my_products_data)
        print("Zapisałem nowe produkty!")
        last_new_product_addition_time = current_time
        print("Zapisałem nowe produkty!")"""


    # zamknięcie przeglądarki
    driver.quit()

    print("Pobrano informacje o produktach i zapisano do pliku 'products.csv' oraz 'my_products.csv'")

    comparison_data = compare_products(my_products_data, germania_products_data)
    write_product_data_to_csv(comparison_data, 'comparison.csv')

    print("Porównano produkty i zapisano do pliku 'comparison.csv'")

    new_products = save_new_products(germania_products_data, my_products_data)
    if new_products:
        print("Nowe produkty:")
        for new_product in new_products:
            print(f"{new_product['name']} - Cena: {new_product['price']} - Stan magazynowy: {new_product['stock']}")

    disable_unlisted_products_in_woocommerce(germania_products_data, my_products_data)

    # zaktualizuj produkty w WooCommerce
    update_woocommerce_products(comparison_data)

     # Wyłącz produkty nieobecne w "comparison.csv"

    # Odczekaj określony czas przed ponownym uruchomieniem skryptu
    time.sleep(300)  # odczekaj 1 godzinę (3600 sekund) przed ponownym uruchomieniem
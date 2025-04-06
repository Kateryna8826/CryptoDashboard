import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Функція отримання історичних даних з  CoinGecko
def get_historical_data(coin_id, currency="usd", days=90, max_retries=3):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": currency, "days": days, "interval": "daily"}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                prices = data["prices"]
                df = pd.DataFrame(prices, columns=["timestamp", "price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
            elif response.status_code == 429:
                print(f"Помилка 429 для {coin_id}, спроба {attempt + 1}/{max_retries}. Чекаємо 10 секунд...")
                time.sleep(10)
            else:
                print(f"Помилка при отриманні даних для {coin_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Виняток при отриманні даних для {coin_id}: {e}")
            return None

    print(f"Не вдалося отримати дані для {coin_id} після {max_retries} спроб.")
    return None

# Список криптовалют
coins = ["bitcoin", "ethereum", "litecoin", "stacks", "binancecoin", "solana", "maker"]

# Словник для збереження даних
results = []
data_dict = {}

# Розрахунки для кожної валюти
for coin in coins:
    print(f"Запит даних для {coin}...")
    df = get_historical_data(coin, days=90)
    if df is not None:
        # Щоденні зміни цін
        df["returns"] = df["price"].pct_change()

        # Динамічна волатильність (інтервал в 14 діб)
        df["volatility"] = df["returns"].rolling(window=14).std() * np.sqrt(365) * 100

        # Динамічна доходність за 14 днів
        df["rolling_profitability"] = (df["price"] / df["price"].shift(13) - 1) * 100

        # Волатильність за весь період (річна)
        volatility = df["returns"].std() * np.sqrt(365) * 100

        # Доходність за весь період (90 діб)
        initial_price = df["price"].iloc[0]
        final_price = df["price"].iloc[-1]
        profitability = ((final_price - initial_price) / initial_price) * 100

        # Додаємо результати для зведеної таблиці
        results.append({
            "Криптовалюта": coin.capitalize(),
            "Волатильність (річна), %": round(volatility, 2),
            "Доходність за 90 днів, %": round(profitability, 2)
        })

        # Збереження індивідуального CSV
        filename = f"{coin}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Дані для {coin} збережені в {filename}")

        # Зберігаємо дані для графіка
        data_dict[coin] = df

    # Затримка 10 секунд між запитами
    time.sleep(10)

# Збереження всіх результатів в один CSV
if results:
    df_results = pd.DataFrame(results)
    summary_filename = f"crypto_summary_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv"
    df_results.to_csv(summary_filename, index=False)
    print(f"Усі результати збережені в {summary_filename}")

    # Виведення результатів у консоль
    print("\nРезультати за 90 днів:")
    print(df_results.to_string(index=False))

# Графік волатильності (використовуємо збережені дані)
plt.figure(figsize=(12, 6))
for coin in coins:
    if coin in data_dict:
        df = data_dict[coin]
        plt.plot(df["timestamp"], df["volatility"], label=coin.capitalize())

plt.title("Historical Volatility of Cryptocurrencies (Rolling 14-day)")
plt.xlabel("Date")
plt.ylabel("Volatility (Annualized, %)")
plt.legend()
plt.grid(True)
plt.show()
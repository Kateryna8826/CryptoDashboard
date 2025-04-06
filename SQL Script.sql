#Очищення даних від викидів
# Знайдемо середнє значення та стандартне відхилення в стовпці OpenPrice
SET @mean = (SELECT AVG(OpenPrice) FROM maker);
SET @stddev = (SELECT STD(OpenPrice) FROM maker);
# Видаляємо викиди
DELETE FROM maker
WHERE ABS((OpenPrice - @mean) / @stddev) > 3;

SET @mean = (SELECT AVG(Max) FROM maker);
SET @stddev = (SELECT STD(Max) FROM maker);

#Створення єдиної таблиці для криптовалют
# Створюємо таблицю

USE crypto;
CREATE TABLE CryptoData1 (
    id SERIAL PRIMARY KEY,
    Date DATE,
    Currency VARCHAR(50),
    Price DECIMAL(18, 6),
    Market_Volume DECIMAL(18, 2),
    Market_Cap DECIMAL(18, 2)
);
# Заповнюємо значеннями

INSERT INTO CryptoData1 (Date, Currency, Price, Market_Volume, Market_Cap)
SELECT Date, 'Bitcoin', Average, Volume, MarketCap FROM bitcoin
UNION ALL
SELECT Date, 'Ethereum', Average, Volume, MarketCap FROM ethereum
UNION ALL
SELECT Date, 'Binancecoin', Average, Volume, MarketCap FROM binancecoin
UNION ALL
SELECT Date, 'Solana', Average, Volume, MarketCap FROM solana
UNION ALL
SELECT Date, 'Maker', Average, Volume, MarketCap FROM maker
UNION ALL
SELECT Date, 'Litecoin', Average, Volume, MarketCap FROM litecoin
UNION ALL
SELECT Date, 'Story_protocol', Average, Volume, MarketCap FROM story_protocol;

#Заповнення порожніх рядків середнім арифметичним 
# Створюємо тимчасову таблицю, де рахуємо середнє значення по стовпцю volatility, ігноруючи пусті рядки
CREATE TEMPORARY TABLE temp_avg  AS
SELECT AVG(OpenPrice) AS avg_OpenPrice
FROM bitcoin
WHERE OpenPrice != ' ' AND volatility IS NOT NULL;

# Оновлюємо основну таблицю

UPDATE bitcoin
SET volatility = (SELECT avg_ OpenPrice FROM temp_avg)
WHERE OpenPrice = ' ';

# Видаляємо тимчасову таблицю
DROP TEMPORARY TABLE temp_avg;

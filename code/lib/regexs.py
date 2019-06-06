import re

r_prices = re.compile(r"(usd|eur|€|\$|£|฿|₵|₡|₫|৳|ƒ|₣|₲|₴|₭|₽|₱|₨|₪|₩|¥|៛)+\s{0,10}(?:\d+(?:[.,\-/]*\d+)*)")
r_prices_after = re.compile(r"\s?(?:\d+(?:[.,\-/]\d+){0,9})(\s{0,10}|-)(usd|eur|cents|cent|€|\$|£|฿|₵|₡|₫|৳|ƒ|₣|₲|₴|₭|₽|₱|₨|₪|₩|¥|៛)+")
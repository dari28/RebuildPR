import re

r_float = r"((?:\d+([\.,'\"]\d*){0,9}|\.\d+)\b)"
r_float_only = r"((?:\d+\.\d+)\b)"
floats_re = re.compile(r_float)
url_re = re.compile(r"(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.][a-z0-9]+)*\.[a-z]{2,5}\b(:[0-9]{1,5})?(\/\S*)?", re.IGNORECASE)
email_re = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
date_re = re.compile("(?:(?:(?:(?:(?<!:)\\b\\'?\\d{1,4},? ?)?\\b(?:[Jj]an(?:uary)?|[Ff]eb(?:ruary)?|[Mm]ar(?:ch)?|[Aa]pr(?:il)?"
                     "|May|[Jj]un(?:e)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ept?(?:ember)?|[Oo]ct(?:ober)?|[Nn]ov(?:ember)?|[Dd]ec(?:ember)?)\\b(?:(?:,? ?\\'?)?"
                     "\\d{1,4}(?:st|nd|rd|n?th)?\\b(?:[,\\/]? ?\\'?\\d{2,4}[a-zA-Z]*)?(?: ?- ?\\d{2,4}[a-zA-Z]*)?(?!:\\d{1,4})\\b))|(?:(?:(?<!:)\\b\\'?"
                     "\\d{1,4},? ?)\\b(?:[Jj]an(?:uary)?|[Ff]eb(?:ruary)?|[Mm]ar(?:ch)?|[Aa]pr(?:il)?|May|[Jj]un(?:e)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ept?"
                     "(?:ember)?|[Oo]ct(?:ober)?|[Nn]ov(?:ember)?|[Dd]ec(?:ember)?)\\b(?:(?:,? ?\\'?)?\\d{1,4}(?:st|nd|rd|n?th)?\\b(?:[,\\/]? ?\\'?\\d{2,4}"
                     "[a-zA-Z]*)?(?: ?- ?\\d{2,4}[a-zA-Z]*)?(?!:\\d{1,4})\\b)?))|(?:\\b(?<!\\d\\.)(?:(?:(?:[0123]?[0-9][\\.\\-\\/])?[0123]?[0-9][\\.\\-\\/]"
                     "[12][0-9]{3})|(?:[0123]?[0-9][\\.\\-\\/][0123]?[0-9][\\.\\-\\/][12]?[0-9]{2,3}))(?!\\.\\d)\\b))")
phone_re = re.compile("(?<![0-9])(?:\\+\\d{1,2}\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}(?![0-9])")
time_re = re.compile("(?:(?:\\d+)?\\.?\\d+(?:AM|PM|am|pm|a\\.m\\.|p\\.m\\.))|(?:(?:[0-2]?[0-9]|[2][0-3]):(?:[0-5][0-9])(?::(?:[0-5][0-9]))?"
                     "(?: ?(?:AM|PM|am|pm|a\\.m\\.|p\\.m\\.))?)")
hashtag_re = re.compile("\\#\\b[\\w\\-\\_]+\\b")
username_re = re.compile("@\\S+")
# r_sym_num = re.compile(r"(\S{1,15}\s*(\"?(?:\d+(?:[.,\-/]*\d+)*)+\"?)|(\"?(?:\d+(?:[.,\-/]*\d+)*)+\"?\W*(?:\d+(?:[.,\-/]*\d+)*)+))")
# r_num_sym = re.compile(r"(?:\d+(?:[.,\-/]*\d+)*)+\S+")
r_around_num = re.compile(r"(\S+\s+(\d+\W?)|(\d+\W?\d+))\s*\S*")

r_dollar = r'(\$|\$usd|usd|dollar(s)?|bucks)'
r_euro = r'(€(€)?|eur(o|os)?)'
r_gbr = r'(£|gbp|pound sterling)'
r_rub = r'(₽|rub(le|les)?)'
r_yen = r'(¥|yen(s)?|jpy)'
r_cents = r'(cent(s)?|¢|¢¢|ct.)'
r_euro_cents = r'(euro cent(s)?)'
r_valuta = r'({0}|{1}|{2}|{3}|{4})'.format(r_dollar, r_euro, r_gbr, r_rub, r_yen)
r_sub_valuta = r'({0}|{1})'.format(r_cents, r_euro_cents)

r_price_sign = r'(usd|eur|€|\$|£|฿|₵|₡|₫|৳|ƒ|₣|₲|₴|₭|₽|₱|₨|₪|₩|¥|៛)'
r_prices = re.compile(r"(usd|eur|€|\$|£|฿|₵|₡|₫|৳|ƒ|₣|₲|₴|₭|₽|₱|₨|₪|₩|¥|៛)+\s{0,10}(?:\d+(?:[.,\-/]*\d+)*)")
r_prices_after = re.compile(r"\s?(?:\d+(?:[.,\-/]\d+){0,9})(\s{0,10}|-)(usd|eur|cents|cent|€|\$|£|฿|₵|₡|₫|৳|ƒ|₣|₲|₴|₭|₽|₱|₨|₪|₩|¥|៛)+")
r_inches = re.compile(r'(?:\d+(?:[.,\-/x]\d+){0,9})\s?["“”″]')
r_feet = re.compile(r"(?:\d+(?:[.,\-/x]\d+){0,9})\s?\'")
r_num_space = re.compile(r"\b(?:\d+(?:[.,\-/x]\d+){0,9})(\s{0,10}|-)([a-z%º°/]{1,15}(\^2|\^3)?)(?=\s|$|\W)")
r_sym_num = re.compile(r"(\b|\.)([a-z%º°/]{1,15}(\^2|\^3)?)\s*(?:\d+(?:[.,\-/]\d+){0,9})(?=\s|$|\W)")
r_fraction = re.compile(r"(^|\s)\d+(\s|and)+\d+/\d+(?=\s|$|\W)")
r_fraction_solo = re.compile(r"(^|\s)\d+/\d+(\s|$)")
r_fraction_sym = re.compile(r"\d+½")
r_interval = re.compile(r"(^|(?<=\s))\d+\s[–-]\s\d+(?=\s|$)")
r_years_contraction = re.compile(r'\b(?:(?:30)|(?:40)|(?:50)|(?:60)|(?:70)|(?:80)|(?:90))\'s\b')
r_years_contraction_0 = re.compile(r'\b(?:00)\'s\b')
r_years_contraction_2 = re.compile(r'\b(?:(?:60)|(?:70)|(?:80)|(?:90))s\b')
r_k = re.compile(r"\d+k")
r_zip_code = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
r_dimensions_wlh = re.compile(r'(\d+(?:[.,\-/x]\d+){0,9})\s?[x✕☓❌×]\s?(\d+(?:[.,\-/x]\d+){0,9})(\s?[x✕☓❌×]\s?[\d,.]+)?(?=\s|$|\W)')
r_dimensions_whd = re.compile(r"(\d+(?:[.,\-/x]\d+){0,9})w?\s?[x✕☓×❌]\s?(\d+(?:[.,\-/x]\d+){0,9})h?\s?[x✕☓×❌]\s?(\d+(?:[.,\-/x]\d+){0,9})d?(?=\s|$|\W)")
r_cloth_sizes = re.compile(r'\bsize (xxl|small|xl|2xl|xs|s|m|large|x-large|xxl|xxxl|x-small|medium|2x-large|2x|3x|4x|xl/1x|xxs|l)\b')
r_cloth_sizes_2 = re.compile(r'\b(mens|men|boys|boy|jacket|womans|woman|ladies|girls|youth) (xxl|small|xl|2xl|xs|s|m|large|x-large|xxl|xxxl|x-small|medium|2x-large|2x|3x|4x|xl/1x|xxs|l)\b')
ones = r'(?:one|two|three|four|five|six|seven|eight|nine)((?!\w)|(?!\D))'
tens = u'(?:(?:t|elev)en|twelve|(?:thir|four|fif|six|seven|eigh|nine)teen)((?!\w)|(?!\D))'
prefix_two_digits = u'(?:(?:twen|thir|for|fif|six|seven|eigh|nine)ty(?!^\w))[ ]*(?:and|-)?[ ]*(?:(?:one|two|three|four|five|six|seven|eight|nine))?'
# nums_hundred = u'(?:{0})|(?:{2}|{1})'.format(prefix_two_digits, ones, tens)  # 99
nums_hundred = u'(?:{0})|(?:{2}|{1}|[1-9][0-9]?)'.format(prefix_two_digits, ones, tens)  # 99
# nums_thousand = u'(?:{0})\s+hundred(?:[ ]+(?:and[ ]+)?(?:{1}))?|{1}'.format(ones, nums_hundred)  # 999
nums_thousand = u'(?:{0})\s+hundred(?:[ ]+(?:and[ ]+)?(?:{1}))?|{1}|[1-9][0-9][0-9]'.format(ones, nums_hundred)  # 999
# nums_million = u'(?:{0})\s+thousand(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_thousand)  # 999,999
nums_million = u'(?:{0})\s+thousand(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}|([1-9][0-9][0-9][0-9][0-9]?[0-9]?)'.format(nums_thousand)  # 999,999
nums_billion = u'(?:{1})\s+million(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}|([1-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]?[0-9]?)'.format(nums_million, nums_thousand)  # 999,999,999
nums_trillion = u'(?:{1})\s+billion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_billion, nums_thousand)  # 999,999,999,999
nums_quadrillion = u'(?:{1})\s+trllion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_trillion, nums_thousand)  # 999,999,999,999,999
nums_quintillion = u'(?:{1})\s+quadrillion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_quadrillion, nums_thousand)  # 999,999,999,999,999,999
nums_sextillion = u'(?:{1})\s+quintillion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_quintillion, nums_thousand)  # 999,999,999,999,999,999,999
nums_septillion = u'(?:{1})\s+sextillion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_sextillion, nums_thousand)  # 999,999,999,999,999,999,999,999
big_num = u'(?:{1})\s+septillion(?:[ ]+(?:and[ ]+)?(?:{0}))?|{0}'.format(nums_septillion, nums_thousand)
big_numbers = u'(?:oh|zero)|{0}'.format(big_num)  # ATTENTION: maybe nead one more check for -- oh, may give not coorrect result
point = u'(?:point|dot)(?:[ ]+(?:(?:one|two|three|four|five|six|seven|eight|nine|zero|oh|nought)(?!\w)))+'
number = r'((\b)|(\d))(?:{0})(?:[ ]+{1})?'.format(big_numbers, point)
ordinal_nums = u'(?: *[-]? *)(?:first|second|third|(?:four|fif|six|seven|eigh|nin|ten|eleven|twelf|(?:thir|four|fif|six|seven|eigh|nine)teen|(' \
               u'?:twent|thirt|fort|fift|sixt|sevent|eight|ninet)ie|hundred|thousand|(?:m|b|tr|quadr|quint|sext|sept)illion)th)(?!\w) '
en_cardinal_numerals = re.compile(number, re.U | re.I)
en_ordinal_numerals = re.compile(ordinal_nums, re.U | re.I)
numbers_re = re.compile('\d+([,./]\d+)*')

r_short_scale = u'(million|billion|milliard|trillion|quadrillion|quintillion|sextillion|septillion)'
r_float_with_word = u'({0}\s{1})'.format(r_float_only, r_short_scale)
valuta_with_num = u'(({0}|{2})\s?{1})|({1}\s?({2}|{0}))'.format(number, r_valuta, r_float_with_word)  # Order sensitive
sub_valuta_with_num = u'(({0}|{2})\s?{1})|({1}\s?({0}|{2}))'.format(nums_hundred, r_sub_valuta, r_float)
# currency_tags = re.compile(u'({0}((\s?and\s|\s)({1})?))|({1})'.format(valuta_with_num, sub_valuta_with_num))
currency_tags = re.compile(u'(({0}(\sand)?(\s{1})?)|({1}))'.format(valuta_with_num, sub_valuta_with_num))
# input_string = 'c 5three0-3six3-2six28 twon one eight mnine montwond'
# numerals = [input_string[match.start(): match.end()] for match in en_cardinal_numerals.finditer(input_string)]
# print(numerals)

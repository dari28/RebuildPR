from lib.regexs import *
from lib import tools
from lib.mongo_connection import MongoConnection
# import nlp.config

# mongo = MongoConnection(config.USE_DB)
mongo = MongoConnection()

ref_units = {}
for unit_ in mongo.units.find({}):
    ref_units[unit_['unit']] = set(unit_['variations'])


def parse_units(text, convert):
    def handle_intervals(interval):
        return interval.split('-')

    def handle_mul(s):
        return s.split('x')

    def handle_fraction(fraction):
        fraction_split = fraction.replace(',', '').split('/')
        try:
            assert len(fraction_split) == 2
        except AssertionError:
            return fraction_split
        try:
            value = float(fraction_split[0].strip()) / float(fraction_split[1].strip())
        except (ZeroDivisionError, ValueError):
            return []
        return [str(value)]

    def handle_value(value):
        values = [value]
        i = 0
        while i < len(values) or i > 100:
            v = values[i]
            if '-' in v:
                values.remove(v)
                values += handle_intervals(v)
                continue
            if 'x' in v:
                values.remove(v)
                values += handle_mul(v)
                continue
            if '/' in v:
                values.remove(v)
                values += handle_fraction(v)
                continue
            i += 1
        return values

    output_text = str(text)
    detected_units = []
    unknown_units = []
    # for match in r_fraction.finditer(output_text):
    #     try:
    #         string = match.string[match.start():match.end()].strip()
    #         split = string.split()
    #         value = int(split[0])
    #         fraction_split = split[1].split('/')
    #         value += int(fraction_split[0]) / int(fraction_split[1])
    #         output_text = output_text.replace(string, str(value))
    #     except:
    #         pass
    # for match in r_fraction_sym.finditer(output_text):
    #     try:
    #         string = match.string[match.start():match.end()].strip()
    #         value = int(tools.extract_numbers(string)) + 0.5
    #         output_text = output_text.replace(string, str(value))
    #     except:
    #         pass
    # for match in r_k.finditer(output_text):
    #     try:
    #         string = match.string[match.start():match.end()].strip()
    #         value = int(string[0:-1]) * 1000
    #         output_text = output_text.replace(string, str(value))
    #     except:
    #         pass
    # for match in r_years_contraction.finditer(output_text):
    #     string = match.string[match.start():match.end()].strip()
    #     output_text = output_text.replace(string, '19' + string)
    # for match in r_years_contraction_0.finditer(output_text):
    #     string = match.string[match.start():match.end()].strip()
    #     output_text = output_text.replace(string, '20' + string)
    # for match in r_years_contraction_2.finditer(output_text):
    #     string = match.string[match.start():match.end()].strip()
    #     output_text = output_text.replace(string, '19' + string)
    # for match in r_interval.finditer(output_text):
    #     string = match.string[match.start():match.end()].strip()
    #     output_text = output_text.replace(string, string.replace(' ', ''))

    search_text = str(output_text)

    for match in en_cardinal_numerals.finditer(search_text):
        string = match.string[match.start():match.end()].strip()
        print(string)

    for match in r_prices.finditer(search_text):
        string = match.string[match.start():match.end()].strip()
        clear_string = tools.remove_digits_and_delimiters(string)
        if clear_string == '':
            continue
        value = string.replace(clear_string, '')
        value = tools.trim_punkt(value).strip()
        for k in ref_units:
            if clear_string in ref_units[k]:
                values = handle_value(value)
                for val in values:
                    detected_units.append({'unit': k, 'val': val})
                search_text = search_text.replace(string, ' . ' + k + ' . ')
                output_text = output_text.replace(string, value + ' ' + k + ' ')
                break
    for match in r_prices_after.finditer(search_text):
        string = match.string[match.start():match.end()].strip()
        clear_string = tools.remove_digits_and_delimiters(string)
        if clear_string == '':
            continue
        value = string.replace(clear_string, '')
        value = tools.trim_punkt(value).strip()
        for k in ref_units:
            if clear_string in ref_units[k]:
                values = handle_value(value)
                for val in values:
                    if k == 'cents' or k == 'cent':
                        try:
                            val = str(float(val) / 100)
                        except:
                            continue
                        k = '$'
                        detected_units.append({'unit': k, 'val': val})
                    else:
                        detected_units.append({'unit': k, 'val': val})
                search_text = search_text.replace(string, ' . ' + k + ' . ')
                output_text = output_text.replace(string, value + ' ' + k)
                break

    # detected_units = tools.units_conversion(detected_units, convert)
    # Add SIDE
    zip_codes = []
    return {'units': detected_units, 'unknown_units': unknown_units, 'zip': zip_codes}, output_text


def parse_currency(text):
    text = str(text)
    tags = dict()
    tags['money'] = []
    for match in currency_tags.finditer(text):
        string = match.string[match.start():match.end()]
        tags['money'].append({'start_match': match.start(), 'length_match': match.end() - match.start(), 'word': string})
    return tags


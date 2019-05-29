# coding=utf-8
import re
import requests
from bs4 import BeautifulSoup
import pycountry

def get_country_names_list():
    country_list = []
    url = requests.get('https://en.wikipedia.org/wiki/List_of_sovereign_states').text
    soup = BeautifulSoup(url, 'lxml')
    my_table = soup.find('table')
    countries = my_table.findAll('td', style="vertical-align:top;")
    for country in countries:
        cntr = dict()
        zzz = country.find('span', style="display:none")
        name = country.get_text().replace(zzz.get_text(), '') if zzz else country.get_text()
        name = name.replace('→', '–').replace('\n', '')
        name = re.sub(r'[[a-z,0-9].]', '', name)
        name = name.replace('[', '')
        common_name = name.split('–')[0].strip()
        official_name = name.split('–')[1].strip() if len(name.split('–')) > 1 else common_name.strip()
        country_code = mongodb.iso3166.find({'$or': [{'name': official_name}, {'name': common_name},
                                                     {'official_name': official_name}, {'official_name': common_name}]})

        cntr['official_name'] = official_name
        cntr['common_name'] = common_name
        cntr['code'] = country_code['alpha_2'] if country_code['alpha_2'] else country_code['alpha_3']
        country_list.append(cntr)
    return country_list


def get_pr_city_list():
    pr_city_list = []
    url = requests.get('https://suburbanstats.org/population/puerto-rico/list-of-counties-and-cities-in-puerto-rico').text
    soup = BeautifulSoup(url, 'lxml')
    pr_city = soup.findAll('a', title=re.compile('Population Demographics and Statistics'))
    for city in pr_city:
        ct = dict()
        ct['country_id'] = '5cdc1484cde53353db41d8cd'
        ct['state_id'] = '5cdcf40dcde5330f034fccc4'
        ct['name'] = city.get_text()

        pr_city_list.append(ct)
    return pr_city_list


def get_us_state_list():
    us_states_list = []
    url = requests.get('https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations').text
    soup = BeautifulSoup(url, 'lxml')
    table = soup.find('table', "wikitable sortable").findAll('tr')
    for row in table[12:]:
        st = dict()
        state = row.find('td').get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
        state = re.sub(r'[[a-z,0-9].]', '', state)
        description = []
        for desc in row.findAll('td')[2:]:
            d = desc.get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
            if d is not ('' or r'\d'):
                description.append(d)
        description = remove(description)
        # !!!ATTENTION!!! USA change to ID
        st['country_id'] = '5cee5f7a3458e6236b9b5e3e'
        st['name'] = state
        st['description'] = description
        us_states_list.append(st)
    return us_states_list


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


if __name__ == '__main__':
    get_country_names_list()
    print('ok')

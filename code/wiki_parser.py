# coding=utf-8
import urllib3
import re
import requests
from bs4 import BeautifulSoup, NavigableString
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
        country_code = pycountry.countries.get(official_name=official_name) \
            if pycountry.countries.get(official_name=official_name) \
            else pycountry.countries.get(name=common_name.replace(', The', '').replace('The ', ''))
        if country_code:
            country_code = country_code.alpha_2
        else:
            country_code = pycountry.countries.get(name=official_name.replace(', The', '').replace('The ', ''))
            if country_code:
                country_code = country_code.alpha_2
            else:
                country_code = pycountry.countries.get(common_name=common_name.replace(', The', '').replace('The ', ''))
                if country_code:
                    country_code = country_code.alpha_2
                else:
                    country_code = pycountry.countries.get(common_name=common_name.replace(', The', '').replace('The ', ''))
                    if country_code:
                        country_code = country_code.alpha_2
                    else:
                        if common_name == 'Brunei':
                            country_code = pycountry.countries.get(name="Brunei Darussalam").alpha_2
                        else:
                            country_code = "code is unknown"
        cntr['official_name'] = official_name
        cntr['common_name'] = common_name
        cntr['code'] = country_code
        country_list.append(cntr)
    return country_list


def get_pr_city_list():
    pr_city_list=[]
    url = requests.get('https://suburbanstats.org/population/puerto-rico/list-of-counties-and-cities-in-puerto-rico').text
    soup = BeautifulSoup(url, 'lxml')
    pr_city = soup.findAll('a', title=re.compile('Population Demographics and Statistics'))
    for city in pr_city:
        ct = dict()
        ct['country'] = '5cdc1484cde53353db41d8cd'
        ct['state'] = '5cdcf40dcde5330f034fccc4'
        ct['name'] = city.get_text()
        pr_city_list.append(ct)
    return pr_city_list


def get_us_state_list():
    US_states_list = []
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
            if d is not '':
                description.append(d)
        description = remove(description)
        #!!!ATTENTION!!! USA change to ID
        st['country_id'] = '5cdc1484cde53353db41d8cd'
        st['name'] = state
        st['description'] = description
        US_states_list.append(st)
    return US_states_list


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


if __name__ == '__main__':
    get_country_names_list()
    print('ok')
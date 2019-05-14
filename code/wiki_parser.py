# coding=utf-8
import urllib3
import re
import requests
from bs4 import BeautifulSoup, NavigableString




if __name__ == '__main__':
    #get_parsed_groups(u'https://en.wikipedia.org/wiki/List_of_culinary_fruits')
    url = requests.get('https://en.wikipedia.org/wiki/List_of_sovereign_states').text
    soup = BeautifulSoup(url, 'lxml')
    my_table = soup.find('table')
    countries = my_table.findAll('td',style="vertical-align:top;")
    for country in countries:
        zzz = country.find('span',style="display:none")
        name = country.get_text().replace(zzz.get_text(),'') if zzz else country.get_text()
        name = name.replace('→', '–').replace('\n','')
        name = re.sub(r'[[a-z].]','',name)
        common_name = name.split('–')[0]
        official_name = name.split('–')[1] if len(name.split('–')) > 1 else common_name
        print(common_name, official_name)
# coding=utf-8
# import pattern.text.en as en_patt
# import pattern.text.es as es_patt
# import pattern.text.fr as fr_patt
# import pattern.text.it as it_patt
# import pattern.text.nl as nl_patt
from polyglot.downloader import downloader
from polyglot.decorators import memoize
import pymorphy2
import re

from lib.regexs import en_cardinal_numerals as en_numerals
from lib.regexs import en_ordinal_numerals as en_o_numerals
from lib.regexs import nums_billion
from lib.tools import remove_digits
from num2words import num2words
# from nltk.stem.wordnet import WordNetLemmatizer

#import lib.de_tag_pattern as de_patt
from lib.text import Text

pymorphy2_language = ['ru', 'uk']

pattern_language = {
    # 'en': en_patt,
    # 'fr': fr_patt,
    # 'es': es_patt,
    # 'de': de_patt,
    # 'it': it_patt,
    # 'nl': nl_patt
}
morph = pymorphy2.MorphAnalyzer()


def tag(text, language):
    return pattern_language[language].tag(text)


def get_base_form_for_word(word, lang, pos_tag=None):
    if lang in pymorphy2_language:
        parsed_word = morph.parse(word)[0]
        return parsed_word.normal_form
    elif lang in pattern_language.keys():
        lg = pattern_language[lang]
        if pos_tag is None:
            pos_tag = tag(word, lang)[0][1]
        if pos_tag.upper() in ['N', "NN", "NNS", "NNP", "NNPS", "NOUN", "PROPN", "PRON", "PRP", "PRP$"]:
            if ((pos_tag.upper() in ["NNS", "NNPS"]) or pos_tag.upper() not in ["N", "NN", "NNS", "NNP", "NNPS"]) and len(word) > 1:
                base_form_word = lg.singularize(word)
            else:
                base_form_word = word
        elif pos_tag.upper() in ["VERB", "AUX", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "V"]:
            base_form_word = lg.conjugate(word, lg.INFINITIVE)
        elif pos_tag.upper() in ["A", "JJ","JJR","JJS","S"]:
            # if lang == "en":
            #     wnl = WordNetLemmatizer()
            #     base_form_word = wnl.lemmatize(word, 'a')
            # else:
                base_form_word = lg.predicative(word)
        elif pos_tag.upper() in ['R',"RB","RBR","RBS"]:
            # if lang == "en":
            #     wnl = WordNetLemmatizer()
            #     base_form_word = wnl.lemmatize(word, 'r')
            # else:
                base_form_word = word
        else:
            base_form_word = word
        return base_form_word
    else:
        return word


@memoize
def get_supported_languages(task):
    supported_languages = []
    collection = downloader.get_collection(task=task).packages
    for package in collection:
        key = package.language
        key = key if isinstance(key, str) else key.encode('utf-8')
        supported_languages.append(key)
    return supported_languages


digit_re = re.compile("\d+")


def find_digit(input_str):
    #input_str = unicode(input_str)
    for c in input_str:
        #if unicode.isdigit(c):
        if str.isdigit(c):
            return True
    return False


def left_digits(input_str):
    ret = ''
    #input_str = unicode(input_str)
    for c in input_str:
        #if unicode.isdigit(c):
        if str.isdigit(c):
            ret += c
    return int(ret)


def replace_numerals(input_string, lang):
    new_string = ''
    if lang in pymorphy2_language:
        polyglot_text = Text(input_string, hint_language_code=lang)
        for token in polyglot_text.tokens:
            if find_digit(token):
                new_string += num2words(left_digits(token), lang='ru', to='cardinal') + ' '
                # try:
                #     parsed_word = morph.parse(token)[0]
                #     if str(parsed_word.tag).split(',')[0].split()[0] == 'ADJF':
                #         new_string += num2words(left_digits(token), lang='ru', to='ordinal') + ' '
                #     else:
                #         new_string += num2words(left_digits(token), lang='ru', to='cardinal') + ' '
                # except:
                #     pass
            else:
                new_string += token + ' '
    elif lang in pattern_language.keys():
        tagset = tag(input_string, lang)
        for pos_tag in tagset:
            if find_digit(pos_tag[0]):
                try:
                    if pos_tag[1] == 'CD':
                        new_string += num2words(left_digits(pos_tag[0]), lang=lang) + ' '
                    else:
                        new_string += num2words(left_digits(pos_tag[0]), lang=lang, to='ordinal') + ' '
                except:
                    new_string += pos_tag[0] + ' '
            else:
                new_string += pos_tag[0] + ' '
    else:
        new_string = input_string
        last_match = 0
        for match in digit_re.finditer(input_string):
            match_str = input_string[match.start(): match.end()]
            try:
                find_pos = new_string.find(match_str, last_match)
                new_string = new_string[0:find_pos] + ' ' + num2words(left_digits(match_str), lang=lang) + ' ' + input_string[match.end(): len(input_string)]
                last_match = find_pos+len(match_str)
            except:
                pass
    return new_string


def replace_num_to_word_around_money_sign(input_string):
    try:
        input_string = re.sub(r"((?<=\$\s)|(?<=\$))\d+", lambda m: num2words(m.group()), input_string)
        input_string = re.sub(r"\d+((?<=\$)|(?<=\s\$))", lambda m: num2words(m.group()), input_string)
    except Exception as ex:
        print(ex)
        pass
    return input_string


def replace_str_numerals(input_string):

    cardinal_numbers = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3,
        'four': 4, 'five': 5, 'six': 6, 'seven': 7,
        'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
        'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
    }
    cardinal_orders = {'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000, }
    # ordinal_numbers = {
    #     "first": 1, "second": 2,
    #     "third": 3, "fourth": 4,
    #     "fifth": 5, "sixth": 6,
    #     "seventh": 7, "eighth": 8,
    #     "ninth": 9, "tenth": 10,
    #     "eleventh": 11, "twelfth": 12,
    #     "thirteenth": 13, "fourteenth": 14,
    #     "fifteenth": 15, "sixteenth": 16,
    #     "seventeenth": 17, "eighteenth": 18,
    #     "nineteenth": 19, "twentieth": 20,
    #     "thirtieth": 30,
    #     "fortieth": 40, "fiftieth": 50,
    #     "sixtieth": 60, "seventieth": 70,
    #     "eightieth": 80, "ninetieth": 90,
    #     "hundredth": 100, "thousandth": 1000,
    #     'millionth': 1000000, 'billionth': 1000000000,
    #     }
    ordinal_numbers = {}

    # numerals = en_numerals.findall(input_string)  ## character case is already ignored
    input_string = replace_num_to_word_around_money_sign(input_string)
    numerals = [remove_digits(input_string[match.start(): match.end()]) for match in en_numerals.finditer(input_string)]
    checked_text = set()
    output = input_string
    for numeral in numerals:
        for catch_pos, catch in enumerate(re.findall('(?i)\\b(?<='+numeral+') *\w+',input_string)):
            text_part = re.search('(?i)'+numeral+' *'+catch, input_string)
            text_part = set(range(text_part.start(), text_part.end()))
            if not checked_text & text_part:
                if en_o_numerals.findall(catch):
                    numb = en_o_numerals.findall(catch)[0].replace(' ','')
                    if numb in ordinal_numbers.keys():
                        #####
                        # if last cardinal and ordinal have same rank ordinal add to numerals like a separate numeral else like a part
                        #####
                        numerals[[num for num,i in enumerate(numerals) if i ==numeral][catch_pos]]+=' '+numb #ordinal[numb]
                        checked_text |= text_part
# **************************ADD ORDINALS INTO LIST******************************************* #
    # for numeral in en_o_numerals.findall(input_string):
    #     text_part = re.search(numeral,input_string)
    #     text_part = set(range(text_part.start(), text_part.end()))
    #     if not checked_text & text_part:
    #         numerals.append(numeral)
    #         checked_text |= text_part
    for numeral in numerals:
        digit =[0]
        FLOATINGPOINT = 0
        ORDINAL = ' '
        float_part = '0.'
        for word in re.findall(r'\w+', numeral):
            # word = word.lower()
            if word in cardinal_numbers.keys() and not FLOATINGPOINT:
                digit[-1]+=cardinal_numbers[word]
            elif word in cardinal_orders.keys() and not FLOATINGPOINT:
                if digit[-1] !=0:
                    digit[-1] = digit[-1]*cardinal_orders[word]
                    digit.append(0)
                elif len(digit) >=2:
                    digit[-2] = digit[-2]*cardinal_orders[word]
            elif FLOATINGPOINT:
                if word in cardinal_numbers.keys():
                    float_part+= str(cardinal_numbers[word])
            elif en_o_numerals.findall(word):
                if word not in (u'first', u'second', u'third'):
                    ORDINAL = 'th '
                else:
                    if word == u'first':
                        ORDINAL = u'st '
                    if word == u'second':
                        ORDINAL = u'nd '
                    if word == u'third':
                        ORDINAL = u'rd'
                digit[-1]= ordinal_numbers[word]
            else:
                if word in (u'point', u'dot'):
                    FLOATINGPOINT = 1
        if float_part != '0.':
            digit = sum(digit) +float(float_part)
        else:
            digit=sum(digit)
        output = re.sub('((\b)|(?!\d))'+numeral+'((?!\w)|(?!\D))',' '+str(digit)+ORDINAL, output, re.I|re.U)  # whitespace crutch, error in regular expression, it capture whitespace after two-digit-prefix numeral
    return output


if __name__ == '__main__':
    print(replace_numerals(u'1 slovo 23 24 slovo e', 'cz'))

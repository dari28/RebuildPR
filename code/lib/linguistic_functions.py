# coding=utf-8
# import pattern.text.en as en_patt
# import pattern.text.es as es_patt
# import pattern.text.fr as fr_patt
# import pattern.text.it as it_patt
# import pattern.text.nl as nl_patt
from num2words import num2words
from polyglot.downloader import downloader
from polyglot.decorators import memoize
import pymorphy2
import re

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


if __name__ == '__main__':
    print(replace_numerals(u'1 slovo 23 24 slovo e', 'cz'))

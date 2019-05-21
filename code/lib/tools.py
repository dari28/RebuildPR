# """useful features"""
import re
import os
import sys
import traceback

import iso639
import requests
import json
import numpy
import difflib

import string
import ctypes

from itertools import permutations, product
from lib.text import Text
#
# # from lib.mongo_connection import MongoConnection
#
# punctuation = '[!"#$%&\\\'()*+,-./:;<=>?@[\\]^_`{|}~]'
#


def sample_update_matches(back_map, origin_text, matches):
    # origin_text MUST BE unicode type. In other case we have the wrong length of string and position of words
    utf_origin_text = origin_text  # if isinstance(origin_text, unicode) else origin_text.decode('utf-8')
    for match in matches:
        start_match = match['start_match']
        match['start_match'] = int(back_map[start_match])
        match['length_match'] = int(back_map[start_match + match['length_match'] - 1] - match['start_match'] + 1)
        match['word'] = utf_origin_text[match['start_match']: match['start_match'] + match['length_match']]
    return matches


def sample_strip(samples):
    """removes spaces at the beginning and at the end"""
    if isinstance(samples, list):
        result = []
        for sample in samples:
            result.append(sample.strip())
        return result
    # if isinstance(samples, str) or isinstance(samples, unicode):
    if isinstance(samples, str):  # Add SIDE(PY3)
        return samples.strip()
    return samples


def delete_in_sample(sample, start, count):
    """removes "count" elements from the "start" index"""
    end = start + count - 1
    string = sample['string']
    if len(string) < start + count or start < 0 or count <= 0:
        return sample
    new_sample = {}
    new_matches = []
    for match in sample['matches']:
        sm = match['start_match']
        lm = match['length_match']
        rm = sm + lm - 1
        new_match = {}
        if start < sm:
            new_start_match = start if end >= sm - 1 else sm - count
        else:
            new_start_match = sm
        if end < sm or start > rm:
            new_match['start_match'] = new_start_match
            new_match['length_match'] = lm
            new_matches.append(new_match)
        else:
            new_length_match = ((rm - end) if (rm > end) else 0) + ((start - sm) if (sm < start) else 0)

            if new_length_match > 0:
                new_match['start_match'] = new_start_match
                new_match['length_match'] = new_length_match
                new_matches.append(new_match)

    new_sample['matches'] = new_matches
    new_sample['string'] = string[:start]+string[start+count:]
    return new_sample


def sample_strip_and_recalc_matches(sample):
    """removes spaces at the beginning and at the end AND recalc matches"""
    ret_sample = sample
    string = sample["string"]
    len_string = len(string)
    zeros_left = len_string - len(string.lstrip())
    zeros_right = len_string - len(string.rstrip())
    if zeros_right > 0:
        ret_sample = delete_in_sample(ret_sample, len_string - zeros_right, zeros_right)
    if zeros_left > 0:
        ret_sample = delete_in_sample(ret_sample, 0, zeros_left)
    return ret_sample


def sample_remove_tabs(origin_text, result='map', mode='min'):
    """Remove tabs and multiple spaces"""
    if mode == 'min':
        tab = '\t'
    else:
        tab = '\s'
    new_text = re.sub(tab, ' ', origin_text)
    new_text = re.sub(' +', ' ', new_text)
    if result == 'map':
        skip_map = check_skip_string(new_text, origin_text)
        back_map = numpy.where(numpy.array(skip_map) == 0)[0]
        return new_text, back_map
    elif result == 'skip':
        skip_map = check_skip_string(new_text, origin_text)
        return new_text, skip_map
    else:
        return new_text


def fixing_line_breaks(text):
    return re.sub('[\n\r\f]+', '.', text)


def adaptiv_remove_tab(origin_text):
    punctuation_sign = '[!"#$%&\'()*+,-\./:;<=>?@[\\]^_`{|}~]'
    tab = '[\n\r\f]'

    end = 0
    new_text = ''
    for match in re.finditer('{0}{1}+'.format(punctuation_sign, tab), origin_text):
        # b = match.regs[0]
        b = match.span()  # Add SIDE(PY3)
        new_text += origin_text[end:(b[0] + 1)] + ' '*(b[1] - b[0] - 1)
        end = b[1]
    new_text += origin_text[end:]
    fixed_text = new_text

    end = 0
    new_text = ''
    for match in re.finditer('{1}+(?={0})'.format(punctuation_sign, tab), fixed_text):  # ' '
        # b = match.regs[0]
        b = match.span()  # Add SIDE(PY3)
        new_text += fixed_text[end:(b[0])] + ' ' * (b[1] - b[0] - 1)
        end = b[1]
    new_text += fixed_text[end:]
    fixed_text = new_text

    end = 0
    new_text = ''
    for match in re.finditer('{1}+(?!{0})'.format(punctuation_sign, tab), fixed_text):  # '.'
        # b = match.regs[0]
        b = match.span()  # Add SIDE(PY3)
        new_text += fixed_text[end:(b[0])] + '.' + ' ' * (b[1] - b[0] - 1)
        end = b[1]
    new_text += fixed_text[end:]
    fixed_text = new_text

    new_text = re.sub(' +', ' ', fixed_text)
    skip_map = check_skip_string(new_text, fixed_text)
    back_map = numpy.where(numpy.array(skip_map) == 0)[0]
    return new_text, back_map


def remove_tab(origin_text):
    tab = '\s'
    fixed_text = re.sub(tab, ' ', origin_text)
    new_text = re.sub(' +', ' ', fixed_text)
    skip_map = check_skip_string(new_text, fixed_text)
    back_map = numpy.where(numpy.array(skip_map) == 0)[0]
    return new_text, back_map


def fixe_samples_match(skip_map, origin_matches):
    matches = []
    if sum(skip_map) > 0:
        shift_map = numpy.cumsum(skip_map)
        for match in origin_matches:
            new_match = {}
            start_origin = match['start_match']
            new_match['start_match'] = start_origin - shift_map[start_origin]
            end_origin = start_origin + match['length_match'] - 1
            new_match['length_match'] = end_origin - shift_map[end_origin] - new_match[
                                        'start_match'] + 1
            matches.append(new_match)
    else:
        matches = list(origin_matches)
    return matches


def to_lower(text):
    if isinstance(text, str):
        return str.lower(text)  # Add SIDE(PY3)
    # return string.lower(text) # Delete SIDE(PY3)

    # if isinstance(text, unicode):  # Delete SIDE(PY3)
    #     return unicode.lower(text)  # Delete SIDE(PY3)
    return text


def sort_model(models, tag='type'):
    """groups models by type"""
    result_set = {}
    for model in models:
        if model[tag] not in result_set:
            result_set[model[tag]] = [model]
        else:
            result_set[model[tag]].append(model)
    return result_set


def get_abs_path(path):
    """"""
    path = path if os.path.isabs(path) else \
        os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(sys.modules['nlp.config'].__file__)),
                path
            )
        )
    return path


def find_nth_overlapping(haystack, needle, n):
    """find n-ed entrance needle to haystack"""
    start = -1
    while start >= 0 and n > 0:
        start = haystack.find(needle, start+1)
        n -= 1
    return start


def search_positions_entity(entity):
    """Search positions entity in polyglot.entities"""
    pos_token = 0
    entry = 0
    for token in entity.parent.tokens:
        if pos_token == entity.start:
            break
        if token == entity.parent.tokens[entity.start]:
            entry += 1
        pos_token += 1
    start = find_nth_overlapping(entity.parent.row, entity.parent.tokens[entity.start], entry + 1)

    if len(entity._collection) > 1:
        pos_token = 0
        entry = 0
        for token in entity.parent.tokens:
            if pos_token == (entity.end-1):
                break
            if token == entity.parent.tokens[entity.end-1]:
                entry += 1
            pos_token += 1
        start_lost = find_nth_overlapping(entity.parent.row, entity.parent.tokens[entity.end-1], entry + 1)
        end = start_lost + len(entity.parent.tokens[entity.end-1])
    else:
        end = start + len(entity.parent.tokens[entity.start])
    return start, end


def search_positions_word(word, index_word, polyglot_text):
    """Search positions entity in polyglot.words"""
    pos_token = 0
    entry = 0
    for token in polyglot_text.words:
        if pos_token == index_word:
            break
        if token == word:
            entry += 1
        pos_token += 1
    start = find_nth_overlapping(polyglot_text.row, word, entry + 1)
    end = start + len(word)
    return start, end


def message_box(text='', head='', type_box=0):
    """Universal message box"""
    if sys.platform == "linux" or sys.platform == "linux2":
        # linux
        pass
    elif sys.platform == "darwin":
        # OS X
        pass
    elif sys.platform == "win32":
        # Windows...
        ctypes.windll.user32.MessageBoxA(None, text, head, type_box)


class ParseStanfordTSV(object):
    """Converts and filters the stanford NER classification results"""
    def __init__(self, classification, set_tags, origin_text):
        self.classification = classification
        self.set_tags = set_tags
        self.origin_text = origin_text

    def __iter__(self):
        end_pos = 0
        for word_class in re.finditer('.+(?<!\r)(?=\r?\n)', self.classification):
            try:
                # word, tag = string.split(word_class.group(0), '\t')
                word, tag = str.split(word_class.group(0), '\t')
                start_pos = self.origin_text.find(word,  end_pos)
                end_pos = start_pos + len(word)
                if tag in self.set_tags:
                    yield {'match': {'start_match': start_pos,
                                     'length_match': len(word),
                                     'word': word},
                           'tag': tag}
            except:
                pass


class ParsePolyglot(object):
    """Converts and filters the polyglot entities"""
    def __init__(self, classification, set_tags, origin_text, text_class):
        self.classification = classification
        self.set_tags = set_tags
        self.origin_text = origin_text
        self.text_class = text_class

    def __iter__(self):
        end_pos = 0
        for word_class in self.classification:
            try:
                if word_class.tag in self.set_tags:
                    for i in range(word_class.start, word_class.end):
                        # utf8_units = self.text_class.words[i] if isinstance(self.text_class.words[i], unicode) \
                        #     else self.text_class.words[i].decode('utf8')
                        utf8_units = self.text_class.words[i]
                        if i == word_class.start:
                            start_pos = self.origin_text.find(utf8_units, end_pos)
                        end_pos = self.origin_text.find(utf8_units, end_pos) + len(utf8_units)

                    yield {'match': {'start_match': start_pos,
                                     'length_match': len(self.origin_text[start_pos: end_pos]),
                                     'word': self.origin_text[start_pos: end_pos]},
                           'tag': word_class.tag}
            except:
                pass


class ParsePolyglotPolarity(object):
    """Converts and filters the polyglot entities"""
    def __init__(self, classification, set_tags, origin_text, dict_tags):
        self.classification = classification
        self.set_tags = set_tags
        self.origin_text = origin_text
        self.dict_tags = dict_tags

    def __iter__(self):
        end_pos = 0
        for word in self.classification:
            try:
                tag = word.polarity
                utf8_units = word  # if isinstance(word, unicode) else word.decode('utf8')
                start_pos = self.origin_text.find(utf8_units, end_pos)
                end_pos = start_pos + len(utf8_units)
                if tag:
                    if self.dict_tags[tag] in self.set_tags:
                        yield {'match': {'start_match': start_pos,
                                         'length_match': len(utf8_units),
                                         'word': utf8_units},
                               'tag': self.dict_tags[tag]}
            except:
                print(get_error())


class EncodingPredictEntity(object):
    def __init__(self, matches, origin_text):
        self.matches = matches
        self.origin_text = origin_text

    def __iter__(self):
        end_pos = 0
        entity = self.matches['entity']
        matches = []
        doc = self.origin_text
        for match in self.matches['matches']:
            tag = '<{}>'.format(match['tag'])
            start = doc.find(match['match']['word'], end_pos)
            length = match['match']['length_match']
            doc = doc[:start] + tag + doc[start + length:]
            start_pos = doc.find(tag, end_pos)
            end_pos = start_pos + len(tag)
            matches.append({'match': {'start_match': start,
                                      'length_match': end_pos - start_pos},
                            'tag': match['tag']})
        yield {'matches': matches,
               'entity': entity,
               'string': doc}


class DecodingPredictEntity(object):

    def __init__(self, match, words):
        self.match = match
        self.words = words
        tags = [match['tag'] for match in match['matches']]
        self.tags = dict((tag, tags.count(tag)) for tag in tags)

    def __iter__(self):
        combination_words = []
        tags = self.tags.keys()
        for tag in tags:
            count = self.tags[tag]
            if count == 1:
                combination_words.append(self.words[tag])
            else:
                combination_words.append(list(permutations(self.words[tag], self.tags[tag])))
        combination = list(product(*combination_words))
        samples = []
        for comb in combination:
            sample = self.replace(self.match['string'], tags, comb)
            samples.append(sample)
        samples.append({'string': self.match['string'],
                        'matches':self.match['matches'],
                        'entity': self.match['entity']})
        yield samples

    def replace(self, doc, tags, combination):
        document = doc
        words = {}
        for tag in tags:
            words[tag] = combination[tags.index(tag)].__iter__()
        end_pos = 0
        matches = []
        for match in self.match['matches']:
            word = words[match['tag']].next()
            tag = '<{}>'.format(match['tag'])
            start = document.find(tag, end_pos)
            length = match['match']['length_match']
            document = document[:start] + word + document[start + length:]
            start_pos = document.find(word, end_pos)
            end_pos = start_pos + len(word)
            matches.append({'match': {'start_match': start,
                                      'length_match': end_pos - start_pos,
                                      'word': word},
                            'tag': match['tag']})
        return {'string': document,
                'matches': matches,
                'entity': self.match['entity']}


class ParseMatchesMorphemes(object):
    """Converts and filters the polyglot entities"""
    def __init__(self, matches, text, lang=None):
        self.matches = matches
        if isinstance(text, Text):
            self.text_class = text
            self.origin_text = text.raw
        else:
            self.origin_text = text
            self.text_class = Text(text, hint_language_code=lang)

    def __iter__(self):
        end_pos = 0
        ini_pos = 0
        left_pos = 0
        right_pos = 0
        n_word = -1
        n_word_start = 0
        # morphemes = [ morph.string.strip() for morph in self.text_class.morphemes]
        morphemes = []
        [morphemes.extend(morph.morphemes) for morph in self.text_class.tokens]
        for match in self.matches:
            if right_pos > match[0]:
                n_word = n_word_start - 1
                end_pos = left_pos
            while match[0] > end_pos:
                n_word += 1
                ini_pos = self.origin_text.find(morphemes[n_word], end_pos)
                end_pos = ini_pos + len(morphemes[n_word])
            n_word_start = n_word
            left_pos = ini_pos
            while end_pos < match[1]:
                right_pos = end_pos
                n_word += 1
                ini_pos = self.origin_text.find(morphemes[n_word], end_pos)
                end_pos = ini_pos + len(morphemes[n_word])
            if end_pos > match[1]:
                end_pos -= len(morphemes[n_word])
                n_word -= 1
            if ini_pos <= match[1]:
                right_pos = end_pos
            yield [self.origin_text[left_pos: right_pos], left_pos, right_pos]


class ParseMatchesWords(object):
    """Converts and filters the polyglot entities"""
    def __init__(self, matches, text, lang=None):
        self.matches = matches
        if isinstance(text, Text):
            self.text_class = text
            self.origin_text = text.row
        else:
            self.origin_text = text
            self.text_class = Text(text, hint_language_code=lang)

    def __iter__(self):
        end_pos = 0
        ini_pos = 0
        left_pos = 0
        right_pos = 0
        n_word = -1
        n_word_start = 0
        for match in self.matches:
            if right_pos > match[0]:
                n_word = n_word_start - 1
                end_pos = left_pos
            while match[0] > end_pos:
                n_word += 1
                ini_pos = self.origin_text.find(self.text_class.words[n_word], end_pos)
                end_pos = ini_pos + len(self.text_class.words[n_word])
            n_word_start = n_word
            left_pos = ini_pos
            while end_pos < (match[1]):
                right_pos = end_pos
                n_word += 1
                ini_pos = self.origin_text.find(self.text_class.words[n_word], end_pos)
                end_pos = ini_pos + len(self.text_class.words[n_word])
            if ini_pos <= (match[1]):
                right_pos = end_pos

            yield [self.origin_text[left_pos: right_pos], left_pos, right_pos]


class ParseMatchesUnits(object):
    """"""
    def __init__(self, matches, text, units, units_tag=None):
        self.matches = matches
        try:
            text = text.decode('utf8')
        except:
            pass
        self.origin_text = text
        self.units = units
        self.units_tag = units_tag

    def __iter__(self):

        for match in self.matches:
            end_pos = -1
            ini_pos = 0
            left_pos = -1
            right_pos = -1
            n_word = -1
            n_word_start = 0
            tag_match = []
            if right_pos > match[0]:
                n_word = n_word_start
                end_pos = left_pos
            while match[0] > end_pos:
                n_word += 1
                utf8_units = self.units[n_word]
                try:
                    utf8_units = utf8_units.decode('utf8')
                except:
                    pass
                end_pos = max(end_pos, 0)
                ini_pos = self.origin_text.find(utf8_units, end_pos)
                end_pos = ini_pos + len(utf8_units)

            n_word_start = max(n_word, 0)
            left_pos = ini_pos
            # end_pos = ini_pos

            while end_pos < match[1]:
                right_pos = end_pos
                if self.units_tag and n_word > -1:
                    tag_match.append(self.units_tag[n_word][1])
                n_word += 1
                utf8_units = self.units[n_word]
                try:
                    utf8_units = utf8_units.decode('utf8')
                except:
                    pass
                ini_pos = self.origin_text.find(utf8_units, end_pos)
                end_pos = ini_pos + len(utf8_units)
            if ini_pos <= match[1]:
                right_pos = end_pos
                if self.units_tag:
                    tag_match.append(self.units_tag[n_word][1])
                n_word += 1
            n_word -= 1

            if self.origin_text[left_pos: right_pos]==u'':
                pass
            yd = [self.origin_text[left_pos: right_pos], left_pos, right_pos, n_word_start, n_word, tag_match]
            yield yd


class ParseMatchesUnitsBack(object):
    """"""
    def __init__(self, matches, text, units, units_tag=None):
        self.matches = matches
        try:
            text = text.decode('utf8')
        except:
            pass
        self.origin_text = text
        self.units = units
        self.units_tag = units_tag

    def __iter__(self):
        end_pos = 0
        ini_pos = 0
        left_pos = 0
        right_pos = 0
        n_word = -1
        n_word_start = 0
        for match in self.matches:
            tag_match = []
            if n_word > match[0]:
                n_word = n_word_start - 1
                end_pos = left_pos
            while match[0] > n_word:
                n_word += 1
                utf8_units = self.units[n_word]
                try:
                    utf8_units = utf8_units.decode('utf8')
                except:
                    pass
                ini_pos = self.origin_text.find(utf8_units, end_pos)
                end_pos = ini_pos + len(utf8_units)
            n_word_start = n_word
            left_pos = ini_pos
            while n_word <= match[1]:
                right_pos = end_pos
                if self.units_tag:
                    tag_match.append(self.units_tag[n_word][1])
                n_word += 1
                if n_word >= len(self.units):
                    break
                utf8_units = self.units[n_word]
                try:
                    utf8_units = utf8_units.decode('utf8')
                except:
                    pass
                ini_pos = self.origin_text.find(utf8_units, end_pos)
                end_pos = ini_pos + len(utf8_units)

            yield [self.origin_text[left_pos: right_pos], left_pos, right_pos, n_word_start, n_word-1, tag_match]


def check_skip_string_old(text, origin_text):
    try:
        text = text.decode('utf8')
    except:
        pass
    try:
        origin_text = origin_text.decode('utf8')
    except:
        pass
    j = 0
    dif_map = [0]*len(origin_text)
    for i in range(len(text)):
        while text[i] != origin_text[j]:
            dif_map[j] = 1
            j += 1
        j += 1
    return dif_map


def check_skip_string(text, origin_text):
    try:
        text = text.decode('utf8')
    except:
        pass
    try:
        origin_text = origin_text.decode('utf8')
    except:
        pass
    dif_map = [1]*len(origin_text)
    diff = difflib.SequenceMatcher(None, text, origin_text)
    last_match = {'a': -1, 'b': -1}
    matches = diff.get_matching_blocks()
    for match in diff.get_matching_blocks():
        if match.size == 0:
            break
        f = last_match['b'] + 1
        ff = match.a - last_match['a'] - 1
        key = range(last_match['b'] + 1, last_match['b'] + 1 + match.a - last_match['a'] - 1)
        dif_map[last_match['b'] + 1: last_match['b'] + match.a - last_match['a']] = [0 for i in key]
        key = range(match.b, match.b + match.size)
        dif_map[match.b: match.b + match.size] = [0 for i in key]
        last_match = {'a': match.a + match.size - 1, 'b': match.b + match.size - 1}
    return dif_map


def check_intersection_range(range1, range2):
    """"""
    result = False
    if range1[0] >= range2[0] and  range1[0] <= range2[1]:
        result = True
    elif range1[1] >= range2[0] and  range1[1] <= range2[1]:
        result = True
    elif range2[0] >= range1[0] and range2[0] <= range1[1]:
        result = True
    elif range2[1] >= range1[0] and range2[1] <= range1[1]:
        result = True
    return result


def list_decode(data, codec='utf-8'):
    """"""
    return [x.decode(codec) for x in data]


def get_error():
    ex_type, ex, tb = sys.exc_info()
    results = {'TypeError': str(ex_type),
               'MessageError': str(ex),
               'TracebackError': "".join(traceback.format_exc())
               }
    return results


def send_post(url, data, cls=None):
    try:
        req = requests.post(url, json=data)
        print("Status: {0}. Url: {2}. Response: {1} ").format(req.status_code, req.text, url)
    except requests.RequestException:
        print("Status: {0}. Url: {2}. Response: {1} ").format(404, None, url)
    except Exception:
        error = get_error()
        print(error)


def send_many_post(urls, data, cls=None):
    if not isinstance(urls, list):
        urls = [urls]
    for url in urls:
        send_post(url, data)


# def create_tmp_file():
#     from nlp.config import TEMP_FILES_DIRECTORY
#     path = get_abs_path(TEMP_FILES_DIRECTORY)
#     if not os.path.isdir(path):
#         os.mkdir(path)
#     import uuid
#     name = os.path.join(path, str(uuid.uuid4()))
#     f = open(name, 'w')
#     return f
#
#
# def open_tmp_file(fname):
#     from nlp.config import TEMP_FILES_DIRECTORY
#     path = get_abs_path(TEMP_FILES_DIRECTORY)
#     name = os.path.join(path, fname)
#     f = open(name, 'r+b')
#     return f
#
#
# def remove_tmp_file(fname):
#     from nlp.config import TEMP_FILES_DIRECTORY
#     path = get_abs_path(TEMP_FILES_DIRECTORY)
#     os.remove(os.path.join(path, fname))
#
#
# def convert_part1_to_part3(lang):
#     try:
#         l = iso639.languages.get(part3=lang)
#     except KeyError:
#         try:
#             l = iso639.languages.get(part1=lang)
#         except KeyError:
#             if lang == 'qcn':
#                 return 'qcn'
#             else:
#                 return
#     return l.part3
#
#
# def convert_part3_to_part1(lang):
#     try:
#         l = iso639.languages.get(part3=lang)
#     except KeyError:
#         try:
#             l = iso639.languages.get(part1=lang)
#         except KeyError:
#             return
#     language = l.part1
#     if language:
#         return language
#     else:
#         return l.part3
#
#
# def convert_name_to_part3(name):
#     if name == 'Slovene':
#         name = 'Slovenian'
#     try:
#         l = iso639.languages.get(name=name)
#     except KeyError:
#         return
#     return l.part3
#
# def convert_name_to_part1(name):
#     if name == 'Slovene':
#         name = 'Slovenian'
#     try:
#         l = iso639.languages.get(name=name)
#     except KeyError:
#         return
#     return l.part1

re_special = ['?', '(', ')', '<', '>', '[', ']', '$', '^', '.', '|', '*', '+', '{', '}']


def escape(pattern):
    s = list(pattern)
    for i, c in enumerate(pattern):
        if c == "\000":
            s[i] = "\\000"
        if c in re_special:
            s[i] = " \{}".format(c)
    return pattern[:0].join(s)

# if __name__ == '__main__':
#     # mongo = MongoConnection()
#     # entity_standford = list(mongo.entity.find({'type': 'default_stanford'}))
#     # set_id = [entity['_id'] for entity in entity_standford]
#     # result = export_data(entities=set_id)
#     # print result
#     #a = check_skip_string('124', '1234')
#     #print a
#     #b = {'string': 'as   df ', 'matches': [{'start_match': 0, 'length_match': 2}, {'start_match': 5, 'length_match': 2}]}
#     #a = fixe_samples_match('asdf', b['string'], b['matches'])
#     #p rint a
#     #a = check_skip_string('as .. df', 'as      \n.  df')
#     #print a
#     # text, back_map = adaptiv_remove_tab('asd.\n\n vbn\r\n.  \n  \n\r.\r\n')
#     # test_text = 'asd. vbn . . . '
#     # result = text == test_text
#     # print text
#     pass
#
# ####################################################
# #"""TEST delete_in_sample(sample, start, count)"""
#     # sample = {u'matches': [
#     #     {u'length_match': 7, u'start_match': 10}
#     # ], u'string': u'\xbfPor qu\xe9 mi WiFi entra y sale? '}
#     # new_sample0 = delete_in_sample(sample, 0, 1)  # LEFT
#     #
#     # new_sample1 = delete_in_sample(sample, 1, 1)  #LEFT
#     # # {u'length_match': 7, u'start_match': 9}
#     # new_sample2 = delete_in_sample(sample, 6, 3)
#     # # {u'length_match': 7, u'start_match': 7}
#     # new_sample3 = delete_in_sample(sample, 6, 4)
#     # # {u'length_match': 7, u'start_match': 6}
#     # new_sample4 = delete_in_sample(sample, 6, 7)
#     # # {u'length_match': 4, u'start_match': 6}
#     # new_sample5 = delete_in_sample(sample, 10, 3)
#     # # {u'length_match': 4, u'start_match': 10}
#     # new_sample6 = delete_in_sample(sample, 10, 7)
#     # # {}
#     # new_sample7 = delete_in_sample(sample, 10, 10)
#     # # {}
#     # new_sample8 = delete_in_sample(sample, 12, 2)
#     # # {u'length_match': 5, u'start_match': 10}
#     # new_sample9 = delete_in_sample(sample, 12, 8)
#     # # {u'length_match': 2, u'start_match': 10}
#     # new_sample10 = delete_in_sample(sample, 17, 3) #RIGHT
#     # # {u'length_match': 7, u'start_match': 10}
#     # new_sample11 = delete_in_sample(sample, 0, 31)
#     # # {'matches': [], 'string': u''}
#     # print(new_sample4)
# #######################################################
#     #string = "  Hello   "
#     #string = " Mi WiFi gotas en mi sala de estar.\u00a0"
#     # string = u" Mi WiFi gotas en mi sala de estar.\u00a0"
#     # print(type(string))
#     # len_string = len(string)
#     # zeros_all = len_string - len(string.strip())
#     # print(len(string))
#     # zeros_left = len_string - len(string.lstrip())
#     # print(len(string))
#     # zeros_right = len_string - len(string.rstrip())
#     # print(len(string))
#     ###################################################
def country_code():
    import csv
    with open('/home/vnc/Desktop/RebuildPR/data/country_code_alpha2.csv', mode='r') as infile:
        reader = csv.reader(infile)
        my_dict = {rows[1].lower(): rows[0] for rows in reader}
    return my_dict

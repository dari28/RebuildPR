
import os

from polyglot.decorators import memoize


from nlp.config import STANFORD, JAVA_CONFIG, STANFORD_PREPOSSESSING
from lib import tools
from lib.text import Text
from lib.linguistic_functions import get_base_form_for_word, pattern_language, tag

import jnius_config

jnius_config.add_options('-Xrs', '-Xmx{0}'.format(JAVA_CONFIG['max_size']))
# jnius_config.add_classpath(tools.get_abs_path(SPHINX['path_sphinx']))
jnius_config.add_classpath(tools.get_abs_path(STANFORD['path_stanford_ner']))
# jnius_config.add_classpath(tools.get_abs_path(MARY_TTS['path_mary_tts']))


@memoize
def GetJavaClass(name_class):
    os.environ['CLASSPATH'] = tools.get_abs_path(STANFORD['path_stanford_ner'])
    from jnius import autoclass
    return autoclass(name_class)


PropertiesFile = GetJavaClass('edu.stanford.nlp.util.StringUtils').propFileToProperties
ClassifierFlags = GetJavaClass('edu.stanford.nlp.sequences.SeqClassifierFlags')
CRFClassifier = GetJavaClass('edu.stanford.nlp.ie.crf.CRFClassifier')
ColumnDataClassifier = GetJavaClass('edu.stanford.nlp.classify.ColumnDataClassifier')
Annotation = GetJavaClass('edu.stanford.nlp.pipeline.Annotation')
TokenizerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.TokenizerAnnotator')
WordsToSentencesAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.WordsToSentencesAnnotator')
POSTaggerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.POSTaggerAnnotator')
NERCombinerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.NERCombinerAnnotator')
MorphAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.MorphaAnnotator')
jInteger = GetJavaClass('java.lang.Integer')
jString = GetJavaClass('java.lang.String')
jMap = GetJavaClass('java.util.HashMap')
SystemJava = GetJavaClass('java.lang.System')
jProperties = GetJavaClass('java.util.Properties')
jArrayList = GetJavaClass('java.util.ArrayList')


def to_prop(prop):
    properties = jProperties()
    for key in prop:
        if "=" in prop[key]:
            for prop_splited in prop[key].split(","):
                ps = prop_splited.split("=")
                prop_splited_key = ps[0]
                prop_splited_value = ps[1]
                properties.setProperty(jString(prop_splited_key), jString(prop_splited_value))
        else:
            properties.setProperty(jString(key), jString(prop[key]))
    return properties


def annotation_polyglot(data, language):
    # map_setting = {
    #     'part_of_speech': getPOSTaggerAnnotator
    # }
    text = Text(data, language)
    text_row = text.raw
    text_row = text_row if isinstance(text_row, str) \
        else text_row.encode('utf-8')
    jannotation = Annotation(jString(text_row))
    # jtokens = getTokens(text, text.words)
    # annot.set(getClassAnnotation('TokensAnnotation'), jtokens)
    jsentence, jtokens = getSentence(text)
    # don't convert - Java
    jannotation.set(getClassAnnotation('TokensAnnotation'), jtokens)
    # don't convert - Java
    jannotation.set(getClassAnnotation('SentencesAnnotation'), jsentence)
    return jannotation


def getClassAnnotation(name_class):
    return GetJavaClass('edu.stanford.nlp.ling.CoreAnnotations$' + name_class)().getClass()


def getTokens(sentence, tokens, from_pos=0, save_inex=False, index_sentence=None):
    result = jArrayList()
    end_pos = 0
    index = 1
    core_label = None
    # sentence = if isinstance(sentence, unicode) else sentence.decode('utf8')  # Delete SIDE(PY3)
    try:
        sentence = sentence.decode('utf8')  # Add SIDE(PY3)
    except UnicodeError:
        pass
    except AttributeError:
        pass
    for tok in tokens:
        # tok = if isinstance(tok, unicode) else tok.decode('utf8')  # Delete SIDE(PY3)
        try:
            tok = tok.decode('utf8')  # Add SIDE(PY3)
        except UnicodeError:
            pass
        except AttributeError:
            pass
        start_pos = sentence.find(tok, end_pos)
        before = sentence[end_pos: start_pos]
        if core_label:
            core_label.setAfter(before)
        end_pos = start_pos + len(tok)
        core_label = getCoreLabel(tok.encode('utf-8'), start_pos + from_pos, end_pos + from_pos - 1)
        core_label.setBefore(before)
        if index_sentence:
            # core_label.setSentIndex(jInteger(index_sentence))
            core_label.setSentIndex(index_sentence)
        if save_inex:
            core_label.setIndex(index)
            index += 1
        result.add(core_label)
    return result


def getCoreLabel(token_text, token_begin, token_end):
    '''
    :param token_text: encoded uft-8 text
    :param token_begin:
    :param token_end:
    :return:
    '''
    cl = GetJavaClass('edu.stanford.nlp.ling.CoreLabel')(5)
    # cl.setValue(jString(token_text))
    # cl.setWord(jString(token_text))
    # cl.setOriginalText(jString(token_text))
    cl.setValue(token_text)
    cl.setWord(token_text)
    cl.setOriginalText(token_text)
    cl.set(getClassAnnotation('CharacterOffsetBeginAnnotation'), jInteger(token_begin))
    cl.set(getClassAnnotation('CharacterOffsetEndAnnotation'), jInteger(token_end))
    return cl


def getSentence(text):
    jSentenceSet = GetJavaClass('java.util.ArrayList')()
    jTokensSet = GetJavaClass('java.util.ArrayList')()
    tokenOffset = 0
    for sentence in text.sentences:
        jSentence = Annotation(sentence.raw.encode('utf-8'))
        jSentence.set(getClassAnnotation('CharacterOffsetBeginAnnotation'), jInteger(sentence.start))
        jSentence.set(getClassAnnotation('CharacterOffsetEndAnnotation'), jInteger(sentence.end-1))
        jtokens = getTokens(sentence.raw, sentence.words, sentence.start, True, jSentenceSet.size())
        jTokensSet.addAll(jtokens)
        #don't convert - Java
        jSentence.set(getClassAnnotation('TokensAnnotation'), jtokens)
        jSentence.set(getClassAnnotation('TokenBeginAnnotation'), jInteger(tokenOffset))
        tokenOffset += len(sentence.words)
        jSentence.set(getClassAnnotation('TokenEndAnnotation'), jInteger(tokenOffset))
        jSentence.set(getClassAnnotation('SentenceIndexAnnotation'), jInteger(jSentenceSet.size()))
        jSentenceSet.add(jSentence)
    return jSentenceSet, jTokensSet


@memoize
def load_stanford_models(key):
    return CRFClassifier.getClassifier(tools.get_abs_path(STANFORD[key]))


def func(prop_ner_temp):
    result = []
    enamurate = prop_ner_temp.propertyNames()
    while enamurate.hasMoreElements():
        result.append(enamurate.nextElement())
    return result


@memoize
def load_stanford_ner(text, language):
    prop = get_prop_for_language(language)
    prop.update({'ner.model': tools.get_abs_path(STANFORD[text]), 'ner.useSUTime': 'false'})
    prop_ner = to_prop(prop)
    return NERCombinerAnnotator(prop_ner)


@memoize
def get_prop_for_language(language):
    if language in STANFORD_PREPOSSESSING:
        prop = STANFORD_PREPOSSESSING[language]
        prop['pos.model'] = tools.get_abs_path(prop['pos.model'])
        if 'segment.model' in prop:
            prop['segment.model'] = tools.get_abs_path(prop['segment.model'])
        if 'segment.serDictionary' in prop:
            prop['segment.serDictionary'] = tools.get_abs_path(prop['segment.serDictionary'])
        if 'segment.sighanCorporaDict' in prop:
            prop['segment.sighanCorporaDict'] = tools.get_abs_path(prop['segment.sighanCorporaDict'])
        return prop
    else:
        return None


@memoize
def getTokenizerAnnotator(language):
    prop = get_prop_for_language(language)
    if prop:
        prop_an = to_prop(prop)
        return TokenizerAnnotator(prop_an)
    else:
        return None


@memoize
def getWordsToSentencesAnnotator(language):
    prop = get_prop_for_language(language)
    if prop:
        prop_an = to_prop(prop)
        return WordsToSentencesAnnotator(prop_an)
    else:
        return None


@memoize
def getPOSTaggerAnnotator(language):
    prop = get_prop_for_language(language)
    if prop:
        if 'pos.model' not in prop:
            return None
        prop_an = to_prop(prop)
        #return POSTaggerAnnotator('pos', prop_an)
        return POSTaggerAnnotator(jString('pos'), prop_an)
    else:
        return None


@memoize
def getMorphAnnotator(language):
    if language == 'en':
        return MorphAnnotator()
    else:
        return None


def get_column(settings, start_column=2):
    current_column = start_column
    result = ''
    map_setting = {
      'part_of_speech': 'tag',
      'normal_form': 'lemma'
    }
    for key in map_setting:
        if key in settings and settings[key]:
            result += ',{0}={1}'.format(map_setting[key], current_column)
            current_column += 1
    return result


def get_anotation_row(token, settings):
    result = ''
    map_setting = {
        'part_of_speech': 'PartOfSpeechAnnotation',
        'normal_form': 'LemmaAnnotation'
    }
    for key in map_setting:
        if key in settings and settings[key]:
            tag = token.get(getClassAnnotation(map_setting[key]))
            result += '\tA{0}'.format(tag)
    return result


def annotation_stanford(data, language, settings):
    '''
    :param data:
    :param language:
    :param settings:
    :return:
    '''
    map_setting = {
        'part_of_speech': getPOSTaggerAnnotator,
    }
    # annotation = Annotation(data)  # Delete SIDE(PY3)
    annotation = Annotation(jString(data))  # Add SIDE(PY3)(NO DATA WITHOUT IT)
    getTokenizerAnnotator(language).annotate(annotation)
    getWordsToSentencesAnnotator(language).annotate(annotation)
    # getPOSTaggerAnnotator(language).annotate(annotation)
    for key in map_setting:
        if settings and key in settings and settings[key]:
            map_setting[key](language).annotate(annotation)
    return annotation


def polyglot_posttag(annotation, language, text=None, data=None):
    if language in pattern_language:
        if not data:
            data = annotation.get(getClassAnnotation('TextAnnotation'))
        tags = tag(data, language)
    else:
        if not text:
            if not data:
                data = annotation.get(getClassAnnotation('TextAnnotation'))
            text = Text(data, language)
        tags = text.pos_tags
    jTokkens = annotation.get(getClassAnnotation('TokensAnnotation'))
    for i in range(jTokkens.size()):
        jTokken = jTokkens.get(i)
        word = jTokken.get(getClassAnnotation('TextAnnotation'))
        # Delete SIDE(PY3)
        # if isinstance(word, str):
        #    word = word.decode('utf-8')
        try:
            word = word.decode('utf8')  # Add SIDE(PY3)
        except UnicodeError:
            pass
        except AttributeError:
            pass
        if word == tags[i][0]:
            tag_pos = tags[i][1]
            # Delete SIDE(PY3)
            # if isinstance(tag_pos, str):
            #    tag_pos = tag_pos.decode('utf-8')
            try:
                tag_pos = tag_pos.decode('utf8')  # Add SIDE(PY3)
            except UnicodeError:
                pass
            except AttributeError:
                pass
            jTokken.set(getClassAnnotation('PartOfSpeechAnnotation'), jString(tag_pos))
        else:
            raise ValueError(('Error in stanford module: {0} not equals {1}'.format(word, tags[i][0])))


def polyglot_lemm(annotation, language, text=None, pos_tags=None):
    jTokkens = annotation.get(getClassAnnotation('TokensAnnotation'))
    for i in range(jTokkens.size()):
        jTokken = jTokkens.get(i)
        word = jTokken.get(getClassAnnotation('TextAnnotation')) if not text else text.words[i]
        pos_tag = jTokken.get(getClassAnnotation('PartOfSpeechAnnotation')) if not pos_tags else pos_tags[i]
        lemm = get_base_form_for_word(word, language, pos_tag)
        jTokken.set(getClassAnnotation('LemmaAnnotation'), lemm)


def annotation(data, language, settings):
    text = None
    if language in STANFORD_PREPOSSESSING:
        annotation = annotation_stanford(data, language, {})
    else:
        annotation = annotation_polyglot(data, language)

    if 'normal_form' in settings and settings['normal_form']:
        settings['part_of_speech'] = True

    if 'part_of_speech' in settings and settings['part_of_speech']:
        pos_anotate = getPOSTaggerAnnotator(language)
        if pos_anotate:
            pos_anotate.annotate(annotation)
        else:
            text = Text(data, language)
            polyglot_posttag(annotation, language, text, data)

    if 'normal_form' in settings and settings['normal_form']:
        if language == 'en':
            getMorphAnnotator(language).annotate(annotation)
        else:
            if text:
                polyglot_lemm(annotation, language, text)
            else:
                polyglot_lemm(annotation, language)

    return annotation

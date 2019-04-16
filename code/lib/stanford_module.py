
import os

from polyglot.decorators import memoize


#from nlp.config import STANFORD, JAVA_CONFIG, STANFORD_PREPOSSESSING, MARY_TTS
#import tools
from lib import tools
from lib.text import Text
from lib.linguistic_functions import get_base_form_for_word, pattern_language, tag
#from speech_to_text.config import SPHINX

import jnius_config

STANFORD = dict(
    # languages=['en', 'zh', 'de', 'es', 'fr', 'ar'],
    # # languages=[],
    crf_english_3class='../stanford_corenlp/classifiers/english.all.3class.distsim.crf.ser.gz',
    crf_english_4class='../stanford_corenlp/classifiers/english.conll.4class.distsim.crf.ser.gz',
    crf_english_7class='../stanford_corenlp/classifiers/english.muc.7class.distsim.crf.ser.gz',
    crf_chinese_7class='../stanford_corenlp/classifiers/chinese.misc.distsim.crf.ser.gz',
    crf_german_7class='../stanford_corenlp/classifiers/german.conll.hgc_175m_600.crf.ser.gz',
    crf_spanish_4class='../stanford_corenlp/classifiers/spanish.ancora.distsim.s512.crf.ser.gz',
    crf_france_3class='../stanford_corenlp/classifiers/france.3class.crf.ser.gz',
    # path_stanford_ner='./stanford_corenlp/stanford-corenlp-3.8.0.jar',
    path_stanford_ner='../stanford_corenlp/stanford_update.jar',
)

STANDFORD_PACKAGE = {
    'en': [
        'crf_english_3class',
        'crf_english_4class',
        'crf_english_7class'
    ],
    'es': ['crf_spanish_4class'],
    'zh': ['crf_chinese_7class'],
    'de': ['crf_german_7class'],
    'fr': ['crf_france_3class'],
    'ar': []
}

STANFORD_PREPOSSESSING = dict(
    en={
        'pos.model': '../stanford_corenlp/pos-tagger/english-left3words-distsim.tagger',
        'tokenize.language': 'en',
        'tokenize.options': 'untokenizable=allKeep, invertible=true'
    },
    fr={
        'pos.model': '../stanford_corenlp/pos-tagger/french.tagger',
        'tokenize.language': 'fr',
        'tokenize.options': 'untokenizable=allKeep, invertible=true'
    },
    zh={
        'pos.model': '../stanford_corenlp/pos-tagger/chinese-distsim.tagger',
        'tokenize.language': 'zh',
        'ssplit.boundaryTokenRegex': '\x5B\x2E\xE3\x80\x82\x5D\x7C\x5B\x21\x3F\xEF\xBC\x81\xEF\xBC\x9F\x5D\x2B',
        'ner.language': 'chinese',
        'ner.applyNumericClassifiers': 'true',
        'segment.sighanPostProcessing': 'true',
        'segment.sighanCorporaDict': '../stanford_corenlp/ch_model/segmenter/chinese',
        'segment.serDictionary': '../stanford_corenlp/ch_model/segmenter/chinese/dict-chris6.ser.gz',
        'segment.model': '../stanford_corenlp/ch_model/segmenter/chinese/ctb.gz',
    },
    de={
        'pos.model': '../stanford_corenlp/pos-tagger/german-hgc.tagger',
        'tokenize.language': 'de',
        'ner.applyNumericClassifiers': 'false',
        'tokenize.options': 'untokenizable=allKeep, invertible=true'
    },
    es={
        'pos.model': '../stanford_corenlp/pos-tagger/spanish-distsim.tagger',
        'tokenize.language': 'es',
        'tokenize.options': 'untokenizable=allKeep, invertible=true'
    },
    ar={
        'tokenize.language': 'ar',
        'segment.model': '../stanford_corenlp/ar_model/segmenter/arabic/arabic-segmenter-atb+bn+arztrain.ser.gz',
        'ssplit.boundaryTokenRegex': '[.]|[!?]+|[!\u061F]+',
        'pos.model': '../stanford_corenlp/ar_model/pos-tagger/arabic/arabic.tagger'
    }
)

JAVA_CONFIG = dict(
    #max_size='300000m',
    max_size='4096m',
    default_config_crf=dict(
        useClassFeature='true',
        useWord='true',
        useNGrams='true',
        noMidNGrams='true',
        maxNGramLeng=6,
        usePrev='true',
        useNext='true',
        useSequences='true',
        usePrevSequences='true',
        useTypeSeqs='true',
        useTypeSeqs2='true',
        useTypeySequences='true',
        wordShape='chris2useLC',
        useDisjunctive='true'
    ),
    fixed_config_crf=dict(
        map='word=0,answer=1',
        qnSize=10,
        saveFeatureIndexToDisk='true',
        maxLeft=1,
        featureDiffThresh=0.05
    ),
    default_config_cdc={
        "1.minNGramLeng": 1,
        "intern": "true",
        "1.binnedLengths": "10, 20, 30",
        "QNsize": 15,
        "useQN": "true",
        "useClassFeature": "true",
        "1.maxNGramLeng": 4,
        "sigma": 3,
        "printClassifierParam": 200,
        "1.usePrefixSuffixNGrams": "true",
        "1.seNGrams": "true",
        "tolerance": 0.0001,
    },
    fixed_config_cdc={
        "goldAnswerColumn": 0,
        "displayedColumn": 1,
    }
)


jnius_config.add_options('-Xrs', '-Xmx{0}'.format(JAVA_CONFIG['max_size']))
#jnius_config.add_classpath(tools.get_abs_path(SPHINX['path_sphinx']))
#jnius_config.add_classpath(tools.get_abs_path(STANFORD['path_stanford_ner']))
jnius_config.add_classpath(STANFORD['path_stanford_ner'])
#jnius_config.add_classpath(tools.get_abs_path(MARY_TTS['path_mary_tts']))

@memoize
def GetJavaClass(name_class):
    #os.environ['CLASSPATH'] = tools.get_abs_path(STANFORD['path_stanford_ner'])
    os.environ['CLASSPATH'] = STANFORD['path_stanford_ner']
    from jnius import autoclass
    return autoclass(name_class)


PropertiesFile = GetJavaClass('edu.stanford.nlp.util.StringUtils').propFileToProperties
ClassifierFlags = GetJavaClass('edu.stanford.nlp.sequences.SeqClassifierFlags')
CRFClassifier = GetJavaClass('edu.stanford.nlp.ie.crf.CRFClassifier')
ColumnDataClassifier = GetJavaClass('edu.stanford.nlp.classify.ColumnDataClassifier')
jMap = GetJavaClass('java.util.HashMap')
SystemJava = GetJavaClass('java.lang.System')
TokenizerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.TokenizerAnnotator')
WordsToSentencesAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.WordsToSentencesAnnotator')
POSTaggerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.POSTaggerAnnotator')
NERCombinerAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.NERCombinerAnnotator')
MorphAnnotator = GetJavaClass('edu.stanford.nlp.pipeline.MorphaAnnotator')
jInteger = GetJavaClass('java.lang.Integer')
jString = GetJavaClass('java.lang.String')
Annotation = GetJavaClass('edu.stanford.nlp.pipeline.Annotation')


def to_prop(prop):
    properties = GetJavaClass('java.util.Properties')()
    for key in prop:
        if "=" in prop[key]:
            for prop_splited in prop[key].split(","):
                ps = prop_splited.split("=")
                prop_splited_key = ps[0]
                prop_splited_value = ps[1]
                properties.setProperty(prop_splited_key, prop_splited_value)
        else:
            properties.setProperty(key, prop[key])
    return properties


def annotation_polyglot(data, language, settings={}):
    # map_setting = {
    #     'part_of_speech': getPOSTaggerAnnotator
    # }
    text = Text(data, language)
    text_row = text.raw
    text_row = text_row if isinstance(text_row, str) \
        else text_row.encode('utf-8')
    jannotation = Annotation(text_row)
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
    result = GetJavaClass('java.util.ArrayList')()
    end_pos = 0
    index = 1
    core_label = None
    sentence = sentence #if isinstance(sentence, unicode) else sentence.decode('utf8')
    for tok in tokens:
        tok = tok #if isinstance(tok, unicode) else tok.decode('utf8')
        start_pos = sentence.find(tok, end_pos)
        before = sentence[end_pos: start_pos]
        if core_label:
            core_label.setAfter(before)
        end_pos = start_pos + len(tok)
        core_label = getCoreLabel(tok.encode('utf-8'), start_pos + from_pos, end_pos + from_pos - 1)
        core_label.setBefore(before)
        if index_sentence:
            #core_label.setSentIndex(jInteger(index_sentence))
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
        return POSTaggerAnnotator('pos', prop_an)
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


def annotation_stanford(data, language, settings={}):
    '''
    :param data:
    :param language:
    :param settings:
    :return:
    '''
    map_setting = {
        'part_of_speech': getPOSTaggerAnnotator,
    }
    annotation = Annotation(data)
    getTokenizerAnnotator(language).annotate(annotation)
    getWordsToSentencesAnnotator(language).annotate(annotation)
    # getPOSTaggerAnnotator(language).annotate(annotation)
    for key in map_setting:
        if key in settings and settings[key]:
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
        if isinstance(word, str):
            word = word.decode('utf-8')
        if word == tags[i][0]:
            tag_pos = tags[i][1]
            if isinstance(tag_pos, str):
                tag_pos = tag_pos.decode('utf-8')
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
        annotation = annotation_stanford(data, language)
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

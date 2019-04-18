POLIGLOT = dict(
    path_polyglot_data='../polyglot_data',
)

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


stanford_models = [
    {
        'model': 'crf_english_3class',
        'tags': ['ORGANIZATION', 'LOCATION', 'PERSON'],
        'language': 'en',
        'name': 'Detects'
    },
    {
        'model': 'crf_english_4class',
        'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'MISC'],
        'language': 'en',
        'name': 'Detects'
    },
    {
        'model': 'crf_english_7class',
        'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'DATE', 'MONEY', 'PERCENT', 'TIME'],
        'language': 'en',
        'name': 'Detects'
    },
    {
        'model': 'crf_chinese_7class',
        'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'FACILITY', 'DEMONYM', 'MISC', 'GPE'],
        'language': 'zh',
        'name': ''
    },
    {
        'model': 'crf_german_7class',
        'tags': ['I-MISC', 'B-LOC', 'I-PER', 'I-LOC', 'B-MISC', 'I-ORG', 'B-ORG', 'B-PER'],
        'language': 'de',
        'name': 'Erkennt'
    },
    {
        'model': 'crf_spanish_4class',
        'tags': ['OTROS', 'PERS', 'ORG', 'LUG'],
        'language': 'es',
        'name': 'Detecta'
    },
    {
        'model': 'crf_france_3class',
        'tags': ['I-ORG', 'I-PERS', 'I-LIEU'],
        'language': 'fr',
        'name': '\x44\xC3\xA9\x74\x65\x72\x6D\x69\x6E\x65\x20\x6C\x65\x73'
    }
]

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

description_tag = {
    'ORGANIZATION': 'Trained model of CRF, defining organizations',
    'LOCATION': 'Trained model of CRF, defining places',
    'PERSON': 'Trained model of CRF, defining personality',
    'DATE': 'Trained model of CRF, defining the dates',
    'MONEY': 'Trained model of CRF, defining finances',
    'PERCENT': 'Trained model of CRF, defining personality',
    'TIME': 'Trained model of CRF, defining dates',
    'MISC': 'Trained model of CRF, defining misc data',
    'FACILITY': 'Trained model of CRF, defining objects',
    'DEMONYM': 'Trained model of CRF, defining ethnicity',
    'GPE': 'Trained model of CRF, defining geographical and political entity, a location which has a government, like U.S.A. or New York',
    'I-MISC': 'Trained model of CRF, defining misc data (inside entity)',
    'B-LOC': 'Trained model of CRF, defining places (begin entity)',
    'I-PER': 'Trained model of CRF, defining personality (inside entity)',
    'B-PER': 'Trained model of CRF, defining personality (begin entity)',
    'I-LOC': 'Trained model of CRF, defining places(inside entity)',
    'B-MISC': 'Trained model of CRF, defining misc data (begin entity)',
    'I-ORG': 'Trained model of CRF, defining organizations (inside entity)',
    'B-ORG': 'Trained model of CRF, defining organizations (begin entity)',
    'OTROS': 'Trained model of CRF, defining misc data',
    'PERS': 'Trained model of CRF, defining personality',
    'ORG': 'Trained model of CRF, defining organizations',
    'LUG': 'Trained model of CRF, defining places',
    'I-PERS': 'Trained model of CRF, defining personality',
    'I-LIEU': 'Trained model of CRF, defining places'
}


MONGO = dict(
    mongo_host='mongodb://localhost',
    database='newsAPI',
    article_collection='article',
)

"""Improved polyglot.text module"""
import string

from polyglot.decorators import cached_property
from polyglot.base import Sequence
from polyglot.tokenize import SentenceTokenizer
from polyglot.text import BaseBlob, WordList


class Sentence(BaseBlob):
    """A sentence within a Text object. Inherits from :class:`BaseBlob <BaseBlob>`.
    :param sentence: A string, the raw sentence.
    :param start_index: An int, the index where this sentence begins
                        in Text. If not given, defaults to 0.
    :param end_index: An int, the index where this sentence ends in
                        a Text. If not given, defaults to the
                        length of the sentence - 1.
    """

    def __init__(self, sentence, start_index=0, end_index=None, hint_language_code=None):
        super(Sentence, self).__init__(sentence)
        #: The start index within a Text
        self.start = start_index
        #: The end index within a Text
        self.end = end_index or len(sentence) - 1
        self.hint_language_code = hint_language_code

    @property
    def dict(self):
        '''The dict representation of this sentence.'''
        return {
            'raw': self.raw,
            'start': self.start,
            'end': self.end,
            'entities': [(e.tag, e) for e in self.entities],
            'tokens': self.tokens,
            'words': self.words,
            'pos_tags': self.pos_tags,
            'language': self.language.code,
            # TODO: 'polarity': self.polarity,
        }

    @cached_property
    def polarity(self):
        """Return the polarity score as a float within the range [-1.0, 1.0]
        """
        scores = [w.polarity for w in self.words if w.polarity != 0]
        return sum(scores) / float(len(scores)) if len(scores) > 0 else 0.


class Text(BaseBlob):
    """.
    """

    def __init__(self, text, hint_language_code=None, split_apostrophe=False):
        super(Text, self).__init__(text)

        self.hint_language_code = hint_language_code
        self.split_apostrophe = split_apostrophe

    def __str__(self):
        if len(self.raw) > 1000:
            return u"{}...{}".format(self.raw[:500], self.raw[-500:])
        else:
            return self.raw

    @property
    def sentences(self):
        """Return list of :class:`Sentence <Sentence>` objects."""
        return self._create_sentence_objects()

    @property
    def raw_sentences(self):
        """List of strings, the raw sentences in the blob."""
        return [sentence.raw for sentence in self.sentences]

    @property
    def serialized(self):
        """Returns a list of each sentence's dict representation."""
        return [sentence.dict for sentence in self.sentences]

    def to_json(self, *args, **kwargs):
        '''Return a json representation (str) of this blob.
        Takes the same arguments as json.dumps.
        .. versionadded:: 0.5.1
        '''
        try:
            import ujson as json
        except ImportError:
            import json
        return json.dumps(self.serialized, *args, **kwargs)

    @property
    def json(self):
        '''The json representation of this blob.
        .. versionchanged:: 0.5.1
            Made ``json`` a property instead of a method to restore backwards
            compatibility that was broken after version 0.4.0.
        '''
        return self.to_json()

    def _create_sentence_objects(self):
        '''Returns a list of Sentence objects from the raw text.
        '''
        sentence_objects = []
        sent_tokenizer = SentenceTokenizer(locale=self.language.code)
        seq = Sequence(self.raw)
        seq = sent_tokenizer.transform(seq)
        for start_index, end_index in zip(seq.idx[:-1], seq.idx[1:]):
            # Sentences share the same models as their parent blob
            sent = seq.text[start_index: end_index].strip()
            if not sent:
                continue
            s = Sentence(sent, start_index=start_index, end_index=end_index, hint_language_code=self.hint_language_code)
            # s.detected_languages = self.detected_languages
            sentence_objects.append(s)
        return sentence_objects

    @cached_property
    def polarity(self):
        """Return the polarity score as a float within the range [-1.0, 1.0]
        """
        scores = [w.polarity for w in self.words if w.polarity != 0]
        return sum(scores) / float(len(scores)) if len(scores) > 0 else 0.

    @property
    def words(self):
        """Return a list of word tokens. This excludes punctuation characters.
        If you want to include punctuation characters, access the ``tokens``
        property.
        :returns: A :class:`WordList <WordList>` of word tokens.
        """
        return self.tokens

    @cached_property
    def tokens(self):
        """Return a list of tokens, using this blob's tokenizer object
        (defaults to :class:`WordTokenizer <textblob.tokenizers.WordTokenizer>`).
        """
        seq = self.word_tokenizer.transform(Sequence(self.raw))
        tokens = WordList(seq.tokens(), parent=self, language=self.language.code)

        fix_hyphen = []
        i = 0
        while i < len(tokens):
            hyphen_word = ''
            while i + 3 < len(tokens) and tokens[i+1] == '-' and tokens[i+2] not in string.punctuation:
                if tokens[i+3] == '-':
                    hyphen_word += tokens[i] + tokens[i+1]
                    i += 2
                    if i + 2 < len(tokens):
                        if tokens[i+1] == '-' and tokens[i+2] not in string.punctuation:
                            hyphen_word += tokens[i] + tokens[i + 1] + tokens[i+2]
                            i+=3
                            if tokens[i] != '-':
                                break
                else:
                    hyphen_word += tokens[i] + tokens[i + 1] + tokens[i + 2]
                    i += 3
                    if tokens[i] != '-':
                        break
            if hyphen_word:
                fix_hyphen.append(hyphen_word)
                continue
            else:
                if i + 2 < len(tokens):
                    if tokens[i] not in string.punctuation and tokens[i+1] == '-' and tokens[i+2] not in string.punctuation:
                            fix_hyphen.append(tokens[i]+tokens[i+1]+tokens[i+2])
                            i += 3
                            continue
            fix_hyphen.append(tokens[i])
            i+=1

        if self.split_apostrophe:
            fix_apostrophe = []
            for token in fix_hyphen:
                if '\'' in token:
                    split = token.split('\'')
                    for i, t in enumerate(split):
                        fix_apostrophe.append(t)
                        if i != len(split) - 1:
                            fix_apostrophe.append('\'')
                else:
                    fix_apostrophe.append(token)
            return WordList(fix_apostrophe, parent=self, language=self.language.code)
        else:
            return WordList(fix_hyphen, parent=self, language=self.language.code)


if __name__ == '__main__':
    print(Text('mother-in-law trade-in car to ').words)

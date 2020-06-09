import re

SENTENCE_AGGREGATOR = " "
LEN_SENTENCE_AGGR = len(SENTENCE_AGGREGATOR)


def _make_regex_with_escapes(escapers):
    words_regex = r'{}[^_\W]+{}'

    temp_regexes = []
    for escaper_pair in escapers:
        (start, end) = escaper_pair
        temp_regexes.append(words_regex.format(start, end))

    return r"|".join(temp_regexes)


def shallow_word_segment(phrase, escape_pairs=None):
    """ Takes in a string phrase and segments it into words based on simple regex

    Args:
        phrase (str): phrase to be segmented to words
        escape_pairs ([(str, str)]): list of tuples where each tuple is a pair of substrings that should not be
                    used as word seperators. The motivation is to escapte special tags such as [HESITATION], ~SILENCE~
                    IMPORTANT: Row regex has to be used when definng escapte pairs
                        ("[", "]") will not work as [] are special chars in regex. Instead ("\[", "\]")

    Returns:
        ([str]): list of words extracted from the phrase
    """
    if escape_pairs is None:
        escape_pairs = []

    escape_pairs.append(("", ""))

    _regex = _make_regex_with_escapes(escape_pairs)
    return re.findall(_regex, phrase, flags=re.UNICODE)


def _segment_sentences(text):
    """segments a text into a set of sentences

    Args:
        text:

    Returns:

    """
    import en_core_web_sm
    nlp = en_core_web_sm.load()

    text_sentences = nlp(text)

    for sentence in text_sentences.sents:
        yield sentence.text


def partition_text(text, max_size):
    """takes a text string and creates a list of substrings that are shorter than a given length

    Args:
        text (str): text to be partitioned (usually a lecture transcript)
        max_size (int): maximum number of characters one partition should contain

    Returns:
        chunks([str]): list of sub strings where each substring is shorter than the given length
    """
    # get sentences
    sentences = _segment_sentences(text)

    chunks = []

    temp_sents = []
    temp_len = 0
    for sentence in sentences:
        len_sentence = len(sentence)
        expected_len = temp_len + LEN_SENTENCE_AGGR + len_sentence  # estimate length cost
        if expected_len > max_size:  # if it goes above threshold,
            if len(temp_sents) > 0:
                chunks.append(SENTENCE_AGGREGATOR.join(temp_sents))  # first load the preceding chunk
                temp_sents = []
                temp_len = 0

        temp_sents.append(sentence)  # then aggregate the sentence to the temp chunk
        temp_len += len_sentence

    if len(temp_sents) > 0:
        chunks.append(SENTENCE_AGGREGATOR.join(temp_sents))  # send the remainder chunk

    return chunks

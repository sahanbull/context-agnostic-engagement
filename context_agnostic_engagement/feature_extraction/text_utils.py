SENTENCE_AGGREGATOR = " "
LEN_SENTENCE_AGGR = len(SENTENCE_AGGREGATOR)


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

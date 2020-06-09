from collections import defaultdict

from context_agnostic_engagement.feature_extraction._api_utils import wikify
from context_agnostic_engagement.feature_extraction._text_utils import partition_text

# values for Doc Frequency and Words to Ignore, more details about these variables
# found at: http://www.wikifier.org/info.html
DF_IGNORE_VAL = 50
WORDS_IGNORE_VAL = 50


def get_wikipedia_topic_features(text, api_key, chunk_size=5000):
    """ get Wikification for the transcript using http://www.wikifier.org

    Args:
        text (str): text that needs to be Wikified
        api_key (str): API key for Wikifier obtained from http://www.wikifier.org/register.html
        chunk_size (int): maximum number of characters that need included in each Wikified fragment.

    Returns:
        enrichments ([{str: val}]): list of annotated chunks from the transcript

    """
    text_partitions = partition_text(text, max_size=chunk_size)

    enrichments = []
    i = 1
    for text_part in text_partitions:
        temp_record = {}
        annotations = wikify(text_part, api_key, DF_IGNORE_VAL, WORDS_IGNORE_VAL)
        temp_record["part"] = i
        temp_record["text"] = text_part
        temp_record["annotations"] = annotations
        enrichments.append(temp_record)
        i += 1

    return enrichments


def get_ranked_topics(chunks, option, top_n):
    """ ranks the topics using the aggregated score across multiple Wikified chunks of the text.

    Args:
        chunks ([{str: val}]): list of Wikified chunks for the transcript
        option {str}: pageRank or cosine
        top_n (int): n top ranked topics of interest

    Returns:
        final_rec ({str:val}): dict with key for top_n_url or top_n_value and the URL or value of the topic

    """
    chunks = list(chunks)

    total_length = sum([len(part["text"]) for part in chunks])

    records = defaultdict(list)
    for part in chunks:
        annotations = part["annotations"]["annotation_data"]
        weight = len(part["text"])
        norm = weight / total_length
        for concept in annotations:
            url = concept["url"]
            val = concept.get(option, 0.)
            records[url].append(val * norm)

    rec = [(title, sum(val)) for title, val in records.items()]

    # sort by normalised weight
    rec.sort(key=lambda l: l[1], reverse=True)
    n_recs = rec[:top_n]

    final_rec = {}
    for idx, item in enumerate(n_recs):
        url, val = item
        _idx = idx + 1
        final_rec["topic_{}_{}_url".format(_idx, option)] = url
        final_rec["topic_{}_{}_val".format(_idx, option)] = val

    return final_rec


def get_authority_wiki_features(text, api_key, top_n):
    """ returns top-n most authoritative Wikipedia topics with PageRank scores.
    Calculated using http://www.wikifier.org/

    Args:
        text (str): text that needs to be Wikified for authority
        api_key (str): API key for Wikifier obtained from http://www.wikifier.org/register.html
        top_n (int): n top ranking topics to be returned with PageRank scores

    Returns:
        ranked_topic_records ({str:val}): dict with key for top_n_url or top_n_value and the URL or value of the topic

    """
    enriched_chunks = get_wikipedia_topic_features(text, api_key)
    ranked_topic_records = get_ranked_topics(enriched_chunks, "pageRank", top_n)

    return ranked_topic_records


def get_coverage_wiki_features(text, api_key, top_n):
    """ returns top-n most covered Wikipedia topics with cosine similarity scores.
    Calculated using http://www.wikifier.org/

    Args:
        text (str): text that needs to be Wikified for coverage
        api_key (str): API key for Wikifier obtained from http://www.wikifier.org/register.html
        top_n (int): n top ranking topics to be returned with cosine scores

    Returns:
        ranked_topic_records ({str:val}): dict with key for top_n_url or top_n_value and the URL or value of the topic

    """
    enriched_chunks = get_wikipedia_topic_features(text, api_key)
    ranked_topic_records = get_ranked_topics(enriched_chunks, "cosine", top_n)

    return ranked_topic_records

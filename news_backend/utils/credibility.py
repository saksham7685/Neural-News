import re
import requests
from textstat import text_standard

SOURCE_CREDIBILITY = {
    "IndianExpress": 0.9,
    "Hindustantimes": 0.85,
}

def get_credibility_score(title, content, source):

    source_score = SOURCE_CREDIBILITY.get(source, 0.5)

    readability_score = text_standard(content, float_output=True) 
    normalized_readability_score = min(readability_score, 10) / 10 # clipping the score to 10
    
    credibility_score = (0.7 * source_score) + (0.3 * normalized_readability_score)
    credibility_score = min(credibility_score, 1.0)

    return round(credibility_score, 2)

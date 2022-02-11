import torch
import gensim
from transformers import pipeline
class Summery:

    def __init__(self):
        self.summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base")

    def summerize(self,article):
        text=self.summarizer(article,early_stopping=False, max_length=80, min_length=40, do_sample=False)
        result=text[0]['summary_text']
        return result




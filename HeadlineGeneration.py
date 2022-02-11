import torch


from gensim.summarization import summarize
from transformers import T5ForConditionalGeneration,T5Tokenizer

class Title_Generation:
    
    def __init__(self): 
        
        self.device = torch.device("cpu")
        self.model = T5ForConditionalGeneration.from_pretrained("Michau/t5-base-en-generate-headline")
        self.tokenizer = T5Tokenizer.from_pretrained("Michau/t5-base-en-generate-headline")
        self.model = self.model.to(self.device)
        
    def generate(self, article):
        
        text=article
        max_len = 256
        encoding = self.tokenizer.encode_plus(text, return_tensors = "pt")
        input_ids = encoding["input_ids"].to(self.device)
        attention_masks = encoding["attention_mask"].to(self.device)

        beam_outputs = self.model.generate(
            input_ids = input_ids,
            attention_mask = attention_masks,
            max_length = 64,
            num_beams = 3,
            early_stopping = True,
        )

        result = self.tokenizer.decode(beam_outputs[0])
        result=result[5:-4]
        return result

    def summerizer(self,original_text):
        short_summary = summarize(original_text)
        return short_summary

    def generate_title(self, article):
        text=self.summarizer(article, max_length=10, min_length=10, do_sample=False)
        result=text[0]['summary_text']
        return result

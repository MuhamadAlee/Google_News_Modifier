from styleformer import Styleformer
import torch
import warnings
warnings.filterwarnings("ignore")

class Plag:

    def __init__(self):
        self.sf0 = Styleformer(style = 0) 
        self.sf2 = Styleformer(style = 1) 
        

    def replag2(self,source_sentence):
        target_sentence = self.sf2.transfer(source_sentence)
        
        if target_sentence is None:
            target_sentence=source_sentence
        else:
            txt=self.replag0(target_sentence)
            if txt is not None:
                target_sentence=txt
        return target_sentence

    def replag0(self,source_sentence):
        target_sentence = self.sf0.transfer(source_sentence)
        
        if target_sentence is None:
            target_sentence=source_sentence
        return target_sentence
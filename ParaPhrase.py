import plagarism
import warnings
warnings.filterwarnings("ignore")

class Phrase:

  def __init__(self):
    self.plg=plagarism.Plag()
    

  def rephrase(self,input_text,num_return_sequences):
    output=self.plg.replag2(input_text)
    
   
    
    return output

    
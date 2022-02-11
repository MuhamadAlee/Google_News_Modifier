from GoogleNews import GoogleNews
from scrapper import ScrapNews
from googlesearch import search
from newspaper import Article
import ParaPhrase as phraser
from datetime import datetime
import time
import re
import warnings
import random
import dill
import os
import pandas as pd
from HeadlineGeneration import Title_Generation

warnings.filterwarnings("ignore")


class ArtGen:

    def __init__(self):
        #using modules
        self.pp=phraser.Phrase()
        
        self.googlenews = GoogleNews()
        self.scrap=ScrapNews()
        self.title_generation = Title_Generation()

    def sent_splitter(self,txt):
        sentences=txt.split('.')
        return sentences


    def url_removal(self,text):
        text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)
        return text 

    def time_comparison(self,times):
        timestamps=['sec','min','hour','day','week','month']
        flag=False
        last=""
        ind=-1
        for ts in timestamps:
            for index,date in enumerate(times):
                if (ts in date) or (ts+'s' in date):
                    val=int(date.split(' ')[0])
                    if (last=="") or (last>val):
                        flag=True
                        ind=index
                        last=val
            if (flag):
                break
        return ind

    def remove_emoji(self,string):
        emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    def reconcatenate(self,txt_list):
        paragraph=""
        for sentence in txt_list:
            paragraph+=sentence+". "
        return paragraph


    def text_rephraser(self,text):
        ARTICLE = ""
        sentences=self.sent_splitter(text)
        for sent in sentences:
            out=self.pp.rephrase(sent,1)
            ARTICLE+=out
        return ARTICLE
    
    def news_extraction(self,query,query_set):
        ARTICLE=""
        iteration_flag=True
        all_news=self.scrap.scrape(query)
        times=all_news['date']
        ind=self.time_comparison(times)
        query=all_news['title'][ind]
        news_headline=query    
        print("Blog is generated against: \n"+"*"*50+query+"*"*50)
        # URLs=search(query,  num_results=10, lang="en")
        URLs=search(query,  num=10, lang="en")
        if query in query_set:
            return "","",query_set
        else:
            query_set.add(query)

        for url in URLs:
            
            # if len(ARTICLE.split())>700:
            #     iteration_flag=False
            #     break
            try:
                print("-"*100)
                print(url)
                print("-"*100) 
                if(iteration_flag):
                    article = Article(url, language="en")
                    article.download()
                    article.parse()
                    article.nlp()

                    text=article.text
                    article_title = article.title


                    if len(text.split()) > 300:
                        iteration_flag = False
                    else:
                        continue
                    text=text.replace('?','.')
                    text=text.replace('"','')
                    text=self.url_removal(text)
                    text=self.remove_emoji(text)
                    ARTICLE=self.text_rephraser(text)

                else:
                    break
                    
            except:
                continue
                
        
        return article_title,ARTICLE,query_set


    def generate_blog(self,article, promo_content):
        splited_blog = article.split('.')
        total_lines = len(splited_blog)

        first_paragraph = ". ".join(splited_blog[:int(total_lines*.33)])
        second_paragraph =". ".join(splited_blog[int(total_lines*.33) : int(total_lines*.66)])
        third_paragraph = ". ".join(splited_blog[int(total_lines*.66) : ])
        
        first_paragraph_title = self.title_generation.generate(first_paragraph)+ ' : '
        second_paragraph_title = self.title_generation.generate(second_paragraph)+ ' : '
        third_paragraph_title = self.title_generation.generate(third_paragraph)+ ' : '

        blog = first_paragraph_title + '\n'+ first_paragraph + '\n' + second_paragraph_title +'\n'+ second_paragraph + '\n' + third_paragraph_title +'\n'+ third_paragraph + '\n'+'About Xana : '+'\n'+ promo_content
        return blog

    def get_data_list(sef,data):
        csv_data = data.split("’,’")
        csv_list = []
        for i in range(len(csv_data)):
            csv_list.append(csv_data[i].replace("’]", "").replace("[‘" ,""))
        return csv_list

    def save_file(self,head_block,text,query, promo_content, intro_query):
        now = datetime.now()
        fl_name = query+"_"+now.strftime("%d_%m_%Y_%H_%M_%S")+".txt"
        blog = self.generate_blog(text,promo_content)
        blog = blog + '\n' + 'For more info Please visit https://xana.net/' + '\n' + 'Follow us on twitter https://twitter.com/XANAMetaverse'
        processed_blog = head_block+"\n\n\n"+"Introduction : "+'\n' +intro_query+'\n'+blog

        f = open("blogs/"+fl_name, "w")
        f.write(processed_blog)
        f.close()
    

    def main_event(self, promo_content, intro_dict):
            
            query_words=["metaverse","nft","gamefi"]
            query_sets = {"metaverse":set(),"nft":set(),"gamefi":set()}
            while True:
                for word in query_words:
                        
                        query_set=query_sets[word]
                        try:
                            last=[word]
                            article=""
                            query, article, query_set =self.news_extraction(word,query_set)
                            if article=="":
                                continue
                            print(article)
                            if (article!=""):           
                                head_block=query
                                print("="*100)
                                print('Head : ', head_block)
                                print("Article : ", article)
                                print("Word : ", word)
                                print("Rephrased Promo : ", promo_content)
                                print("="*100)

                                intro_query = random.choice(intro_dict[word])
                                rephrased_intro_query = self.text_rephraser(intro_query)

                                print("="*100)
                                print("Intro Query : "+intro_query)
                                print("Rephrased Query : ", rephrased_intro_query)
                                print("="*100)
                                
                                self.save_file(head_block,article,word, promo_content, rephrased_intro_query)

                                print("Article is generated")

                        except Exception as e:
                            print(e)
                            continue    
                    
                    # script will rerun itself after evry 15 minutes
                print("___________________Waiting for next turn _______________________")
                time.sleep(15*6)  

#"""
if __name__ == '__main__':
    if not os.path.exists('ag.pickle'):
        ag=ArtGen()
        with open('ag.pickle','wb') as f:
            dill.dump(ag,f)
        # dill.dump(ag,open('ag.pickle','wb'))
    else:
        with open('ag.pickle', 'rb') as f:
            ag = dill.load(f)

        # ag=dill.load(open('ag.pickle','rb'))
    
    promo_content = "XANA is a layer-2 solution on Ethereum, custom-built for the metaverse. It is the next-gen metaverse where users can interact in virtual reality. They can create their avatars using NFTs and do business or participate in entertainment events in XANA World."
    promo_content = ag.text_rephraser(promo_content)
    intro_dict = { }

    # intro_df = pd.read_csv('metverse_gmeify_nft0.csv')
    # intro_dict['metaverse'] = ag.get_data_list(intro_df['description'][0])
    # intro_dict['gamefi'] = ag.get_data_list(intro_df['description'][1])
    # intro_dict['nft'] = ag.get_data_list(intro_df['description'][2])

    intro_dict['metaverse'] = ['A metaverse is a network of 3D   virtual worlds focused on social connection. In futurism and science fiction, the term is often described as a hypothetical iteration of the Internet as a single, universal virtual world that is facilitated by the use of virtual and augmented reality headsets']
    intro_dict['gamefi'] = ['GameFi — also known as “play-to-earn” — is the marriage of gaming and blockchain-powered financialization. Whether through quests, trading, or other mechanisms, GameFi allows gamers to earn digital assets for their in-game efforts. While traditional games have allowed players to accrue and trade digital assets for decades, they could lose their investment at any time if the publisher shut the game down or went out of business. GameFi games, on the other hand, keep their assets stored on a distributed network. These operate independently of any single organization, substantially derisking the digital assets.']
    intro_dict['nft'] = ["NFTs are tokens that we can use to represent ownership of unique items. They let us tokenise things like art, collectibles, even real estate. They can only have one official owner at a time and they're secured by the Ethereum blockchain – no one can modify the record of ownership or copy/paste a new NFT into existence.",
    "NFT stands for non-fungible token. Non-fungible is an economic term that you could use to describe things like your furniture, a song file, or your computer. These things are not interchangeable for other items because they have unique properties.Fungible items, on the other hand, can be exchanged because their value defines them rather than their unique properties. For example, ETH or dollars are fungible because 1 ETH / $1 USD is exchangeable for another 1 ETH / $1 USD"]
    ag.main_event(promo_content, intro_dict)
    

#"""

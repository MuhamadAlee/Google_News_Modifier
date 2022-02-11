from concurrent.futures import ProcessPoolExecutor as Task_Manager
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from nltk.tokenize import sent_tokenize
from GoogleNews import GoogleNews
from scrapper import ScrapNews
from googlesearch import search
from newspaper import Article
from bs4 import BeautifulSoup
import ParaPhrase as phraser
import Summerizer as summ
from datetime import datetime
import HeadlineGeneration
import uploading
import requests, lxml
import random
import string
import heapq
import time
import nltk
import re
import os
import dill
import warnings
import requests
import cv2
import pandas as pd
import numpy as np
import gc

warnings.filterwarnings("ignore")


class ArtGen:

    def __init__(self):
        #using modules
        self.pp=phraser.Phrase()
        self.sm=summ.Summery()
        self.googlenews = GoogleNews()
        self.scrap=ScrapNews()
        self.tg=HeadlineGeneration.Title_Generation()
        self.now = datetime.now()
       
    def __enter__(self):
        
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def sent_splitter(self,txt):
        sentences=txt.split('.')
        return sentences

    def news(self,query):
        all_news = {'title': [], 'link': [],'headline': [], 'date': []}
        self.googlenews.search(query)
        results=self.googlenews.results(sort=True)
        all_times=[]
        for news in results:
            all_times.append(news["date"])
        least_index=self.time_comparison(all_times)
        news=results[least_index]
        all_news['title'].append(news["title"])
        all_news['link'].append(news["link"])
        all_news['headline'].append(news["desc"])
        all_news['date'].append(news["date"])
            
        return all_news

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

    def url_removal(self,text):
        text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)
        return text 

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

    def image_save(self,link):
        f_name = 'images/image.jpg'
        try:
            url = link
            page = requests.get(url)
            with open(f_name, 'wb') as f:
                f.write(page.content)
            img=cv2.imread(f_name)
            cv2.imwrite(f_name,img)
        except:
            img = np.zeros((512,512,3), np.uint8)
            cv2.imwrite(f_name,img)

    def news_extraction(self,last,query,all_news,ind):
        news_headline=""
        news_url=""
        ARTICLE=""
        image_flag=True

        
        # all_news=self.scrap.scrape(query)
        

        
        while image_flag:
            
            if(len(all_news['date'])==0):
                print("Sorry article will be generated after 15 minutes")
                image_flag=False
                query=""
                ARTICLE=""
                news_headline=""
                news_url=""
                break
                

            times=all_news['date']
            # ind=self.time_comparison(times)
            
            query=all_news['title'][ind]
            
            print("News is generated against: \n"+"*"*50+query+"*"*50)
            news_headline=query
            # URLs=search(query,  num_results=10, lang="en")
            URLs=[all_news['link'][ind]]
            iteration_flag=True
            if query in last:
                print("Sorry latest Article is already generated")
                image_flag=False
                query=""
                ARTICLE=""
                news_headline=""
                news_url=""
                break
            
            for url in URLs:
                try:
                    if(iteration_flag):
                        article = Article(url, language="en")
                        article.download()
                        article.parse()
                        article.nlp()
                        
                        text=article.text
                        text=text.replace('?','.')
                        text=text.replace('"','')
                        text=self.url_removal(text)
                        text=self.remove_emoji(text)
                        sentences=self.sent_splitter(text)
                        
                        for sent in sentences:
                            out=self.pp.rephrase(sent,1)
                            ARTICLE+=out
                        
                        image_link=article.top_image
                        if (len(image_link)>1):
                            self.image_save(image_link)
                            if len(ARTICLE)>100:
                                image_flag=False
                                news_url=url
                                break
                            else:
                                ARTICLE=""

                        if(len(Article)<100):
                            ARTICLE=""
                            query=""
                            news_headline=""
                            news_url=""
                            image_flag=False
                            break


                except Exception as ex:
                    print(ex)
                    image_flag=False
                    break
                    
        
        return ARTICLE,query,news_headline,news_url

    def save(self,name,content):
        f = open(name, "w")
        f.write(content)
        f.close()

    def header(self,article):
        try:
            head_block=self.tg.generate(article)
        except:
            head_block="<unk>"
        return head_block
    

    def save_logs(self,category,headline,url,tweet):
        df=pd.read_csv("logs/"+category+".csv")
        data={"Headline":headline,"Url":url,"Tweet":tweet}
        df = df.append(data, ignore_index = True)
        df.to_csv("logs/"+category+".csv",index=False)

    def clear_logs(self,lst):
        for category in lst:
            if(os.path.exists("logs/"+category+".csv")):
                os.remove("logs/"+category+".csv")
            temporary_lst_headline=[" "]
            temporary_lst_url=[" "]
            temporary_lst_tweet=[" "]
            df=pd.DataFrame(list(zip(temporary_lst_headline, temporary_lst_url, temporary_lst_tweet)),
              columns=['Headline','Url', 'Tweet'])
            df.to_csv("logs/"+category+".csv",index=False)

    def para_maker(self, article):
        art_lst=[]
        article=self.sent_splitter(article)
        # article=article[:-1]
        length=round(len(article)/5)
        for i in range(5):
            start=length*i
            end=start+length
            art_lst.append(". ".join(article[start:end]))
        return art_lst


    def main_event(self):
        
            
            query_words=["gamefi","metaverse","nft"]
            last_links={  "gamefi":[],"metaverse":[],"nft":[]}
            self.clear_logs(query_words)
            while True:
                my_counter=0
                for word in query_words:
                    last=last_links[word]
                    if len(last)>=3:
                        my_counter+=1
                if my_counter==3:
                    print("********** THE DONE **********")
                    break

                for word in query_words:
                    try:
                        last=last_links[word]
                        if len(last)>=3:
                            print("-------------passed-------------")
                            continue

                        all_news=self.scrap.scrape(word,1)

                        if len(all_news['title'])<=3:
                            all_news=self.scrap.scrape(word,0)
                    

                
                        
                        ind=0
                        while True:
                            if len(last)>=3 or (len(all_news['title'])-1)==ind:
                                break
                            
                            article,query,headline,url=self.news_extraction(last,word,all_news,ind)
                            if (article=="") or (len(article)<100) :
                                ind+=1
                                continue

                            art_lst=self.para_maker(article)
                            print("--------------------------------------------------------------------")
                            article=""
                            for line in art_lst:
                                art_line=self.sm.summerize(line)
                                art_line=self.sent_splitter(art_line)
                                art_line=self.reconcatenate(art_line[:-1])
                                article+=art_line
                            
                            
                                
                            if (query not in last) and (query is not ""):


                                tweet=self.sm.summerize(article)
                                tweets=self.sent_splitter(tweet)
                                tweet=self.reconcatenate(tweets[:-1])
                                if (". . . ." in article) or ("sarah safina" in tweet):
                                    ind+=1
                                    continue

                                print("--------------------------------------------------------------------")
                                print("*"*50,query+"\n\n\n"+article+"\n\n\n"+tweet,"*"*50)

                                        
                                # head_block=self.header(article)
                                img_block="image.jpg"
                                
                                head_block=query

                                self.up=uploading.Upload()
                                self.up.login()
                                success=self.up.create_blog(head_block,article,img_block,word)
                                
                                
                                if(success):
                                    self.save_logs(word,head_block,url,tweet)
                                    if len(last)==10:
                                        last.pop(0)
                                    last.append(query)
                                    print("Article is generated")

                            ind +=1

                    except Exception as e:
                        print(e)
                        continue    
                
                # script will rerun itself after evry 15 minutes
                print("___________________Waiting for next turn _______________________")
                time.sleep(60)  




def every_day_task():
    if(os.path.exists("objects/ags.pickle")):
        with dill.load(open("objects/ags.pickle", "rb")) as ag:
            
            ag.main_event()
            
    else:
        with dill.load(open("objects/ags.pickle", "rb")) as ag:
            dill.dump(ag, file = open("objects/ags.pickle", "wb"))

            ag.main_event()


def job():
    with Task_Manager(max_workers=1) as executor:
        result = executor.submit(every_day_task).result()

if __name__ == '__main__':
    trigger = OrTrigger([CronTrigger(hour=8, minute=15, day_of_week=' Mon, Tue, WED, THU, FRI')])
    scheduler = BlockingScheduler()
    scheduler.add_job(job, trigger)
    scheduler.start()
    





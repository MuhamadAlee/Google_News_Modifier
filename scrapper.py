from bs4 import BeautifulSoup
import requests, urllib.parse, lxml

class ScrapNews():

    def __init__(self):
      pass
    def scrape(self,query,turner=0):
        all_news={'title': [],'date': [],'link': []}
        if turner==0:
            li_url="https://www.google.com/search?q="+query+"&tbm=nws&sxsrf=AOaemvJ3xg4cdnrpZwy6USE5NEAN4oDFNw:1632813407467&source=lnt&tbs=sbd:1&sa=X&ved=2ahUKEwjuqIv5j6HzAhWyS_EDHS0zAr8QpwV6BAgBECk&biw=1853&bih=981&dpr=1"
        elif turner==1:
            li_url="https://www.google.com/search?q="+query+"&tbm=nws&sxsrf=APq-WBug40fogbRcEfWxBHu5FTKuMOJNUQ:1644390046442&source=lnt&tbs=qdr:h&sa=X&ved=2ahUKEwiN_tukhvL1AhVmyoUKHQ-WAJ0QpwV6BAgBEBI&biw=1920&bih=976&dpr=1"
        
        page=requests.get(li_url, timeout=20)
        soup=BeautifulSoup(page.text,'lxml')
        links=soup.find_all('a')
        
        for link in links:
            if ("/url?q=http" in link['href']):
                lks=link['href'].replace("/url?q=","")
                lk=lks.split("&")[0]
                if lk not in all_news["link"]:
                    all_news["link"].append(lk)

        Titles=soup.find_all('h3')
        for title in Titles:
            if (title.text is not None):
                all_news["title"].append(title.text)

        Dates=soup.find_all('span')
        for date in Dates[8:-6]:
            if ("ago" in date.text):
                all_news["date"].append(date.text)

        all_news["link"]=all_news["link"][:-2]
        return all_news

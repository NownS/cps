import requests
import csv
from bs4 import BeautifulSoup

def searchinsoup(soup_array, search):
    return int(str(soup_array).find(search))

class Scraper():
    def __init__(self) :
        self.url = "http://security.cau.ac.kr/board.htm?bbsid=news&ctg_cd=&skey=&keyword=&mode=list"
        self.newstitle = []
        self.newslink = []
        self.newssee = []
        self.newsdate = []
    
    def getpage(self, soup) :
        pages = soup.select(".btn")
        tmp = searchinsoup(pages[1], "page=")
        tmp2 = searchinsoup(pages[1], "<img")
        self.pagelen = int(str(pages[1])[tmp+5:tmp2-2])
    
    def getnews(self,cnt) :
        res = requests.get(self.url + "&page=" + str(cnt+1))

        if res.status_code != 200: 
            print("request error: ", res.status_code)
        
        html = res.content.decode('euc-kr')
        soup = BeautifulSoup(html, "html.parser")
        
        tmp = soup.find_all("div", class_ = "photoList")
        newslist = tmp[0].find_all("p")

        for n in newslist:
            self.newstitle.append(n.find('b').text)
            self.newslink.append("http://security.cau.ac.kr/board.htm" + n.find("a")['href'])
            self.newssee.append(n.find("span", title="조회수").text)
            self.newsdate.append(n.find("span", title="작성일").text)
        self.writeCSV(self.newstitle, self.newslink, self.newssee, self.newsdate, cnt)

    def writeCSV(self, title, link, see, date, cnt) :
        file = open("CAUISNEWS.csv", "a", newline="")
        
        wr = csv.writer(file)
        for i in range(len(title)) :
            wr.writerow([str(i+1 + cnt*9), title[i], link[i], see[i], date[i]])

        file.close

    def scrap_init(self) :
        file= open("CAUISNEWS.csv","w", newline = "")
        wr = csv.writer(file)
        wr.writerow(["No.", "Title", "URL", "View", "Date"])
        file.close



res = requests.get("""
http://security.cau.ac.kr/board.htm?bbsid=news&ctg_cd=&skey=&keyword=&mode=list&page=1
""")
if res.status_code != 200: 
    print("request error: ", res.status_code)
html = res.content.decode('euc-kr')
soup = BeautifulSoup(html, "html.parser")
scraper = Scraper()
scraper.getpage(soup)
scraper.scrap_init()
for i in range(scraper.pagelen):
    scraper.getnews(i)

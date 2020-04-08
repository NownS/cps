import requests
import csv
from bs4 import BeautifulSoup
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, uic


def searchinsoup(soup_array, search):
    return int(str(soup_array).find(search))



class Scraper(QObject):

    updated = pyqtSignal(int)

    def __init__(self, textBrowser) :
        super().__init__()
        self.url = "http://security.cau.ac.kr/board.htm?bbsid=news&ctg_cd=&skey=&keyword=&mode=list"
        self.newstitle = []
        self.newslink = []
        self.newsview = []
        self.newsdate = []
        self.textBrowser = textBrowser
    
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
            self.newsview.append(n.find("span", title="조회수").text)
            self.newsdate.append(n.find("span", title="작성일").text)
        self.writeCSV(self.newstitle, self.newslink, self.newsview, self.newsdate, cnt)

    def writeCSV(self, title, link, view, date, cnt) :
        file = open("CAUISNEWS.csv", "a", newline="")
        
        wr = csv.writer(file)
        for i in range(len(title)) :
            wr.writerow([str(i+1 + cnt*9), title[i], link[i], view[i], date[i]])
        file.close
        self.newstitle = []
        self.newslink = []
        self.newsview = []
        self.newsdate = []

    def scrap(self) :
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
        self.getpage(soup)
        for i in range(self.pagelen):
            self.getnews(i)
            self.textBrowser.append("{}번째 페이지 Done".format(i+1))
            self.updated.emit(int(((i+1)/self.pagelen)*100))

        

form_class = uic.loadUiType("CAUISNEWS.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #크롤러 클래스 가져오기
        self.crawler = Scraper(self.textBrowser)

        #Thread 적용
        self.thread = QThread()
        self.crawler.moveToThread(self.thread)
        self.thread.start()

        #push 버튼이랑 scrap 연동
        self.pushButton.clicked.connect(self.pushmyButton)

        #Window title
        self.setWindowTitle("CAU IS News Crawler")

        #progressBar
        self.crawler.updated.connect(self.progressBarValue)


    #Progress Bar Value 초기화
    def pushmyButton(self) :
        self.progressBarValue(0)
        self.crawler.scrap()


    def progressBarValue(self, value) :
        self.progressBar.setValue(value)

 
if __name__ == '__main__' :

    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
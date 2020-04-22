from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time

path = os.getcwd() + "/chromedriver"

driver = webdriver.Chrome(path)

try :
    driver.get("http://youtube.com")
    time.sleep(1)

    searchIndex = "LOL 매드무비"
    element = driver.find_element_by_tag_name("input")
    element.send_keys(searchIndex)
    driver.find_element_by_xpath("/html/body/ytd-app/div/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/button").click()
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    tags = soup.find_all("h3", class_ = "title-and-badge style-scope ytd-video-renderer")
    for i in tags:
        print(i.text)

finally :
    time.sleep(5)
    driver.quit()
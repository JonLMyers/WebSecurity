#!/usr/bin/python
import urllib
import socket
import BeautifulSoup
import re
import os
import threading

class Spider:
    def __init__(self, s):
        self.socket = s
        self.failed = []
        self.crawled = []

    def Union(self, p, q):
        for e in q:
            if e not in q:
                p.appen(e)
    
    def extractLinks(self, page):
        dom = parse(page).getroot()
        dom.make_links_absolute()
        links = dom.csselect('a')
        return [link.get('href') for link in links if link.get('href')]
    
    def Crawl(self, limit=float('inf')):
        toCrawl = [self.socket]
        while toCrawl and len(self.crawled) < limit:
            page = toCrawl.pop()
            if page not in self.crawled:
                try:
                    self.Union(toCrawl, self.extractLinks(page))
                except Exception as e:
                    print e
                    self.failed.append([page, e])
                    pass
        return self.crawled

def Connect(url):
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((url, port))
    return s

def ScrapeCsecWeb(s):
    request = "GET /programs/computing-security-bs HTTP/1.1\n"
    requestHost = "Host: www.rit.edu\n\n"
    fullResponse = ''
    i = 0;
    s.send(request + requestHost)

    while True:
        response = s.recv(2048)
        fullResponse = fullResponse + response
        if response == '':
            break

    s.close()

    soup = BeautifulSoup.BeautifulSoup(fullResponse)
    courses = soup.findAll('table')[0].tbody.findAll('tr')
    for course in courses:
        if i > 1 and len(course.findAll('td')) > 2:
            number = course.findAll('td')[0].contents
            name = course.findAll('td')[1].contents
            print str(number + name)
        i = i + 1

def DownloadImage(img2, i):
    image = ''
    s = Connect('www.rit.edu')
    request = "GET http://www.rit.edu" + img2 + " HTTP/1.1\n"
    requestHost = "Host: www.rit.edu\n\n"
    s.send(request + requestHost)
    
    while True:
        response = s.recv(2048)
        if len(response) < 1: break
        image = image + response
    
    s.close()

    pos = image.find("\r\n\r\n")
    image = image[pos + 4:]
    imgFile = "/home/soren/Github/WebSecurity/pictures/image" + str(i) + ".jpg"
    fhand = open(imgFile, 'w+')
    fhand.write(image)
    fhand.close()

def ScrapeCsecImages(s):
    request = "GET /gccis/computingsecurity/people HTTP/1.1\n"
    requestHost = "Host: www.rit.edu\n\n"
    imgList = []
    threads = []

    fullResponse = ''
    i = 1
    s.send(request + requestHost)

    while True:
        response = s.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response

    s.close()

    soup = BeautifulSoup.BeautifulSoup(fullResponse)
    imgs = soup.findAll("div", {"class":"staff-picture"})
    for img in imgs:
        imgList.append(str(img.findAll('img')[0].get('src')))
        
    for img2 in imgList:
        t = threading.Thread(target=DownloadImage, args=(img2, i))
        threads.append(t)
        t.start()
        i += 1

def FullWebCrawl():
    print 'Enter host.  Example: "www.rit.edu"'
    url = str(input("$> "))
    requestHost = "Host: " + url + "\n\n"

    print 'Enter Url to crawl with trailing "/". Example: "http://www.rit.edu/"'
    fullUrl = str(input("$> "))
    request = "GET " + fullUrl + " HTTP/1.1\n"

    s = Connect(url)

def main():
    s = Connect('www.rit.edu')
    s2 = Connect('www.rit.edu')

    ScrapeCsecWeb(s)
    ScrapeCsecImages(s2)
    FullWebCrawl()
    

if __name__ == "__main__":
    main()

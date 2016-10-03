#!/usr/bin/python
import urllib2
import socket
import re
import os
import threading
import sys
import argparse
import mechanize
import urlparse
import urllib
import ssl
import pandas
from urlparse import urlsplit
from lxml.html import parse
from BeautifulSoup import BeautifulSoup, SoupStrainer

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


def MakeRequest(s, url, host):
    request = "GET " + url + " HTTP/1.1\n"
    requestHost = "Host: " + host + "\r\n\r\n"    
    fullResponse = ''
    s.send(request + requestHost)
    while True:
        response = s.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response

    return fullResponse

def MakeRequestSSL(s, url, host):
    request = "GET " + url + " HTTP/1.1\n"
    requestHost = "Host: " + host + "\r\n\r\n"    
    fullResponse = ''
    ws = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA")
    ws.send(request + requestHost)
    while True:
        response = ws.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response

    return fullResponse

def FullWebCrawl(booler, csv):
    maxPages = 4
    findEmails = 1
    emails = []
    urlQueue = []
    crawledUrls = []
    
    if booler:
        print 'Enter depth: '
        maxPages = int(input("$> "))
        print 'Enter host.  Example: "www.rit.edu"'
        host = str(input("$> "))
        print 'Enter Url to crawl with trailing "/". Example: "http://www.rit.edu/"'
        url = str(input("$> "))
    else:
        url = str(csv)
        host = str(csv)

    urlQueue.append(url)
    while len(urlQueue) > 0 and maxPages > 0:
        s = Connect(url)
        page = MakeRequest(s, urlQueue[0], host)
        
        soup = BeautifulSoup(page)
        links = soup.findAll('a')
        
        newEmails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", page, re.I))
        emails.append(newEmails)
        
        surl = urlQueue[0]
        crawledUrls.append(surl)
        urlQueue.pop(0)

        print "Now in: " + surl
        print "-------------------------------------------------------------"

        for tag in links:
            link = tag.get('href', None)
            if link is not None and link not in crawledUrls and url in link:
                crawledUrls.append(link)
                urlQueue.append(link)
                print link
        
        maxPages = maxPages - 1
        s.close()

    print emails
    return crawledUrls 

def main():
    s = Connect('www.rit.edu')
    s2 = Connect('www.rit.edu')
    directories = []
    #ScrapeCsecWeb(s)
    #ScrapeCsecImages(s2)
    #FullWebCrawl(False, None)

    df = pandas.read_csv('companies.csv', names=['name', 'url'])
    urls = df.url.tolist()
    for url in urls:
        url = url.replace("http://", "")
        url = url.replace("https://", "")
        print url
        directories.append(FullWebCrawl(False, url))
    print directories

if __name__ == "__main__":
    main()

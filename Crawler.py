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
import json
import pandas
from urlparse import urlsplit
from lxml.html import parse
from BeautifulSoup import BeautifulSoup, SoupStrainer

def Connect(url, port):
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

    soup = BeautifulSoup(fullResponse)
    courses = soup.findAll('table')[0].tbody.findAll('tr')
    for course in courses:
        if i > 1 and len(course.findAll('td')) > 2:
            number = course.findAll('td')[0].contents
            name = course.findAll('td')[1].contents
            print str(number + name)
        i = i + 1

def DownloadImage(img2, i):
    image = ''
    s = Connect('www.rit.edu', 80)
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

    soup = BeautifulSoup(fullResponse)
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
    ws = socket.ssl(s)
    ws.send(request + requestHost)
    while True:
        response = ws.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response
    s.close()
    return fullResponse

def HandleRequest(url, host):
    link = ''
    if url.find("https://") is not -1:
        s = Connect(host, 443)
        page = MakeRequestSSL(s, url, host)
        s.close()
        return page
    else:
        s = Connect(host, 80)
        page = MakeRequest(s, url, host)
        soup = BeautifulSoup(page)
        '''try:
            if soup.title.string == "301 Moved Permanently":
                links = soup.findAll('a')
                for tag in links:
                    link = tag.get('href', None)
                s.close()
                page = HandleRequest(link, host)
        except ValueError:
            print "301 check failed."'''
        s.close()
        return page

def FullWebCrawl(booler, csv):
    maxPages = 4
    findEmails = 1
    emails = set()
    urlQueue = []
    crawledUrls = []
    
    if booler:
        print 'Enter depth: '
        #maxPages = int(input("$> "))
        print 'Enter host.  Example: "www.rit.edu"'
        #host = str(input("$> "))
        print 'Enter Url to crawl with trailing "/". Example: "http://www.rit.edu/"'
        #url = str(input("$> "))
    else:
        url = csv
        host = csv
    
    host = str("www.rit.edu")
    url = str("http://www.rit.edu/")

    urlQueue.append(url)
    while len(urlQueue) > 0 and maxPages > 0:
        url = urlQueue[0]
        page = HandleRequest(url, host)
        newEmails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", page, re.I))
        emails.update(newEmails)
        
        surl = urlQueue[0]
        crawledUrls.append(surl)
        urlQueue.pop(0)

        print "Now in: " + surl
        print "-------------------------------------------------------------"
        soup = BeautifulSoup(page)
        links = soup.findAll('a')

        for tag in links:
            link = tag.get('href', None)
            if link is not None and link not in crawledUrls and url in link:
                crawledUrls.append(link)
                urlQueue.append(link)
                print link
        
        maxPages = maxPages - 1

    print emails
    return crawledUrls 

def main():
    directories = []
    #s = Connect('www.rit.edu', 80)
    #s2 = Connect('www.rit.edu', 80)
    #ScrapeCsecWeb(s)
    #ScrapeCsecImages(s2)
    FullWebCrawl(True, None)

    """df = pandas.read_csv('companies.csv', names=['name', 'url'])
    urls = df.url.tolist()
    for url in urls:
        url = url.replace("http://", "")
        url = url.replace("https://", "")
        url = url.replace("/market/pages/index.aspx", "")
        url = url.replace("/pages/home.aspx", "")
        url = url.replace("/", "")
        directories.append(FullWebCrawl(False, url))
    print directories"""

if __name__ == "__main__":
    main()

#!/usr/bin/python
import urllib2
import urllib
import socket
import re
import time
import os
import threading
import sys
import argparse
import mechanize
import urlparse
import urllib
import ssl
import errno
import json
import csv
import pandas
from urlparse import urlsplit
from lxml.html import parse
from socket import error as SocketError
from BeautifulSoup import BeautifulSoup, SoupStrainer
maxConnections = 5
pool = threading.BoundedSemaphore(value=maxConnections)


def Connect(url, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    if port == 443:
        sock = ssl.wrap_socket(s)
        print "Connecting to: {}:{}".format(url, port)
        try:
            sock.connect((url, port))
        except SocketError as e:
            print e
        sock.settimeout(None)
        #sock.setblocking(0)
        return sock
    else:
        s.connect((url, port))
        s.settimeout(None)
        #s.setblocking(0)
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
            number = ''.join(number)
            name = ''.join(name)
            print number + ' ' + name
        i = i + 1

def DownloadImage(img2, i):
    image = ''
    img2 = img2.replace(" ", "%20")
    if len(img2) < 250:
        s = Connect('www.rit.edu', 80)
        request = "GET " + img2 + " HTTP/1.1\n"
        print request
        agent = "User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0\n"
        lang = "Accept-Language: en-US,en;q=0.5\n"
        con = "Upgrade-Insecure-Requests: 1\n"
        encoding = "Accept-Encoding: gzip, deflate\n"
        connection = "Connection: keep-alive\n"
        requestHost = "Host: www.rit.edu\r\n\r\n"
        pool.acquire() 
        s.send(request + encoding + connection + agent + lang + con + requestHost)
        while True:
            response = s.recv(2048)
            if len(response) < 1: break
            image = image + response
        
        s.close()
        pool.release()
        
        pos = image.find("\r\n\r\n")
        image = image[pos + 4:]
        imgFile = "/home/soren/Github/WebSecurity/pictures/image" + str(i) + ".jpg"
        fhand = open(imgFile, 'w+')
        fhand.write(image)
        fhand.close()

def ScrapeCsecImages(s):
    request = "GET /gccis/computingsecurity/people HTTP/1.1\n"
    requestHost = "Host: www.rit.edu\r\n\r\n"
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
        DownloadImage(img2, i)
        i += 1

def MakeRequest(s, url, host):
    request = "GET " + url + " HTTP/1.1\n"
    keep = "Connection: Close\n"
    userAgent = "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1\n"
    requestHost = "Host: " + host + "\r\n\r\n"    
    fullResponse = ''
    s.send(request + keep + userAgent + requestHost)

    while True:
        response = s.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response
    
    return fullResponse

def MakeRequestSSL(s, url, host):
    request = "GET " + url + " HTTP/1.1\n"
    requestHost = "Host: " + host + "\r\n\r\n"    
    userAgent = "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1\n"
    fullResponse = ''
    keep = 'Connection: close\n'
    print "########"
    print request + keep + userAgent + requestHost
    print "########"
    s.send(request + keep + userAgent + requestHost)
    while True:
        response = s.recv(2048)
        if response == '':
            break 
        fullResponse = fullResponse + response
    s.close()
    return fullResponse

def HandleRequest(url, host):
    link = ''
    print host
    print url
    if url.find("https://") is not -1:
        try:
            s = Connect(host, 443)
            page = MakeRequestSSL(s, url, host)
            s.close()
            return page
        except ValueError:
            return ValueError
    else:
        s = Connect(host, 80)
        page = MakeRequest(s, url, host)
        print len(page)
        
        print "---------------------------------------------------------------"
        if len(page) < 700:
            headers, body = page.split("\r\n\r\n")
            print headers
            match = re.findall(r'HTTP/1\.(?:0|1) 301[^\r\n]+', headers)
            if len(match) > 0:
                locationMatch = re.findall(r"Location: ([^\r\n]+)", headers)
                if len(locationMatch) > 0:
                    link = locationMatch[0]
                    host = link.replace("http://", "").replace("https://", "").split("/", 1)[0]
                    print host
                    print link
                    page = HandleRequest(link, host)
                else:
                    raise ValueError("error finding location header")

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
        maxPages = int(input("$> "))
        print 'Enter host.  Example: "www.rit.edu"'
        host = str(input("$> "))
        print 'Enter Url to crawl with trailing "/". Example: "http://www.rit.edu/"'
        url = str(input("$> "))
    else:
        url = '/'
        host = csv

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
                print link
                urlQueue.append(link.encode('utf-8'))
                crawledUrls.append(link.encode('utf-8'))
        
        maxPages = maxPages - 1

    print emails
    return crawledUrls 

def DirBuster(dirFile):
    host = "52.23.205.104"
    addPage = dirFile.split()
    print addPage

def main():
    directories = []
    #s = Connect('www.rit.edu', 80)
    #s2 = Connect('www.rit.edu', 80)
    #ScrapeCsecWeb(s)
    #ScrapeCsecImages(s2)
    #FullWebCrawl(True, None)

    '''df = pandas.read_csv('companies.csv', names=['name', 'url'])
    urls = df.url.tolist()
    for url in urls:
        try:
            url = url.replace("http://", "")
            url = url.replace("https://", "")
            url = url.replace("/market/pages/index.aspx", "")
            url = url.replace("/pages/home.aspx", "")
            url = url.replace("/", "")
            directories.extend(FullWebCrawl(False, url))
        except socket.error as e:
            print e

    os.remove("directories.txt")
    dirFile = open("directories.txt", 'w')
    for item in directories:
        print>>dirFile, item'''
    #dirFile.close()
    #dirFile = open("directories.txt", 'r')
    #DirBuster(dirFile)

if __name__ == "__main__":
    main()

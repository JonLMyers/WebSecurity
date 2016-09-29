#!/usr/bin/python
import urllib
import socket
import BeautifulSoup
import re
import os
import thread

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

def ScrapeCsecImages(s):
    request = "GET /gccis/computingsecurity/people HTTP/1.1\n"
    requestHost = "Host: www.rit.edu\n\n"
    imgList = []

    fullResponse = ''
    i = 1;
    s.send(request + requestHost)

    while True:
        response = s.recv(2048)
        fullResponse = fullResponse + response
        if response == '':
            break

    s.close()

    soup = BeautifulSoup.BeautifulSoup(fullResponse)
    imgs = soup.findAll("div", {"class":"staff-picture"})
    for img in imgs:
        imgList.append(img.findAll('img')[0].get('src'))

    for img2 in imgList:     
        s = Connect('www.rit.edu')
        request = "GET http://www.rit.edu" + img2 + " HTTP/1.1\n"
        requestHost = "Host: www.rit.edu\n\n"
        s.send(request + requestHost)
        image = ''
        
        while True:
            response = s.recv(2048)
            if len(response) < 1: break
            image = image + response
        
        s.close()

        print len(image)
        pos = image.find("\r\n\r\n")
        image = image[pos + 4:]
        imgFile = "/home/soren/Github/WebSecurity/pictures/image" + str(i) + ".jpg"
        fhand = open(imgFile, 'w+')
        print len(image)
        fhand.write(image)
        fhand.close()
        i += 1

def main():
    s = Connect('www.rit.edu')
    s2 = Connect('www.rit.edu')

    ScrapeCsecWeb(s)
    thread.start_new_thread(ScrapeCsecImages, (s2))


if __name__ == "__main__":
    main()

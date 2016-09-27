#!/usr/bin/python
import urllib
import socket
import BeautifulSoup

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
            print number + name
        i = i + 1 

def main():
    #Scrape the csec website.
    s = Connect('www.rit.edu')
    ScrapeCsecWeb(s)



if __name__ == "__main__":
    main()

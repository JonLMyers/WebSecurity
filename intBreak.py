#!/usr/bin/python
import socket
import urllib

def Connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def SendDataA1(s):
    con = "GET /posts/1/vote/like HTTP/1.1\n"
    host = "Host: localhost\n"
    leng = "Content-Length: 2\n\n"
    breaker = "Connection: close\n"
    ua = "User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0\n"
    b = "Accept: */*\n"
    a = "Accept-Language: en-US,en;q=0.5\n"
    c = "Accept-Encoding: gzip, deflate, br\n"
    n = "X-Requested-With: XMLHttpRequest\n"

    s.send(con + host + ua + b + a + c + n + breaker + leng)

while(1):
    s = Connect("localhost", 3000)
    SendDataA1(s) 
    s.close()


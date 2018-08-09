# -*- coding: utf-8 -*-

# Author        : kesalin@gmail.com
# Blog          : http://kesalin.github.io
# Date          : 2014/10/18
# Description   : Export CSND blog articles to Markdown files. 
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
#

import urllib2
import re
import os
import sys
import datetime
import time
import traceback
import codecs
from bs4 import BeautifulSoup

#===========================================================================
# set your CSDN username
__username__ = "rav009"

# set output dir
__output__ = "/home/rav009/PythonSnippet/blogs/"

# set page count
__pagecount__ = 1

enableLog = True

# for test
#__testArticleUrl__ = "http://blog.csdn.net/kesalin/article/details/5414998"

#===========================================================================

# 尝试获取资源次数
gRetryCount = 5
header = {"User-Agent": "Mozilla-Firefox5.0"}

def log(str):
    if enableLog:
        print str

        newFile = open('log.txt', 'a+')
        newFile.write(str + '\n')
        newFile.close()
        
def decodeHtmlSpecialCharacter(htmlStr):
    specChars = {"&ensp;" : "", \
                 "&emsp;" : "", \
                 "&nbsp;" : "", \
                 "&lt;" : "<", \
                 "&gt" : ">", \
                 "&amp;" : "&", \
                 "&quot;" : "\"", \
                 "&copy;" : "®", \
                 "&times;" : "×", \
                 "&divide;" : "÷", \
                 }
    for key in specChars.keys():
        htmlStr = htmlStr.replace(key, specChars[key])
    return htmlStr

def repalceInvalidCharInFilename(filename):
    specChars = {"\\" : "", \
                 "/" : "", \
                 ":" : "", \
                 "*" : "", \
                 "?" : "", \
                 "\"" : "", \
                 "<" : "小于", \
                 ">" : "大于", \
                 "|" : " and ", \
                 "&" :" or ", \
                 }
    for key in specChars.keys():
        filename = filename.replace(key, specChars[key])
    return filename

# process html content to markdown content
def htmlContent2String(contentStr):
    patternImg = re.compile(r'(<img.+?src=")(.+?)(".+ />)')
    patternHref = re.compile(r'(<a.+?href=")(.+?)(".+?>)(.+?)(</a>)')
    patternRemoveHtml = re.compile(r'</?[^>]+>')

    resultContent = patternImg.sub(r'![image_mark](\2)', contentStr)
    resultContent = patternHref.sub(r'[\4](\2)', resultContent)
    resultContent = re.sub(patternRemoveHtml, r'', resultContent)
    resultContent = decodeHtmlSpecialCharacter(resultContent)
    return resultContent

def exportToMarkdown(exportDir, postdate, categories, title, content):
    titleDate = postdate.strftime('%Y-%m-%d')
    contentDate = postdate.strftime('%Y-%m-%d %H:%M:%S %z')
    filename = titleDate + '-' + title
    filename = repalceInvalidCharInFilename(filename)
    filepath = exportDir + '/' + filename + '.markdown'
    print filepath
    log(" >> save as " + filename)

    newFile = open(unicode(filepath, "utf8"), 'w')
    newFile.write('---' + '\n')
    newFile.write('layout: post' + '\n')
    newFile.write('title: \"' + title + '\"\n')
    newFile.write('date: ' + contentDate + '\n')
    newFile.write('comments: true' + '\n')
    newFile.write('categories: [' + categories + ']' + '\n')
    newFile.write('tags: [' + categories + ']' + '\n')
    newFile.write('description: \"' + title + '\"\n')
    newFile.write('keywords: ' + categories + '\n') 
    newFile.write('---' + '\n\n')
    newFile.write(content)
    newFile.write('\n')
    newFile.close()

def download(url, output):
    # 下载文章，并保存为 markdown 格式
    log(" >> download: " + url)

    data = None
    title = ""
    categories = ""
    content = ""
    postDate = datetime.datetime.now()
    
    global gRetryCount
    count = 0
    while True:
        if count >= gRetryCount:
            break
        count = count + 1
        try:
            time.sleep(2.0) #访问太快会不响应
            request = urllib2.Request(url, None, header)
            response = urllib2.urlopen(request)
            data = response.read().decode('UTF-8')
            break
        except Exception,e:
            exstr = traceback.format_exc()
            log(" >> failed to download " + url + ", retry: " + str(count) + ", error:" + exstr)
            pass

    if data == None:
        log(" >> failed to download " + url)
        return

    #print data
    soup = BeautifulSoup(data, features='html5lib')

    topTile = "[置顶]"
    titleDocs = soup.find_all("div", "article_title")
    for titleDoc in titleDocs:
        titleStr = titleDoc.a.get_text().encode('UTF-8')
        title = titleStr.replace(topTile, '').strip()
        #log(" >> title: " + title)

    manageDocs = soup.find_all("div", "article_manage")
    for managerDoc in manageDocs:
        categoryDoc = managerDoc.find_all("span", "link_categories")
        if len(categoryDoc) > 0:
            categories = categoryDoc[0].a.get_text().encode('UTF-8').strip()
        
        postDateDoc = managerDoc.find_all("span", "link_postdate")
        if len(postDateDoc) > 0:
            postDateStr = postDateDoc[0].string.encode('UTF-8').strip()
            postDate = datetime.datetime.strptime(postDateStr, '%Y-%m-%d %H:%M')

    contentDocs = soup.find_all(id="article_content")
    for contentDoc in contentDocs:
        htmlContent = contentDoc.prettify().encode('UTF-8')
        content = htmlContent2String(htmlContent)

    exportToMarkdown(output, postDate, categories, title, content)

def getPageUrlList(url):
    pageUrlList = []
    for i in range(1, __pagecount__ + 1):
        pageUrlList.append("https://blog.csdn.net/" + __username__ + "/article/list/" + str(i))
    return pageUrlList

def getArticleList(url):
    # 获取所有的文章的 url/title
    pageUrlList = getPageUrlList(url)
    
    articleListDocs = []

    strPage = " > parsing page {0}"
    pageNum = 0
    global gRetryCount
    for pageUrl in pageUrlList:
        retryCount = 0
        pageNum = pageNum + 1
        pageNumStr = strPage.format(pageNum)
        print pageNumStr

        while retryCount <= gRetryCount:
            try:
                retryCount = retryCount + 1
                time.sleep(1.0) #访问太快会不响应
                request = urllib2.Request(pageUrl, None, header)
                response = urllib2.urlopen(request)
                data = response.read().decode('UTF-8')
                
                #print data
                soup = BeautifulSoup(data, features="html5lib")

                articleListDocs += soup.find_all("div", attrs={"class": "article-item-box csdn-tracking-statistics"})
                break
            except Exception, e:
                print "getArticleList exception:%s, url:%s, retry count:%d" % (e, pageUrl, retryCount)
                pass
    artices = []
    for article in articleListDocs:
        #print article.prettify().encode('UTF-8')
        a = article.find_all("a")[0]
        #print a.get("href")
        #print a.get_text().encode('utf-8').replace("原", '').replace("转",'').strip()
        #print ts
        #for linkDoc in linkDocs:
            #print linkDoc.prettify().encode('UTF-8')
            #print linkDoc.a
            #link = linkDoc.a
            #url = link["href"].encode('UTF-8')
            #title = link.get_text().encode('UTF-8')
            #title = title.replace(topTile, '').strip()
            #oneHref = "http://blog.csdn.net" + url
            #log("   > title:" + title + ", url:" + oneHref)
            #artices.append([oneHref, title])
        artices.append([a.get("href"),a.get_text().encode('utf-8').replace("原", '').replace("转",'').strip()])

    log("total articles: " + str(len(artices)) + "\n")
    return artices

def getHtmlName(url):
    htmlNameIndex = url.rfind("/");
    urlLen = len(url)
    htmlName = ""
    if htmlNameIndex + 1 == urlLen:
        htmlNameIndex = url.rfind("/", 0, htmlNameIndex)
        htmlName = url[htmlNameIndex + 1:urlLen - 1]
    else:
        htmlName = url[htmlNameIndex + 1:]
    return htmlName

def exportBlog(username, output):
    url = "https://blog.csdn.net/" + username
    outputDir = output

    log(" >> user name: " + username)
    log(" >> output dir: " + outputDir)
    log("start export...")

    outputDir.replace("\\", "/")
    if not os.path.exists(outputDir.decode("utf-8")):
        os.makedirs(outputDir.decode("utf-8"))

    log(url)
    articleList = getArticleList(url)
    totalNum = len(articleList)

    log("start downloading...")
    currentNum = 0
    strPage = "[{0}/{1}] ".decode("utf-8").encode("utf-8")
    for article in articleList:
        currentNum = currentNum + 1
        strPageTemp = strPage.format(currentNum, totalNum)
        strPageTemp = strPageTemp + article[1]
        #log(strPageTemp)

        download(article[0], username)

log("============================================================")
exportBlog(__username__, __output__)
#download(__testArticleUrl__, __output__)

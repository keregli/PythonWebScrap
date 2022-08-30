import requests
from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

#Grabbing Session
s = HTMLSession()
url = 'https://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/viewtopic.php?t=12591'

#Declaring Class
class Report:
    NameResults = []
    IdResults = []
    DateResults = []
    BodyResults1 = []
    BodyResults2 = []
    FinalBodyResults = []
    c = ''

#Grabbing URL
def getdata(url):
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

#Grabbing All Pages
def getNextPage(soup):
    #Wrap in (Try Except) in order to avoid code breaking when the next button no longer appears in search logic
    try:
        page = soup.find('span', {'class': 'gensmall'})
        for link in page:
            for x in link.findAll('a'):
                if x.string == 'Next':
                    url = 'https://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/viewtopic.php?t=12591' + x.get('href')
                    return url
    except:
        return

#Generating List for Post Bodies
def generateBodyList():

    #First loop grabs all posts under row1 attribute
    for ElementBody in soup.findAll('td', {'class': 'row1'}):
        b = ElementBody.findAll('span', {'class': 'postbody'})
        c = ElementBody.findAll('td', {'class': 'quote'})

        #Grabbing responses under quote attribute
        if len(c) > 0:
            for x in c:
                if x.text is not None:
                    Report.c = x.text + ' ' + Report.c

        #Grabbing original posts
        if len(b) > 0:
            for a in b:
                Report.c = a.text + ' ' + Report.c
            Report.BodyResults1.append(Report.c)
            Report.c = ''

    # Second loop grabs all posts under row2 attribute
    for ElementBody in soup.findAll('td', {'class': 'row2'}):
        b = ElementBody.findAll('span', {'class': 'postbody'})
        c = ElementBody.findAll('td', {'class': 'quote'})

        # Grabbing responses under qoute attribute
        if len(c) > 0:
            for x in c:
                if x.text is not None:
                    Report.c = x.text + ' ' + Report.c

        # Grabbing original posts
        if len(b) > 0:
            for a in b:
                Report.c = a.text + ' ' + Report.c
            Report.BodyResults2.append(Report.c)
            Report.c = ''

    #Once loops are finished and both lists are filled...
    #Results of both lists are combined into a new list to properly order posts
    for a in range(0, (len(Report.BodyResults1) + len(Report.BodyResults2))):
        if (a < len(Report.BodyResults1)):
            Report.FinalBodyResults.append(Report.BodyResults1[a])
        if (a < len(Report.BodyResults2)):
            Report.FinalBodyResults.append(Report.BodyResults2[a])


    #Both Original lists are cleared in order to avoid discrepancy when new page gets requested.
    Report.BodyResults1.clear()
    Report.BodyResults2.clear()

#Generating All Lists
def generateList(url):

    # Returns Names
    for ElementName in soup.findAll(attrs='name'):
        names = ElementName.find('b')
        if names not in Report.NameResults:
            Report.NameResults.append(names.text)

    # Returns IDs
    for ElementID in soup.findAll(attrs='name'):
        ids = ElementID.find('a')
        if ids not in Report.IdResults:
            Report.IdResults.append(ids['name'])

    # Returns Bodies
    generateBodyList()

    # Returns Dates
    for ElementDate in soup.findAll(attrs='postdetails'):
        dates = ElementDate.extract()
        if ((dates not in Report.DateResults)):
            if (dates.text[0:6] == "Posted"):
                Report.DateResults.append(dates.text[12:33])

#Looping through all existing pages in order to grab all posts
while True:
    soup = getdata(url)
    url = getNextPage(soup)
    generateList(url)
    print(len(Report.IdResults), len(Report.NameResults), len(Report.DateResults), len(Report.FinalBodyResults))
    df = pd.DataFrame({'ID': Report.IdResults, 'Names': Report.NameResults, 'Date': Report.DateResults, 'Body': Report.FinalBodyResults})
    df.to_csv('thread.csv', index=False, encoding='utf-8')
    if not url:
        break
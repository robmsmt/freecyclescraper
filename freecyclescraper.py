#!/usr/bin/env python

from bs4 import BeautifulSoup
from time import strftime
from os import system
import urllib2
import chardet
import re
import time
import json

searchableGroupList = [
    "https://groups.freecycle.org/group/BarnetUK/posts/offer",
    "https://groups.freecycle.org/group/CamdenSouthUK/posts/offer",
    "https://groups.freecycle.org/group/CityOfLondon/posts/offer",
    "https://groups.freecycle.org/group/HackneyUK/posts/offer",
    "https://groups.freecycle.org/group/HampsteadUK/posts/offer",
    "https://groups.freecycle.org/group/HaringeyUK/posts/offer",
    "https://groups.freecycle.org/group/IslingtonEastUK/posts/offer",
    "https://groups.freecycle.org/group/IslingtonNorthUK/posts/offer",
    "https://groups.freecycle.org/group/IslingtonSouthUK/posts/offer",
    "https://groups.freecycle.org/group/KentishtownUK/posts/offer",
]

def generateIndexHtml():
    html = """
    <!DOCTYPE html><html lang="en"><meta charset="utf-8">
    <head><title>freecyclescraper</title>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.min.js"></script>
        <script type="text/javascript" src="https://cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" src="javascript.js"></script>
    </head>
    <body><section id="content">
        <table id="group_posts_table" class="display" width="100%" cellspacing="0.5">
            <thead>
                <tr>
                    <th>Time Posted</th>
                    <th>Group Name</th>
                    <th>Details</th>
                    <th>Post ID</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </section></body>
    </html>"""
    return html


def getData():
    offerdata = []
    for url in searchableGroupList:
        pageFile = urllib2.urlopen(url)
        pageHtml = pageFile.read()
        pageFile.close()

        ''' todo - fix the unicode bug which means some of the table info is stripped - html meta tags say utf-8 but the
        content looks to be ascii from the chardet analysis of the page'''
        #print(chardet.detect(pageHtml))
        #print(pageFile.headers.getheader('content-type'))

        soup = BeautifulSoup(pageHtml, 'html5lib')
        tr = soup.find_all("tr")

        for element in tr:
            td = element.findAll("td")
            tdData1 = td[0].get_text("|", strip=True)
            # tdData2 is 'broken' due to freecycle not being parsed properly - some data is missing tbc
            tdData2 = td[1]

            # regex strip url to reveal the groupname - front of str then back
            urltext = re.sub(r'https://groups.freecycle.org/group/', '', url)
            urltext = re.sub(r'/posts/offer', '', urltext)
            # regex strip datefield to reveal just the date - front of str then back
            date = re.sub(r'>\|OFFER\|', '', str(tdData1))
            date = re.sub(r'\|\(#[0-9]+\)', '', date)
            # postID stripped from same str as date
            postID = re.sub(r'>\|OFFER\|.*\(', '', str(tdData1))
            postID = re.sub(r'\)', '', postID)

            offerdata.append({"postid": postID,
                              "groupurl": url,
                              "groupurltext": urltext,
                              "dateposted": date,
                              "desc": str(tdData2)
                              })

    # output the offerdata dict to JSON
    with open('data.json', 'w') as fp:
        json.dump(offerdata, fp, sort_keys=False, indent=4)

    return offerdata

def changesInData(difference):
    # changes can be either a new post, deleted post, admin remove one (and changes because of these) e.g.
    # todo make only the new post data printed/spoken (ignore old/deleted etc)

    print("CHANGES at {0}".format(strftime("%Y-%m-%d %H:%M:%S")))
    print(difference)
    x = 0
    while x < 3:
        print "\a"  # makes a "beep"
        time.sleep(0.1)
        x = x + 1

    # this line if uncommented will speak all the differences (osx only)
    #system("say new {0}".format(difference))

    return

if __name__ == '__main__':
    f = open('index.html', 'w')
    f.write(generateIndexHtml())
    f.close()
    prevGetData = None
    #lastDataTimestamp = time.time()
    try:
        with open('data.json') as fp:
            prevGetData = json.load(fp)
        print("loaded data.json file")
    except (IOError, ValueError):
        print("error - opening file")
        prevGetData = None

    while True:
        print ("Refreshing data {0}".format(strftime("%Y-%m-%d %H:%M:%S")))
        newData = getData()

        if newData == prevGetData:
            print("NoChanges at {0}".format(strftime("%Y-%m-%d %H:%M:%S")))
        elif newData != prevGetData and prevGetData is not None:
            difference = [a for a in prevGetData+newData if (a not in prevGetData) or (a not in newData)]
            changesInData(difference)
            #lastDataTimestamp = time.time()
        elif prevGetData is None:
            print("No prev data to compare at {0}".format(strftime("%Y-%m-%d %H:%M:%S")))
        prevGetData = newData
        # pauses between every 60 seconds as to not overload the freecycle server
        time.sleep(60)

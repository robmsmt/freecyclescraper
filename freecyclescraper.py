#!/usr/bin/env python

from bs4 import BeautifulSoup
from time import strftime
from datetime import datetime
from datetime import timedelta
from os import system
import requests
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
                    <th>Details</th>
                    <th>Location</th>
                    <th>Group Name</th>
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
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/52.0.2743.116 Safari/537.36'}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(e)
            print("Waiting 15 minutes")
            time.sleep(60*15)
            return []

        response.encoding = response.headers['content-type']
        pagehtml = response.text

        # Choose a parser (html.parser, lxml, html5lib)
        soup = BeautifulSoup(pagehtml, 'html5lib')
        # Find all TR tags
        tr = soup.find_all("tr")

        for element in tr:
            # Within each TR find the TD tags
            td = element.findAll("td")
            tdData1 = td[0].get_text("|", strip=True)
            tdfull = td[1]
            tdData2 = td[1].get_text("|", strip=True)

            # Use hacky regex to strip out unwanted content (a post with a | could break this)
            tdData2 = re.sub(r'\|See details', '', str(tdData2))
            location = re.sub(r'.*\|\(', '', str(tdData2))
            location = re.sub(r'\)', '', location)
            itemurl = tdfull.a.get('href')
            itemdesc = re.sub(r'\|\(.*\)', '', str(tdData2))
            htmldesc = '<a href="{}">{}</a>'.format(itemurl, itemdesc)

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
                              "htmldesc": htmldesc,
                              "itemdesc": itemdesc,
                              "itemurl": itemurl,
                              "location": location
                              })

    # output the offerdata dict to JSON
    with open('data.json', 'w') as fp:
        json.dump(offerdata, fp, sort_keys=False, indent=4)
    return offerdata

def changesInData(difference):
    # changes can be either a new post OR someone has deleted a top10 post meaning an old one is now "new"
    # we need to drop any that haven't occurred in the last 5 minutes as they are old

    print("CHANGES at {}".format(strftime("%Y-%m-%d %H:%M:%S")))

    for i in range(len(difference)):
        dict = difference[i]
        itemdesc = dict['itemdesc']
        print(itemdesc)
        timepost = dict['dateposted']
        format = "%a %b %d %H:%M:%S %Y"
        now = datetime.now().strftime(format)
        # lol @ date>string>date
        date_object_now = datetime.strptime(now, format)
        date_object_then = datetime.strptime(timepost, format)
        delt = (date_object_now - date_object_then)

        # only notify on changes with timestamp of under 15mins
        if(delt <= timedelta(minutes=15)):
            # makes a "beep"
            print ("\a")
            time.sleep(0.1)
            print ("\a")
            time.sleep(0.1)
            # Speak the differences
            system("say New item, {}".format(dict['itemdesc']))

    return

if __name__ == '__main__':
    f = open('index.html', 'w')
    f.write(generateIndexHtml())
    f.close()
    prevGetData = None
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
            #difference = [a for a in prevGetData+newData if (a not in prevGetData) or (a not in newData)]
            difference = [a for a in prevGetData+newData if (a not in prevGetData)]
            changesInData(difference)
        elif prevGetData is None:
            print("No prev data to compare at {0}".format(strftime("%Y-%m-%d %H:%M:%S")))
        prevGetData = newData
        # pauses between every 60 seconds as to not overload the freecycle server
        time.sleep(60)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MocoParser.py

Google Reader Atom Parser
"""

import time
from xml.etree import ElementTree
from MocoEntry import MocoEntry

def ParseString(feed):
    """ Parse Google Reader Atom 

    return list of MocoEntry
    """
    root = ElementTree.fromstring(feed)

    entry = []

    for elem in root.findall("{http://www.w3.org/2005/Atom}entry"):
        entry.append(_CreateEntry(elem))

    return entry

def _CreateEntry(elem):
    crawlTimestampMsec = int(elem.attrib['{http://www.google.com/schemas/reader/atom/}crawl-timestamp-msec'])

    id = _Strip(elem.find("{http://www.w3.org/2005/Atom}id").text)
    
    link = elem.find('{http://www.w3.org/2005/Atom}link').attrib['href']

    title = _Strip(elem.find('{http://www.w3.org/2005/Atom}title').text)

    publishedText = _Strip(elem.find('{http://www.w3.org/2005/Atom}published').text)
    published = _ParseTime(publishedText)
    
    content = ""
    contentElem = elem.find('{http://www.w3.org/2005/Atom}content')
    if contentElem is not None:
        content = contentElem.text
    else:
        summaryElem = elem.find('{http://www.w3.org/2005/Atom}summary')
        if summaryElem is not None:
            content = summaryElem.text
            
    sourceElem = elem.find('{http://www.w3.org/2005/Atom}source')

    sourceLink = sourceElem.find('{http://www.w3.org/2005/Atom}link').attrib['href']

    sourceTitle = _Strip(sourceElem.find('{http://www.w3.org/2005/Atom}title').text)

    return MocoEntry(id, link, title, published, content,
                 sourceTitle, sourceLink, crawlTimestampMsec)


def _ParseTime(timestr):
    ts = time.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ")
    return ts

def _Strip(s):
    return s.strip(" \t\n")

if __name__ == "__main__":
    pass

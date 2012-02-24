#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MocoEntry.py

Moco Entry for an article
"""

class MocoEntry(object):
    def __init__(self, id, link, title, published, content,
                 sourceTitle, sourceLink, crawlTimestampMsec):
        self.__id = id
        self.__link = link
        self.__title = title
        self.__published = published
        self.__content = content
        self.__sourceTitle = sourceTitle
        self.__sourceLink = sourceLink
        self.__crawlTimestampMsec = crawlTimestampMsec

    def __eq__(self, other):
        return self.__id == other.id

    def __cmp__(self, other):
        if self.__crawlTimestampMsec == other.crawlTimestampMsec:
            return cmp(self.__id, other.id)
        else:
            return cmp(self.__crawlTimestampMsec, other.crawlTimestampMsec)

    @property
    def id(self):
        return self.__id

    def GetLink(self):
        return self.__link

    def SetLink(self, link):
        self.__link = link

    link = property(GetLink, SetLink)

    @property
    def title(self):
        return self.__title

    @property
    def published(self):
        return self.__published

    @property
    def content(self):
        return self.__content

    @property
    def sourceTitle(self):
        return self.__sourceTitle

    @property
    def sourceLink(self):
        return self.__sourceLink

    @property
    def crawlTimestampMsec(self):
        return self.__crawlTimestampMsec


if __name__ == "__main__":
    pass

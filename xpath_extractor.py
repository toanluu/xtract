# encoding: utf-8
"""
Extract content from html file using xpath syntax

Authors: Toan Luu
"""

import time

import requests
from lxml import html

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) "
                  "Gecko/20100101 Firefox/46.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0"
}


def inner_html(node):
    """
    get original html from a node
    """
    return (node.text or '') + ''.join(
        [html.tostring(child) for child in node.iterchildren()])


def xtract_from_url(url, xpath):
    """
    Extract all elements from url
    :param url:
    :param xpath:
    :return: list of values
    """
    SLEEP = 10
    cnt = 6
    while cnt > 0:
        try:
            page = requests.get(url, headers=HEADERS)
            cnt = 0
        except:
            print
            'Fail with request %s, retry in %ss, %s  times left' % (
                url, SLEEP, cnt)
            cnt -= 1
            time.sleep(SLEEP)

    tree = html.fromstring(page.text)
    return tree.xpath(xpath)


def xtract(node, xpath):
    """
    Extract from a node
    :param node:
    :param xpath:
    :return: list of values
    """
    return node.xpath(xpath)


def xtract_first_from_url(url, xpath):
    """
    Extract first element from url
    :param url:
    :param xpath:
    :return: first value
    """
    nodes = xtract_from_url(url, xpath)
    if len(nodes) == 0:
        return None
    return nodes[0]


def xtract_first(node, xpath):
    """
    Extract first element from a node
    """
    nodes = node.xpath(xpath)[0]
    if len(nodes) == 0:
        return None
    return nodes[0]


def xtract_html(node, xpath):
    """
    Extract whole html content fron a node
    :param node:
    :param xpath:
    """
    return inner_html(node.xpath(xpath)[0])


def xtract_fields(url, field_xpaths):
    """
    Extract multiple fields from url
    :param url:
    :param field_xpaths: dictionary of field and xpath, for example:
        {
        'date': '//table[@summary=""]/tbody/tr/td[1]/span/a/text()',
        'content': '//table[@summary=""]/tbody/tr/td[2]/span/text()'
        }
    :return:
    """
    page = requests.get(url, headers=HEADERS)
    tree = html.fromstring(page.text)
    return xtract_fields_from_node(tree, field_xpaths)


def xtract_fields_from_node(node, field_xpaths):
    results = {}
    for k, v in field_xpaths.items():
        results[k] = node.xpath(v)

    return results


def xtract_cleaned_fields_from_url(url, field_xpaths):
    """
    Return only first extracted element
    """
    page = requests.get(url, headers=HEADERS)
    tree = html.fromstring(page.text)
    return xtract_cleaned_fields(tree, field_xpaths)


def xtract_cleaned_fields(node, field_xpaths):
    results = {}
    for k, v in field_xpaths.items():
        values = node.xpath(v)
        if values is None or len(values) == 0:
            results[k] = None
        else:
            results[k] = values[0].strip()

    return results


def xtract_table(url, field_xpaths):
    values = {}
    page = requests.get(url, headers=HEADERS)
    # print page.text
    tree = html.fromstring(page.text)
    length = 0
    for k, v in field_xpaths.items():
        values[k] = tree.xpath(v)
        # print k, values[k]
        newLength = len(values[k])
        if length != 0 and newLength != length:
            print
            'WARNING: Column size is different between values:', \
            length, newLength
            return []
        length = newLength
    """
        Convert map to list to transform table:
        {
            "k1" : ["v11", "v12"],
            "k2" : ["v21", "v22"]
        }
        =>
        [
            {
                "k1": "v11",
                "k2" : "v21"
            },
            {
                "k1": "v12",
                "k2" : "v22"
            }
        ]
    """
    results = []
    for i in range(0, length):
        item = {}
        for k, v in values.items():
            item[k] = v[i]
        results.append(item)
    return results

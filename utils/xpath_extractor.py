# encoding: utf-8
"""
Extract content from html file using xpath syntax

Authors: Toan Luu
"""

import logging
import time
from fake_useragent import UserAgent

import requests
from lxml import html

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s', level=logging.ERROR)

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


class Extractor(object):

    def __init__(self, headers=HEADERS, cookies={}, sleep_failed=10, max_retry=5, delay=0.1):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)

        self.cookies = cookies
        self.sleep_failed = sleep_failed
        self.delay = delay
        self.max_retry = max_retry
        self.headers = headers
        self.user_agent = UserAgent()

    def get_with_cookie(self, url):
        cnt = self.max_retry
        while cnt > 0:
            try:
                self.headers['User-Agent'] = self.user_agent.random
                page = requests.get(url, headers=self.headers, cookies=self.cookies)
                self.cookies = page.cookies
                time.sleep(self.delay)
                cnt = 0
            except:
                self.log.exception('Fail with request %s, retry in %ss, %s  times left' % (url, self.sleep_failed, cnt))
                cnt -= 1
                time.sleep(self.sleep_failed)

        # self.log.info(self.cookies)
        return page

    def xtract_from_url(self, url, xpath):
        """
        Extract all elements from url
        :param url:
        :param xpath:
        :return: list of values
        """

        page = self.get_with_cookie(url)
        tree = html.fromstring(page.text)
        results = tree.xpath(xpath)
        if not results:
            self.log.warning('===>Empty content with url: %s\n%s', url, page.text)

        return results

    def xtract_from_node(node, xpath):
        """
        Extract from a node
        :param node:
        :param xpath:
        :return: list of values
        """
        return node.xpath(xpath)

    def xtract_first_from_url(self, url, xpath):
        """
        Extract first element from url
        :param url:
        :param xpath:
        :return: first value
        """
        nodes = self.xtract_from_url(url, xpath)
        if len(nodes) == 0:
            return None
        return nodes[0]

    def xtract_first_from_node(self, node, xpath):
        """
        Extract first element from a node
        """
        nodes = node.xpath(xpath)[0]
        if len(nodes) == 0:
            return None
        return nodes[0]

    def xtract_html_from_node(self, node, xpath):
        """
        Extract whole html content from a node
        :param node:
        :param xpath:
        """
        return inner_html(node.xpath(xpath)[0])

    def xtract_fields_from_url(self, url, field_xpaths):
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
        page = self.get_with_cookie(url)
        tree = html.fromstring(page.text)
        return self.xtract_fields_from_node(tree, field_xpaths)

    def xtract_fields_from_node(self, node, field_xpaths):
        results = {}
        for k, v in field_xpaths.items():
            values = node.xpath(v)
            results[k] = [v.strip() for v in values]

        return results

    def xtract_cleaned_fields_from_url(self, url, field_xpaths):
        """
        Return only first extracted element
        """
        page = self.get_with_cookie(url)
        tree = html.fromstring(page.text)
        return self.xtract_cleaned_fields_from_node(tree, field_xpaths)

    def xtract_cleaned_fields_from_node(self, node, field_xpaths):
        results = {}
        for k, v in field_xpaths.items():
            values = node.xpath(v)
            if values is None or len(values) == 0:
                results[k] = None
            else:
                results[k] = values[0].strip()

        return results

    def xtract_table_from_url(self, url, field_xpaths):
        values = {}
        page = self.get_with_cookie(url)
        tree = html.fromstring(page.text)
        length = 0
        for k, v in field_xpaths.items():
            values[k] = tree.xpath(v)
            newLength = len(values[k])
            if length != 0 and newLength != length:
                self.log.warning('Column size is different between values: %s vs %s', length, newLength)
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

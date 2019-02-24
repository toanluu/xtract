import time

from utils.xpath_extractor import Extractor

"""
Example using xpath_extractor to extract paper title, author names, email from springer.com.
"""

HEADER = {
    "Host": "academic.oup.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

base_url = 'https://academic.oup.com'
field_xpaths = {
    'title': '//h1[@class="wi-article-title article-title-main"]/text()',
    'name': '//div[@class="info-card-name"]/text()',
    'email': '//div[@class="info-author-correspondence"]/a/text()',
    'time': '//div[@class="citation-date"]/text()'
}
url_xpath = '//div[@class="al-article-items"]/h5/a/@href'
url_template = 'https://academic.oup.com/jpart/issue/{0}/{1}'

cnt = 0


for volume in [29]:
    for issue in [1]:
        xtractor = Extractor(headers=HEADER, delay=2)
        file_name = 'academic-%s-%s.tsv' % (volume, issue)
        print('write to', file_name)
        with open(file_name, 'w', encoding='utf-8') as f:
            url = url_template.format(volume, issue)
            paper_urls = xtractor.xtract_from_url(url, url_xpath)
            if paper_urls:
                for paper_url in paper_urls:
                    paper_detail_url = base_url + paper_url
                    print('extract from', paper_detail_url)
                    result = xtractor.xtract_fields_from_url(paper_detail_url, field_xpaths)
                    if len(result['name']) > 0:
                        cnt += 1
                        output = '%s\t%s\t%s\t%s\t%s\t%s' % (
                            cnt, ','.join(result['time']), ','.join(result['name']), ','.join(result['email']),
                            ','.join(result['title']), paper_detail_url)
                        f.write(output + '\n')
                    else:
                        print('Cannot extract!')
                        time.sleep(60*5)
            else:
                print('ReCaptcha!')
                time.sleep(60 * 10)

        time.sleep(60*10)

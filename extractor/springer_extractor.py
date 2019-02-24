from utils.xpath_extractor import Extractor

"""
Example using xpath_extractor to extract paper title, author names, email from springer.com.
"""

extractor = Extractor()

base_url = 'https://link.springer.com'
field_xpaths = {
    'title': '//h1/text()',
    'name': '//span[@class="authors__name"]/text()',
    'email': '//span[@class="authors__contact"]/a/@title',
    'time': '//time/@datetime'
}
url_xpath = '//h2/a[@class="title"]/@href'
category = 'Civil Engineering'
start_year = 2015
end_year = 2019
url_template = 'https://link.springer.com/search/page/{0}?date-facet-mode=between&facet-sub-discipline={1}&previous-start-year={2}&sortOrder=newestFirst&facet-end-year={3}&previous-end-year={3}&facet-start-year={2}'

cnt = 0
# extract data from first 5 pages
for page in range(1, 6):
    url = url_template.format(page, category, start_year, end_year)
    for paper_url in extractor.xtract_from_url(url, url_xpath):
        paper_url = base_url + paper_url
        result = extractor.xtract_fields_from_url(paper_url, field_xpaths)
        # extract only paper which have contact email
        if len(result['email']) > 0:
            cnt += 1
            output = '%s\t%s\t%s\t%s\t%s\t%s' % (
                cnt, ','.join(result['time']), ','.join(result['name']), ','.join(result['email']),
                ','.join(result['title']), paper_url)
            print(output)

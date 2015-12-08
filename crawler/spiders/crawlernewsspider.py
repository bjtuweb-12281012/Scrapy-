from crawler.items import NeteaseItem
from crawler.items import SinaItem
from crawler.items import TencentItem
from crawler.news_pack.news_func import ListCombiner
from crawler.news_pack.news_func import GetDate

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

import re

class NeteaseNewsSpider(CrawlSpider):
    name = 'netease_news_spider'
    allowed_domains = ['news.163.com']
    start_urls = ['http://news.163.com']
    url_pattern = r'(http://news\.163\.com)/(\d{2})/(\d{4})/\d+/(\w+)\.html'
    rules = [Rule(SgmlLinkExtractor(allow=[url_pattern]), 'parse_news')]
    
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        
        item = NeteaseItem()
        item['source'] = 'netease' # pattern.group(1)
        item['date'] = '20' + pattern.group(2) + pattern.group(3)
        item['newsId'] = pattern.group(4)
        item['cmtId'] = item['newsId']
        item['boardId'] = sel.re(r"boardId = \"(.*)\"")[0]
        item['comments'] = {'link':str('http://comment.news.163.com/'+item['boardId']+'/'+item['cmtId']+'.html')}
        item['contents'] = {'link':str(response.url), 'title':u'', 'passage':u''}
        item['contents']['title'] = sel.xpath("//h1[@id='h1title']/text()").extract()[0]
        item['contents']['passage'] = ListCombiner(sel.xpath('//p/text()').extract())
        return item

class SinaNewsSpider(CrawlSpider):
    name = 'sina_news_spider'
    allowed_domains = ['finance.sina.com.cn']
    start_urls = ['http://roll.finance.sina.com.cn/finance/gncj/gncj/index_1.shtml']
    datenow = GetDate()
    url_pattern = r'(http://finance\.sina\.com\.cn)/china/' + datenow + '/\d{4}(\d{8})\.(?:s)html'
    rules = [Rule(SgmlLinkExtractor(allow=[url_pattern]), 'parse_news'),
             Rule(SgmlLinkExtractor(allow=('./index_[2-9].shtml', ),))]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        datenow = GetDate()
        item = SinaItem()
        item['source'] = 'sina' # pattern.group(1)
        item['date'] = datenow
        item['newsId'] = sel.re(r'comment_id:(\d+-\d-\d+)')[0]
        item['cmtId'] = item['newsId']
        item['channelId'] = sel.re(r'comment_channel:(\w+);')[0]
        item['comments'] = {'link':str('http://comment5.news.sina.com.cn/page/info?format=json&channel='+item['channelId']+'&newsid='+item['cmtId']+'&group=0&compress=1&ie=gbk&oe=gbk&page=1&page_size=100&jsvar=requestId_24')}
        item['contents'] = {'link':str(response.url), 'title':u'', 'passage':u''}
        item['contents']['title'] = sel.xpath("//h1[@id='artibodyTitle']/text()").extract()[0]
        item['contents']['passage'] = ListCombiner(sel.xpath('//p/text()').extract())
        yield item





class TencentNewsSpider(CrawlSpider):
    name = 'tencent_news_spider'
    allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
    rules = [Rule(SgmlLinkExtractor(allow=[url_pattern]), 'parse_news')]
    
    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        item = TencentItem()
        item['source'] = 'tencent' # pattern.group(1)
        item['date'] = pattern.group(2)
        item['newsId'] = pattern.group(3)
        item['cmtId'] = (sel.re(r"cmt_id = (.*);"))[0] # unicode string
        item['comments'] = {'link':str('http://coral.qq.com/')+item['cmtId']}
        item['contents'] = {'link':str(response.url), 'title':u'', 'passage':u''}
        item['contents']['title'] = sel.xpath('//h1/text()').extract()[0]
        item['contents']['passage'] = ListCombiner(sel.xpath('//p/text()').extract())
        return item

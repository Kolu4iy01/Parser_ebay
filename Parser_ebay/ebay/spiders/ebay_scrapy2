import scrapy
from scrapy.http import Request

class EbayScrapySpider(scrapy.Spider):
    name = "ebay_scrapy"
    allowed_domains = ["www.ebay.com"]
    start_urls = ["https://www.ebay.com"]

    def __init__(self, search="Notebook"):
        self.search_string = search

    def parse(self, response):
        trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").get()[0]
        search_url = f"http://www.ebay.com/sch/i.html?_from=R40&_trksid={trksid}&_nkw={self.search_string.replace(' ', '+')}&_ipg=200"
        yield Request(search_url, callback=self.parse_link)

    def parse_link(self, response):
        results = response.xpath('//div/div/ul/li[contains(@class, "s-item")]')
        
        for product in results:
            title = self.extract_title(product)
            price = product.xpath('.//*[@class="s-item__price"]/text()').get()
            product_url = product.xpath('.//a[@class="s-item__link"]/@href').get()

            summary_data = {
                "title": title,
                "Price": price,
                "URL": product_url
            }

            yield Request(product_url, meta={'summary_data': summary_data}, callback=self.parse_product_details)

        next_page_url = response.xpath('//*/a[@class="x-pagination__control"][2]/@href').get()
        if next_page_url and not str(next_page_url).endswith("#"):
            yield Request(next_page_url, callback=self.parse_link)

    def extract_title(self, product):
        title = product.xpath('.//*[@class="s-item__title"]//text()').get()
        if not title:
            title = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]/text()').get()
            if not title:
                title = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]//text()').get()
        
        if title == 'New Listing':
            title = product.xpath('.//*[@class="s-item__title"]//text()').get()[1] if product.xpath('.//*[@class="s-item__title"]//text()').get() else "ERROR"

        return title if title else "ERROR"

    def parse_product_details(self, response):
        data = response.meta['summary_data']
        data["image"] = response.xpath('//div[@class="ux-image-carousel-item image-treatment active  image"]/img/@src').get()
        data["vendor"] = response.xpath('//div[@class="x-sellercard-atf__info__about-seller"]/a/span/text()').get()
        data["shipping"] = response.xpath('//div[@class="ux-labels-values__values-content"]/div/span[@class="ux-textspans ux-textspans--BOLD"]/text()').get()
        yield data

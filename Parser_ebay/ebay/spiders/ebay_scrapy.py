import scrapy


class EbayScrapySpider(scrapy.Spider):
    name = "ebay_scrapy"
    allowed_domains = ["www.ebay.com"]
    start_urls = ["https://www.ebay.com"]

    def __init__(self, search="Notebook"):
        self.search_string = search

    def parse(self, response):
        trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").get()[0]

        # Створіть url і запустіть запити
        yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40&_trksid=" + trksid +
                             "&_nkw=" + self.search_string.replace(' ', '+') + "&_ipg=200",
                             callback=self.parse_link)

    def parse_link(self, response):
        # Cписок товарів
        results = response.xpath('//div/div/ul/li[contains(@class, "s-item" )]')
        for product in results:
            title = product.xpath('.//*[@class="s-item__title"]//text()').get()
            if title == None:
                title = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]/text()').get()
                if title == None:
                    title = product.xpath('.//*[@class="s-item__title s-item__title--has-tags"]//text()').get()

            if title == 'New Listing':
                title = product.xpath('.//*[@class="s-item__title"]//text()').get()[1]

            if title == None:
                title = "ERROR"

            price = product.xpath('.//*[@class="s-item__price"]/text()').get()
            # print('price_________{}'.format(price))
            product_url = product.xpath('.//a[@class="s-item__link"]/@href').get()

            summary_data = {
                "title": title,
                "Price": price,
                "URL": product_url
            }

            data = {'summary_data': summary_data}
            yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details)

        next_page_url = response.xpath('//*/a[@class="x-pagination__control"][2]/@href').get()

        if next_page_url == None or str(next_page_url).endswith("#"):
            self.log("eBay products collected successfully !!!")
        else:
            print('\n' + '-' * 30)
            print('Next page: {}'.format(next_page_url))
            yield scrapy.Request(next_page_url, callback=self.parse_link)

    def parse_product_details(self, response):
        data = response.meta['summary_data']
        data["image"] = response.xpath('//div[@class="ux-image-carousel-item image-treatment active  image"]/img/@src').get()
        data["vendor"] = response.xpath('//div[@class="x-sellercard-atf__info__about-seller"]/a/span/text()').get()
        data["shipping"] = response.xpath('//div[@class="ux-labels-values__values-content"]/div/span[@class="ux-textspans ux-textspans--BOLD"]/text()').get()
        yield data





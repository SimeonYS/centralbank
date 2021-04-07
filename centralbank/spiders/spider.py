import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcentralbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.centralbank.com/news?page={}'

class CcentralbankSpider(scrapy.Spider):
	name = 'centralbank'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//a[@class="post_link"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 12:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="subtitle"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcentralbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

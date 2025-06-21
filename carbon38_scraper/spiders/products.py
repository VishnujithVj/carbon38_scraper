import scrapy
import json
from carbon38_scraper.items import Carbon38ScraperItem

class CarbonSpider(scrapy.Spider):
    name = "carbon"
    allowed_domains = ["carbon38.com"]
    base_url = "https://www.carbon38.com/en-in/collections/tops"
    page_number = 1

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.base_url}?page=1&filter.p.m.custom.available_or_waitlist=1",
            callback=self.parse
        )

    def parse(self, response):
        # Extract embedded JSON from <script> tag
        script_data = response.xpath('//script[contains(text(), "__INITIAL_STATE__")]/text()').get()
        if not script_data:
            self.logger.warning("⚠️ No embedded product JSON found.")
            return

        try:
            # Safely extract JSON string
            json_str = script_data.split('=')[1].strip().rstrip(';')
            data = json.loads(json_str)
            products = data.get('collection', {}).get('products', [])
        except Exception as e:
            self.logger.error(f"❌ JSON parsing failed: {e}")
            return

        for product in products:
            item = Carbon38ScraperItem()
            item['breadcrumbs'] = ["Home", "Collections", "All Products", product.get("title")]
            item['primary_image_url'] = "https:" + product.get("featured_image", "")
            item['brand'] = product.get("vendor")
            item['product_name'] = product.get("title")
            item['price'] = f"₹{product.get('price', 0) / 100:.2f}"
            item['reviews'] = "0 Reviews"  # Can be enriched later with full detail scraping
            item['colour'] = product['variants'][0].get('option1') if product.get("variants") else ""
            item['sizes'] = [v.get('option2') for v in product.get('variants', [])]
            item['description'] = product.get("description", "")
            item['sku'] = product['variants'][0].get('sku') if product.get("variants") else ""
            item['product_id'] = str(product.get("id"))
            item['product_url'] = response.urljoin("/en-in/products/" + product.get("handle"))
            item['image_urls'] = ["https:" + img for img in product.get('images', [])]
            yield item

        # Continue to next page if products exist
        if products:
            self.page_number += 1
            next_page_url = f"{self.base_url}?page={self.page_number}&filter.p.m.custom.available_or_waitlist=1"
            yield response.follow(next_page_url, callback=self.parse)

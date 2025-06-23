import scrapy
import json
from w3lib.html import remove_tags
from carbon38_scraper.items import Carbon38ScraperItem

class CarbonSpider(scrapy.Spider):
    name = "carbon"
    allowed_domains = ["carbon38.com"]
    start_urls = ["https://carbon38.com/en-in/collections/tops"]

    def parse(self, response):
        product_links = response.css("h2.ProductItem__Title a::attr(href)").getall()
        if not product_links:
            self.logger.warning("⚠️ No product links found on page.")
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        json_text = response.xpath(
            '//script[@type="application/json" and @data-product-json]/text()'
        ).get()
        if not json_text:
            self.logger.warning(f"No JSON found on: {response.url}")
            return

        data = json.loads(json_text)
        product = data.get("product", {})
        variants = product.get("variants", [])

        item = Carbon38ScraperItem()
        item["breadcrumbs"] = ["Home", "Collections", "Tops", product.get("title")]
        featured = product.get("featured_image") or ""
        item["primary_image_url"] = "https:" + featured if featured else ""
        item["brand"] = product.get("vendor", "")
        item["product_name"] = product.get("title", "")

        if variants:
            price_int = int(variants[0].get("price", 0))
            item["price"] = f"₹{price_int/100:.2f}"
            item["colour"] = variants[0].get("option1", "")
            item["sizes"] = [v.get("option2", "") for v in variants if v.get("option2")]
            item["sku"] = variants[0].get("sku", "")
        else:
            item["price"] = "₹0.00"
            item["colour"] = ""
            item["sizes"] = []
            item["sku"] = ""

        description = product.get("description") or ""
        item["description"] = remove_tags(description).strip()
        item["reviews"] = "0 Reviews"
        item["product_id"] = str(product.get("id", ""))
        item["product_url"] = response.url
        item["image_urls"] = [
            "https:" + img for img in product.get("images", []) if img
        ]

        yield item

# 🛍️ Carbon38 Scraper Project

This Scrapy project scrapes product data (tops) from the Carbon38 website.




## ✅ Fields Scraped

- `product_name`
- `brand`
- `price`
- `colour`
- `sizes`
- `description`
- `product_url`
- `product_id`
- `primary_image_url`
- `image_urls`
- `breadcrumbs`
- `reviews`
- `sku`


## Tools Used

- **Python** – programming language used
- **Scrapy** – Web scraping framework
- **JSON & CSV** – Output file formats
- **WSL2 (Linux)** – Windows Subsystem for Linux for running Linux tools
- **Ubuntu** – Linux distro used inside WSL2

## How to Run

```bash
scrapy crawl carbon -o Carbon38_data.json
# or export to CSV
scrapy crawl carbon -o Carbon38_data.csv

import scrapy
import pandas as pd
import re

class ShopifyScraperSpider(scrapy.Spider):
    name = 'shopify_scraper'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    # Prevent scrapy from retrying requests with the following http status codes
    custom_settings = {
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408],
        "RETRY_TIMES": 0,
    }
    def start_requests(self):
        # Retrieve the file argument passed
        file = getattr(self, 'file', None)
        if file:
          try:
            # Read csv into a dataframe and loop over the domain_url column
            df = pd.read_csv(file)
            for link in df['domain_url']:
                yield scrapy.Request(url=link, callback=self.parse)
          except FileNotFoundError:
            print("File not found")
        else:
          print("File not specified")

    def parse(self, response):
      # CSS Selector to select the body, and title tag (© Kevin)
      body = response.css('body :not(script):not(style):not(code)::text').extract()
      title = response.css('title::text').extract()
      meta_description = response.css('meta[name=description]::attr(content)').extract()
      imgs = response.css('img[alt]::attr(alt)').extract()
      # response.css outputs a list, this joins it into a string
      sbody = " ".join(body)
      stitle = " ".join(title)
      smeta_description = " ".join(meta_description)
      simgs = " ".join(imgs)
      # Used regex to remove "{{...}}" and extra whitespaces
      stitle = stitle.strip()
      fbody = re.sub(r"{{.*?}}|\s+", " ", sbody)
      fmeta_description = re.sub(r"{{.*?}}|\s+", " ", smeta_description)
      fimgs = re.sub(r"{{.*?}}|\s+", " ", simgs)

      yield {"domain_url": response.url, 'title': stitle, "meta_description": fmeta_description, "texts": fbody,  "alt_text": fimgs}
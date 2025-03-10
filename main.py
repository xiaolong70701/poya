from poya.scraper import PoyaScraper

query = "衛生紙"
scraper = PoyaScraper(query=query)
scraper.run(max_workers=6)
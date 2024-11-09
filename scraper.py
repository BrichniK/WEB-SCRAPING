import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm  # Import tqdm for progress bar

current_page = 1
data = []
proceed = True
start_time = time.time()

# Define the total number of pages to scrape. We set a high number since we stop at the first 404.
total_pages_to_scrape = 50

# Using tqdm to show the progress of scraping through pages
with tqdm(total=total_pages_to_scrape, desc="Scraping Pages", unit="page") as pbar:
    while proceed:
        print(f"Currently scraping page: {current_page}")

        url = f"https://books.toscrape.com/catalogue/page-{current_page}.html"
        proxies = ""

        # proxies={'http': 'http://customer-[your_username]:[your_password]_@pr.oxylabs.io:7777'}

        page = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(page.text, "html.parser")

        # Stop if a 404 page is encountered
        if soup.title and soup.title.text == "404 Not Found":
            proceed = False
        else:
            all_books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

            for book in all_books:
                item = {
                    'Title': book.find("img").attrs["alt"],
                    'Link': "https://books.toscrape.com/catalogue/" + book.find("a").attrs["href"],
                    'Price': book.find("p", class_="price_color").text[2:],
                    'Stock': book.find("p", class_="instock availability").text.strip()
                }
                data.append(item)

        current_page += 1
        pbar.update(1)  # Update the progress bar after each page

df = pd.DataFrame(data)
df.to_csv("books.csv", index=False)

end_time = time.time()
print(f"Scraping completed in {end_time - start_time:.2f} seconds. Data saved to books.csv.")

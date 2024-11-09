import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import threading

# Shared resources and lock for controlling access
data = []
data_lock = threading.Lock()

# Define the function for scraping a single page (Producer)
def scrape_page(page_number):
    url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
    proxies = ""

    try:
        page = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(page.text, "html.parser")

        if soup.title and soup.title.text == "404 Not Found":
            return []

        all_books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
        page_data = []

        for book in all_books:
            item = {
                'Title': book.find("img").attrs["alt"],
                'Link': "https://books.toscrape.com/catalogue/" + book.find("a").attrs["href"],
                'Price': book.find("p", class_="price_color").text[2:],
                'Stock': book.find("p", class_="instock availability").text.strip()
            }
            page_data.append(item)

        # Use the lock to safely append to shared data
        with data_lock:
            data.extend(page_data)

    except Exception as e:
        print(f"Error scraping page {page_number}: {e}")

# Main program
total_pages_to_scrape = 50
start_time = time.time()

threads = []
for page_number in range(1, total_pages_to_scrape + 1):
    t = threading.Thread(target=scrape_page, args=(page_number,))
    threads.append(t)
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv("books_philosophers.csv", index=False)

end_time = time.time()
print(f"Scraping completed in {end_time - start_time:.2f} seconds. Data saved to books_philosophers.csv.")

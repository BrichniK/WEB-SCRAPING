import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed  # Import ThreadPoolExecutor for multithreading

# Define a function for scraping a single page
def scrape_page(page_number):
    url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
    proxies = ""

    try:
        page = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(page.text, "html.parser")

        # Check if it's a 404 page
        if soup.title and soup.title.text == "404 Not Found":
            return []

        # Scrape book details from the page
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
        
        return page_data

    except Exception as e:
        print(f"Error scraping page {page_number}: {e}")
        return []

# Define the total number of pages to scrape
total_pages_to_scrape = 50
data = []

# Start timing
start_time = time.time()

# Using ThreadPoolExecutor for multithreading
with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers for the number of threads
    futures = [executor.submit(scrape_page, page_number) for page_number in range(1, total_pages_to_scrape + 1)]

    # Using tqdm for progress bar
    with tqdm(total=total_pages_to_scrape, desc="Scraping Pages", unit="page") as pbar:
        for future in as_completed(futures):
            page_data = future.result()
            if page_data:
                data.extend(page_data)
            pbar.update(1)

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv("books.csv", index=False)

# End timing
end_time = time.time()
print(f"Scraping completed in {end_time - start_time:.2f} seconds. Data saved to books.csv.")

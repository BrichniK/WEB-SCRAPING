import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from multiprocessing import Pool, cpu_count

# Function to scrape a single page
def scrape_page(page_number):
    url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = []

    try:
        # Fetch the page content
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(page.text, "html.parser")

        # Check for 404 Not Found
        if soup.title and "404 Not Found" in soup.title.text:
            return data  # Return empty list for this page if it's 404

        # Extract book information
        all_books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
        for book in all_books:
            item = {
                'Title': book.find("img").attrs.get("alt", "N/A"),
                'Link': "https://books.toscrape.com/catalogue/" + book.find("a").attrs.get("href", ""),
                'Price': book.find("p", class_="price_color").text[2:],
                'Stock': book.find("p", class_="instock availability").text.strip(),
            }
            data.append(item)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")

    return data

# Function to collect data using multiprocessing
def scrape_all_pages(max_pages):
    with Pool(cpu_count()) as pool:
        # Create a list of page numbers to scrape
        page_numbers = list(range(1, max_pages + 1))

        # Use Pool's map function to scrape pages in parallel
        results = pool.map(scrape_page, page_numbers)

        # Flatten the list of results
        all_data = [item for sublist in results for item in sublist]

    return all_data

if __name__ == "__main__":
    start_time = time.time()
    max_pages_to_scrape = 50  # Set the maximum number of pages you want to scrape

    # Scrape pages using multiprocessing
    data = scrape_all_pages(max_pages_to_scrape)

    # Save the scraped data to a CSV file
    df = pd.DataFrame(data)
    df.to_csv("books_multiprocessing.csv", index=False)

    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time:.2f} seconds. Data saved to books_multiprocessing.csv.")

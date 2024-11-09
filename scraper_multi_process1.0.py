import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
from multiprocessing import Process, Queue, cpu_count

# Function to scrape a range of pages
def scrape_pages(start_page, end_page, queue):
    data = []
    #proceed = True

    # Scraping pages in the given range
    for current_page in range(start_page, end_page + 1):
        url = f"https://books.toscrape.com/catalogue/page-{current_page}.html"
        #print(f"Scraping page: {current_page}")

        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")

            # Stop if a 404 page is encountered
            if soup.title and soup.title.text == "404 Not Found":
                #proceed = False
                break

            all_books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

            # Extracting book data
            for book in all_books:
                item = {
                    'Title': book.find("img").attrs["alt"],
                    'Link': "https://books.toscrape.com/catalogue/" + book.find("a").attrs["href"],
                    'Price': book.find("p", class_="price_color").text[2:],
                    'Stock': book.find("p", class_="instock availability").text.strip()
                }
                data.append(item)

        except Exception as e:
            print(f"Error scraping page {current_page}: {e}")
    
    # Putting the scraped data into the queue
    queue.put(data)

# Main function to handle multiprocessing
def main():
    start_time = time.time()
    total_pages_to_scrape = 50
    pages_per_process = 5

    # Calculate the number of processes needed
    num_processes = (total_pages_to_scrape // pages_per_process) + 1
    queue = Queue()

    processes = []

    # Create a tqdm progress bar
    progress_bar = tqdm(total=total_pages_to_scrape, desc="Scraping Pages", unit="page")

    # Start multiprocessing
    for i in range(num_processes):
        start_page = i * pages_per_process + 1
        end_page = min((i + 1) * pages_per_process, total_pages_to_scrape)

        process = Process(target=scrape_pages, args=(start_page, end_page, queue))
        processes.append(process)
        process.start()

    # Collect data from all processes
    all_data = []
    for _ in range(num_processes):
        # Retrieve data from the queue
        process_data = queue.get()
        all_data.extend(process_data)
        progress_bar.update(pages_per_process)

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Save the collected data to a CSV file
    df = pd.DataFrame(all_data)
    df.to_csv("books.csv", index=False)

    end_time = time.time()
    print(f"\nScraping completed in {end_time - start_time:.2f} seconds. Data saved to books.csv.")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from textblob import TextBlob

start_time = time.time()

#base_url = "https://www.flipkart.com/wonderchef-9-litre-63153420-oven-toaster-grill-otg/product-reviews/itm753e80434b519?pid=OTNFYZ3Q3GUBGUWC&lid=LSTOTNFYZ3Q3GUBGUWCYRJJG2&marketplace=FLIPKART&page={}"
base_url = "https://www.flipkart.com/hp-uhs-i-u1-128-gb-microsdhc-class-10-100-mb-s-memory-card/product-reviews/itmdab1072034b04?pid=ACCF5ZYFFXUPXVZP&lid=LSTACCF5ZYFFXUPXVZP24LCNY&marketplace=FLIPKART"
def scrape_reviews(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    reviews = []
    authors = []

    review_elements = soup.find_all('div', class_='_27M-vq')
    for review_element in review_elements:
        author_element = review_element.find('p', class_='_2sc7ZR _2V5EHH')
        review_text_element = review_element.find('p', class_='_2-N8zT')

        if author_element and review_text_element:
            authors.append(author_element.text.strip())
            reviews.append(review_text_element.text.strip())

    return list(zip(authors, reviews))

def scrape_reviews_parallel(base_url, num_pages):
    all_reviews = []

    with ThreadPoolExecutor() as executor:
        page_urls = [base_url.format(page) for page in range(1, num_pages + 1)]
        results = executor.map(scrape_reviews, page_urls)

    for result in results:
        all_reviews.extend(result)

    return all_reviews

# Scraping 10 pages
num_pages_to_scrape = 20
all_reviews = scrape_reviews_parallel(base_url, num_pages_to_scrape)

csv_filename = 'product_reviews.csv'

# Writing to CSV file with only author, review, sentiment score, and status
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Author', 'Review', 'Sentiment Score', 'Status'])

    positive_count = 0
    neutral_count = 0
    negative_count = 0

    for author, review in all_reviews:
        analysis = TextBlob(review)
        sentiment_score = analysis.sentiment.polarity
        if sentiment_score > 0:
            status = 'Positive'
            positive_count += 1
        elif sentiment_score == 0:
            status = 'Neutral'
            neutral_count += 1
        else:
            status = 'Negative'
            negative_count += 1
        csv_writer.writerow([author, review, sentiment_score, status])

    total_reviews = len(all_reviews)
    positive_percentage = (positive_count / total_reviews) * 100
    neutral_percentage = (neutral_count / total_reviews) * 100
    negative_percentage = (negative_count / total_reviews) * 100

    print(f"Total Reviews: {total_reviews}")
    print(f"Positive: {positive_percentage:.2f}%")
    print(f"Neutral: {neutral_percentage:.2f}%")
    print(f"Negative: {negative_percentage:.2f}%")

print(f"Data saved to {csv_filename}")

print("Process finished --- %s seconds ---" % (time.time() - start_time))

import requests
from bs4 import BeautifulSoup
import csv

def scrape_product_listings(url, num_pages):
    data = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        product_blocks = soup.find_all('div', {'data-component-type': 's-search-result'})

        for block in product_blocks:
            product_url = 'https://www.amazon.in' + block.find('a', {'class': 'a-link-normal'})['href']
            product_name = block.find('span', {'class': 'a-text-normal'}).get_text(strip=True)
            product_price = block.find('span', {'class': 'a-offscreen'}).get_text(strip=True)

            try:
                product_rating = block.find('span', {'class': 'a-icon-alt'}).get_text(strip=True).split()[0]
            except AttributeError:
                product_rating = "No rating"

            try:
                product_reviews = block.find('span', {'class': 'a-size-base'}).get_text(strip=True)
            except AttributeError:
                product_reviews = "No reviews"

            product_data = {
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': product_rating,
                'Number of Reviews': product_reviews,
            }

            data.append(product_data)

    return data

def scrape_product_details(product_data):
    for product in product_data:
        response = requests.get(product['Product URL'])
        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            product_description = soup.find('div', {'id': 'productDescription'}).get_text(strip=True)
        except AttributeError:
            product_description = "No description"

        try:
            asin = soup.find('th', text='ASIN').find_next('td').get_text(strip=True)
        except AttributeError:
            asin = "N/A"

        try:
            manufacturer = soup.find('th', text='Manufacturer').find_next('td').get_text(strip=True)
        except AttributeError:
            manufacturer = "N/A"

        product.update({
            'Description': product_description,
            'ASIN': asin,
            'Manufacturer': manufacturer,
        })

def save_to_csv(data):
    with open('amazon_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
                      'Description', 'ASIN', 'Manufacturer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    amazon_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    num_pages_to_scrape = 20

    product_data = scrape_product_listings(amazon_url, num_pages_to_scrape)
    scrape_product_details(product_data)
    save_to_csv(product_data)

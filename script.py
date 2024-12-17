import requests
from bs4 import BeautifulSoup
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_amazon_product_details(asin):
    """
    Scrape product details from Amazon using the product ASIN
    
    :param asin: Amazon Standard Identification Number
    :return: Dictionary containing product details
    """
    # Amazon product URL
    url = f"https://www.amazon.in/dp/{asin}"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        logging.info(f"Fetching product details for ASIN: {asin}")
        
        # Send GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product title
        title_elem = soup.find('span', {'id': 'productTitle'})
        title = title_elem.get_text(strip=True) if title_elem else 'Title not found'
        
        # Extract product price
        price_whole_elem = soup.find('span', {'class': 'a-price-whole'})
        price_symbol_elem = soup.find('span', {'class': 'a-price-symbol'})
        price = f"{price_symbol_elem.get_text(strip=True) if price_symbol_elem else '₹'}{price_whole_elem.get_text(strip=True) if price_whole_elem else 'Price not found'}"
        
        # Extract product attributes
        attributes = {}
        product_details_div = soup.find('div', {'id': 'prodDetails'})
        if product_details_div:
            for table in product_details_div.find_all('table'):
                for row in table.find_all('tr'):
                    key = row.find('th')
                    value = row.find('td')
                    if key and value:
                        attributes[key.get_text(strip=True)] = value.get_text(strip=True)
        
        # Extract bullet points
        bullet_points = []
        feature_bullets_div = soup.find('div', {'id': 'feature-bullets'})
        if feature_bullets_div:
            bullet_points = [
                li.get_text(strip=True)
                for li in feature_bullets_div.find_all('li') if li.get_text(strip=True)
            ]
        
        # Extract top reviews
        top_reviews = extract_top_reviews(soup)
        
        # Combine all details
        product_details = {
            'ASIN': asin,
            'Title': title,
            'Price': price,
            'Attributes': attributes,
            'BulletPoints': bullet_points,
            'TopReviews': top_reviews
        }
        
        return product_details
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product details: {e}")
        return None

def extract_top_reviews(soup):
    """
    Extract the top reviews for the product
    
    :param soup: BeautifulSoup object of the page
    :return: List of top review details
    """
    top_reviews = []
    reviews_section = soup.find_all('div', {'data-hook': 'review'})
    
    if reviews_section:
        for review_elem in reviews_section:
            try:
                review = {
                    'Title': review_elem.find('a', {'data-hook': 'review-title'}).get_text(strip=True) if review_elem.find('a', {'data-hook': 'review-title'}) else 'No Title',
                    'Rating': float(review_elem.find('i', {'data-hook': 'review-star-rating'}).get_text(strip=True).split()[0]) if review_elem.find('i', {'data-hook': 'review-star-rating'}) else 'No Rating',
                    'Author': review_elem.find('span', {'class': 'a-profile-name'}).get_text(strip=True) if review_elem.find('span', {'class': 'a-profile-name'}) else 'No Author',
                    'ReviewText': review_elem.find('span', {'data-hook': 'review-body'}).get_text(strip=True) if review_elem.find('span', {'data-hook': 'review-body'}) else 'No Review Text'
                }
                top_reviews.append(review)
            except Exception as e:
                logging.warning(f"Error parsing a review: {e}")
    
    return top_reviews

def save_product_details(product_details, filename='product_details.json'):
    """
    Save product details to a JSON file
    
    :param product_details: Dictionary of product details
    :param filename: Output filename
    """
    if product_details:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(product_details, f, indent=4, ensure_ascii=False)
        logging.info(f"Product details saved to {filename}")

# Example usage
if __name__ == "__main__":
    # ASIN of the product
    product_asin = "B07TFD2THQ"
    
    # Fetch and print product details
    product_details = get_amazon_product_details(product_asin)
    
    if product_details:
        # Print details to console
        print(json.dumps(product_details, indent=4, ensure_ascii=False))
        
        # Save to JSON file
        save_product_details(product_details)

import requests
from bs4 import BeautifulSoup
import json
import re

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
        
        # Extract product attributes from the overview table
        attributes = {}
        overview_table = soup.find('table', {'class': 'a-normal'})
        if overview_table:
            for row in overview_table.find_all('tr'):
                key_elem = row.find('td', {'class': 'a-span3'})
                value_elem = row.find('td', {'class': 'a-span9'})
                
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    attributes[key] = value
        
        # Extract product bullet points
        bullet_points = []
        feature_bullets_div = soup.find('div', {'id': 'feature-bullets'})
        if feature_bullets_div:
            # Look for main bullet points
            main_ul = feature_bullets_div.find('ul', {'class': 'a-unordered-list'})
            if main_ul:
                bullet_points.extend([
                    li.get_text(strip=True) 
                    for li in main_ul.find_all('li', {'class': 'a-spacing-mini'})
                ])
            
            # Look for additional bullet points in expanded section
            expanded_ul = feature_bullets_div.find('ul', {'class': 'a-unordered-list a-vertical a-spacing-none'})
            if expanded_ul:
                bullet_points.extend([
                    li.get_text(strip=True) 
                    for li in expanded_ul.find_all('li', {'class': 'a-spacing-mini'})
                ])
        
        # Extract product information
        product_info_elem = soup.find('div', {'id': 'prodDetails'})
        product_info = product_info_elem.get_text(strip=True) if product_info_elem else ''
        
        # Extract top reviews
        top_reviews = extract_top_reviews(soup)
        
        # Combine all details
        product_details = {
            'ASIN': asin,
            'Title': title,
            'Price': price,
            'Attributes': attributes,
            'BulletPoints': bullet_points,
            'ProductInfo': product_info,
            'TopReviews': top_reviews
        }
        
        return product_details
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product details: {e}")
        return None

def extract_top_reviews(soup):
    """
    Extract the top reviews for the product
    
    :param soup: BeautifulSoup object of the page
    :return: List of top review details
    """
    top_reviews = []
    
    # Find the top review section
    top_review_section = soup.find('div', {'data-hook': 'top-review'})
    if top_review_section:
        # Extract each top review
        for review_elem in top_review_section.find_all('div', {'data-hook': 'review'}):
            review = {
                'Title': review_elem.find('a', {'data-hook': 'review-title'}).get_text(strip=True),
                'Rating': float(review_elem.find('i', {'data-hook': 'review-star-rating'}).get_text(strip=True)[0]),
                'Author': review_elem.find('span', {'class': 'a-profile-name'}).get_text(strip=True),
                'ReviewText': review_elem.find('span', {'data-hook': 'review-body'}).get_text(strip=True)
            }
            top_reviews.append(review)
    
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
        print(f"Product details saved to {filename}")

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
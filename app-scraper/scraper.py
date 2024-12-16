import requests
from bs4 import BeautifulSoup

def get_amazon_product_details(asin):
    """
    Scrape product details from Amazon using the product ASIN.

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
        
        # Extract product attributes
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
            bullet_points = [
                li.get_text(strip=True) 
                for li in feature_bullets_div.find_all('li')
            ]
        
        # Combine all details into a dictionary
        product_details = {
            'ASIN': asin,
            'Title': title,
            'Price': price,
            'Attributes': attributes,
            'BulletPoints': bullet_points,
        }
        
        return product_details
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product details: {e}")
        return None

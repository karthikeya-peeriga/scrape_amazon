import os
import csv
import logging
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from flask import Flask, send_file, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_amazon_product_details(asin: str) -> Optional[Dict]:
    """
    Scrape product details from Amazon using the product ASIN
    
    :param asin: Amazon Standard Identification Number
    :return: Dictionary containing product details
    """
    # Amazon product URL (using .in domain, can be parameterized if needed)
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
        logger.info(f"Fetching product details for ASIN: {asin}")
        
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
        
        # Combine all details
        product_details = {
            'asin': asin,
            'title': title,
            'price': price,
            'attributes': attributes,
            'bullet_points': bullet_points
        }
        
        return product_details
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching product details: {e}")
        return None

def process_asins(asins: List[str]) -> List[Dict]:
    """
    Process a list of ASINs and return their details
    
    :param asins: List of Amazon Standard Identification Numbers
    :return: List of product details or error information
    """
    results = []
    for asin in asins:
        try:
            # Attempt to scrape product details
            product_data = get_amazon_product_details(asin)
            
            if product_data:
                # Successfully scraped
                results.append(product_data)
            else:
                # Failed to scrape
                results.append({
                    'asin': asin,
                    'error': 'Unable to fetch product details'
                })
        except Exception as e:
            # Catch any unexpected errors
            results.append({
                'asin': asin,
                'error': str(e)
            })
    
    return results

def process_csv_asins(filepath: str) -> List[Dict]:
    """
    Process ASINs from uploaded CSV file
    
    :param filepath: Path to uploaded CSV file
    :return: List of scraped product details
    """
    asins = []
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip header row
        for row in reader:
            # Assuming first column is ASIN
            if row and row[0].strip():
                asins.append(row[0].strip())
    
    return process_asins(asins)

# Create Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for API calls

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape/manual', methods=['POST'])
def scrape_manual():
    """
    Handle manual ASIN scraping request
    """
    asins = request.json.get('asins', [])
    results = process_asins(asins)
    return jsonify(results)

@app.route('/scrape/bulk', methods=['POST'])
def scrape_bulk():
    """
    Handle bulk ASIN scraping from uploaded CSV
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        results = process_csv_asins(filepath)
        return jsonify(results)

@app.route('/download/asin_template')
def download_asin_template():
    """
    Generate and send a CSV template with 'ASINS' column
    """
    # Create a CSV in memory
    output = BytesIO()
    
    # Create a CSV writer
    writer = csv.writer(output)
    
    # Write the header
    writer.writerow(['ASINS'])
    
    # Example ASINs
    example_asins = [
        'B07TFD2THQ',
        'B08N5KWB9V',
        'B09X7XJHBZ'
    ]
    
    # Write example ASINs
    for asin in example_asins:
        writer.writerow([asin])
    
    # Move to the beginning of the file
    output.seek(0)
    
    # Send the file as a downloadable attachment
    return send_file(
        output, 
        mimetype='text/csv', 
        as_attachment=True, 
        download_name='asin_template.csv'
    )

@app.route('/download/template.csv')
def download_template_csv():
    """
    Send the template CSV file for ASIN upload
    """
    template_path = os.path.join(os.path.dirname(__file__), 'template.csv')
    
    try:
        return send_file(
            template_path, 
            mimetype='text/csv', 
            as_attachment=True, 
            download_name='template.csv'
        )
    except FileNotFoundError:
        return jsonify({'error': 'Template file not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
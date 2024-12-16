from flask import Flask, render_template, request, jsonify
from scraper import get_amazon_product_details

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    asin = request.form.get('asin')
    if not asin:
        return jsonify({'error': 'ASIN is required'}), 400
    
    # Fetch product details
    product_details = get_amazon_product_details(asin)
    
    if not product_details:
        return jsonify({'error': 'Failed to fetch product details. Please try again.'}), 500
    
    return jsonify(product_details)

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------------
# All-in-One Fuel & Metal Price API - Nexxon Hackers Edition
# FIXED VERSION - Actually Working with GoodReturns HTML
# ------------------------------------------------------------

from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# ---------------- CONFIG ----------------
COPYRIGHT_STRING = "Creator Shyamchand & Ayan - CEO & Founder Of - Nexxon Hackers"

CITY_SLUGS = {
    "murshidabad": "murshidabad", "kolkata": "kolkata", "delhi": "delhi",
    "mumbai": "mumbai", "chennai": "chennai", "bangalore": "bangalore",
    "hyderabad": "hyderabad", "pune": "pune", "ahmedabad": "ahmedabad"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# ---------------- HTML TEMPLATE (Same as before, keeping it short here) ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fuel & Metal Price API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<style>
.loading-spinner { border: 2px solid #f3f3f3; border-top: 2px solid #f59e0b; border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.json-viewer { background: #1e1e1e; border-radius: 8px; padding: 16px; overflow-x: auto; font-family: monospace; font-size: 13px; max-height: 500px; }
.json-key { color: #9cdcfe; } .json-string { color: #ce9178; } .json-number { color: #b5cea8; }
.tab-active { background: #f59e0b !important; color: white !important; }
.gradient-bg { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); }
</style>
</head>
<body class="bg-gradient-to-br from-amber-50 via-white to-orange-50 min-h-screen">
<main class="pt-8 pb-12 px-4 max-w-6xl mx-auto">
    <header class="text-center py-8">
        <div class="inline-flex items-center justify-center w-20 h-20 gradient-bg rounded-3xl mb-6 shadow-lg">
            <i class="ri-gas-station-line text-white ri-3x"></i>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Fuel & Metal Price API</h1>
        <p class="text-lg text-gray-600 mb-2">All-in-One Price Tracker for India</p>
        <p class="text-sm text-gray-500">Petrol • Diesel • LPG • Gold • Silver • Platinum</p>
    </header>

    <section class="mb-8 bg-white rounded-3xl p-6 shadow-xl border border-amber-100">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Live API Test</h2>
        <div class="flex gap-2 mb-4 border-b border-gray-200">
            <button id="tabAll" class="tab-active px-4 py-2 rounded-t-lg font-medium text-sm">All</button>
            <button id="tabPetrol" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600">Petrol</button>
            <button id="tabDiesel" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600">Diesel</button>
            <button id="tabGold" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600">Gold</button>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <select id="citySelect" class="px-4 py-3 border rounded-lg">
                <option value="murshidabad">Murshidabad</option><option value="kolkata">Kolkata</option>
                <option value="delhi">Delhi</option><option value="mumbai">Mumbai</option>
            </select>
            <button id="searchBtn" class="gradient-bg text-white px-6 py-3 rounded-lg font-medium">Get Prices</button>
        </div>
        <div id="responseContainer" class="hidden">
            <div class="flex justify-between mb-2"><span class="text-sm">Response:</span><button id="copyBtn" class="text-xs">Copy</button></div>
            <pre id="responseDisplay" class="json-viewer"></pre>
        </div>
        <div id="loadingIndicator" class="hidden text-center py-8"><div class="loading-spinner"></div><span class="ml-3">Fetching...</span></div>
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-xl p-4 text-red-700"></div>
    </section>

    <div class="text-center py-6">
        <div class="inline-block gradient-bg text-white px-8 py-4 rounded-2xl shadow-lg">
            <p class="font-bold text-lg">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-sm opacity-95">CEO & Founder Of - Nexxon Hackers</p>
        </div>
    </div>
</main>
<script>
function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function(m) {
        let cls = 'json-number';
        if (/^"/.test(m)) cls = m.includes(':') ? 'json-key' : 'json-string';
        else if (/true|false/.test(m)) cls = 'json-boolean';
        else if (/null/.test(m)) cls = 'json-null';
        return '<span class="' + cls + '">' + m + '</span>';
    });
}
async function fetchData(url) {
    document.getElementById('responseContainer').classList.add('hidden');
    document.getElementById('errorDisplay').classList.add('hidden');
    document.getElementById('loadingIndicator').classList.remove('hidden');
    try {
        const res = await fetch(url);
        const data = await res.json();
        document.getElementById('loadingIndicator').classList.add('hidden');
        document.getElementById('responseDisplay').innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
        document.getElementById('responseContainer').classList.remove('hidden');
    } catch(e) {
        document.getElementById('loadingIndicator').classList.add('hidden');
        document.getElementById('errorDisplay').textContent = 'Error: ' + e.message;
        document.getElementById('errorDisplay').classList.remove('hidden');
    }
}
let currentTab = 'all';
document.querySelectorAll('[id^="tab"]').forEach(t => t.addEventListener('click', function() {
    document.querySelectorAll('[id^="tab"]').forEach(bt => bt.className = 'px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600');
    this.className = 'tab-active px-4 py-2 rounded-t-lg font-medium text-sm';
    currentTab = this.id.replace('tab', '').toLowerCase();
}));
document.getElementById('searchBtn').addEventListener('click', () => {
    const city = document.getElementById('citySelect').value;
    fetchData('/api/' + (currentTab === 'all' ? 'all' : currentTab) + '?city=' + city);
});
document.getElementById('copyBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(document.getElementById('responseDisplay').textContent);
    document.getElementById('copyBtn').innerHTML = '✓ Copied!';
    setTimeout(() => document.getElementById('copyBtn').innerHTML = 'Copy', 2000);
});
</script>
</body>
</html>
'''

# ---------------- WORKING SCRAPERS ----------------
def extract_price(text):
    """Extract price from text like '₹106.53 / Ltr' or '₹ 14,234/gm'"""
    if not text:
        return None
    match = re.search(r'₹\s*([\d,]+\.?\d*)', text.replace(',', ''))
    if match:
        return float(match.group(1))
    return None

def scrape_petrol(city="murshidabad"):
    """Scrape petrol price - WORKING"""
    url = f"https://www.goodreturns.in/petrol-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Method 1: Find the big price display
        price_div = soup.find("div", class_="fuel-price-display")
        if not price_div:
            price_div = soup.find("div", string=re.compile(r"₹[\d,]+\.?\d*\s*/"))
        
        price = None
        if price_div:
            price = extract_price(price_div.get_text(strip=True))
        
        # Method 2: Look for "Today's petrol price" text
        if not price:
            today_text = soup.find(string=re.compile(r"Today's petrol price.*?₹"))
            if today_text:
                price = extract_price(today_text)
        
        # Method 3: Look in meta tags
        if not price:
            meta_price = soup.find("meta", {"property": "og:description"})
            if meta_price:
                content = meta_price.get("content", "")
                price = extract_price(content)
        
        # Extract last 10 days from table
        history = []
        table = soup.find("table", class_="price-table")
        if not table:
            table = soup.find("table")
        
        if table:
            rows = table.find_all("tr")[1:11]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    date = cols[0].get_text(strip=True)
                    p = extract_price(cols[1].get_text(strip=True))
                    if p:
                        history.append({"date": date, "price": p})
        
        return {
            "city": city.title(),
            "price_per_litre": price,
            "currency": "INR",
            "last_10_days": history
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_diesel(city="murshidabad"):
    """Scrape diesel price - WORKING"""
    url = f"https://www.goodreturns.in/diesel-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        price = None
        # Look for price in various places
        price_div = soup.find("div", class_="fuel-price-display")
        if price_div:
            price = extract_price(price_div.get_text(strip=True))
        
        if not price:
            today_text = soup.find(string=re.compile(r"Today's diesel price.*?₹"))
            if today_text:
                price = extract_price(today_text)
        
        history = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:11]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    date = cols[0].get_text(strip=True)
                    p = extract_price(cols[1].get_text(strip=True))
                    if p:
                        history.append({"date": date, "price": p})
        
        return {
            "city": city.title(),
            "price_per_litre": price,
            "currency": "INR",
            "last_10_days": history
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_lpg(city="murshidabad"):
    """Scrape LPG price - WORKING"""
    url = f"https://www.goodreturns.in/lpg-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        domestic = None
        commercial = None
        
        # Look for the price table
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                text = row.get_text(strip=True)
                if "Domestic" in text:
                    domestic = extract_price(text)
                elif "Commercial" in text:
                    commercial = extract_price(text)
        
        # Alternative: look for price divs
        if not domestic:
            price_divs = soup.find_all("div", class_="price-display")
            for div in price_divs:
                text = div.get_text(strip=True)
                if "Domestic" in text or "14.2" in text:
                    domestic = extract_price(text)
                elif "Commercial" in text or "19" in text:
                    commercial = extract_price(text)
        
        return {
            "city": city.title(),
            "domestic_14kg": domestic,
            "commercial_19kg": commercial,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_gold():
    """Scrape gold prices - WORKING"""
    url = "https://www.goodreturns.in/gold-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        prices = {"24k": None, "22k": None, "18k": None}
        
        # Method 1: Look for the gold rate cards
        cards = soup.find_all("div", class_="gold-rate-card")
        for card in cards:
            text = card.get_text(strip=True)
            if "24K" in text or "24 Carat" in text:
                prices["24k"] = extract_price(text)
            elif "22K" in text or "22 Carat" in text:
                prices["22k"] = extract_price(text)
            elif "18K" in text or "18 Carat" in text:
                prices["18k"] = extract_price(text)
        
        # Method 2: Look in header with prices
        if not any(prices.values()):
            header_prices = soup.find_all("span", class_="gold-price")
            for i, span in enumerate(header_prices):
                price = extract_price(span.get_text(strip=True))
                if price:
                    if i == 0:
                        prices["24k"] = price
                    elif i == 1:
                        prices["22k"] = price
                    elif i == 2:
                        prices["18k"] = price
        
        # Method 3: Extract from top bar text
        if not any(prices.values()):
            top_bar = soup.find("div", class_="top-bar-prices")
            if top_bar:
                text = top_bar.get_text(strip=True)
                matches = re.findall(r'(\d{2}K?)\s*Gold?\s*₹\s*([\d,]+)', text)
                for purity, price_str in matches:
                    p = float(price_str.replace(',', ''))
                    if "24" in purity:
                        prices["24k"] = p
                    elif "22" in purity:
                        prices["22k"] = p
                    elif "18" in purity:
                        prices["18k"] = p
        
        return {"prices_per_gram": prices, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_silver():
    """Scrape silver prices - WORKING"""
    url = "https://www.goodreturns.in/silver-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        price_per_gram = None
        price_per_kg = None
        
        # Look for silver price displays
        text = soup.get_text()
        
        # Extract per gram
        match = re.search(r'Silver\s*[/]\s*g\s*₹\s*([\d,]+\.?\d*)', text)
        if match:
            price_per_gram = float(match.group(1).replace(',', ''))
        
        # Extract per kg
        match = re.search(r'Silver\s*[/]\s*kg\s*₹\s*([\d,]+\.?\d*)', text)
        if match:
            price_per_kg = float(match.group(1).replace(',', ''))
        
        # Alternative from tables
        if not price_per_gram:
            tables = soup.find_all("table")
            for table in tables:
                if "Silver" in table.get_text():
                    rows = table.find_all("tr")
                    for row in rows:
                        row_text = row.get_text(strip=True)
                        if "gram" in row_text.lower():
                            price_per_gram = extract_price(row_text)
                        elif "kg" in row_text.lower():
                            price_per_kg = extract_price(row_text)
        
        return {
            "price_per_gram": price_per_gram,
            "price_per_kg": price_per_kg,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_platinum():
    """Scrape platinum prices - WORKING"""
    url = "https://www.goodreturns.in/platinum-price.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        price_per_gram = None
        price_per_10g = None
        
        text = soup.get_text()
        
        # Extract per gram
        match = re.search(r'Platinum\s*[/]\s*g\s*₹\s*([\d,]+\.?\d*)', text)
        if match:
            price_per_gram = float(match.group(1).replace(',', ''))
        
        # Extract per 10g
        match = re.search(r'Platinum\s*[/]\s*10g\s*₹\s*([\d,]+\.?\d*)', text)
        if match:
            price_per_10g = float(match.group(1).replace(',', ''))
        
        return {
            "price_per_gram": price_per_gram,
            "price_per_10g": price_per_10g,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

# ---------------- API ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/all")
def api_all():
    city = request.args.get("city", "murshidabad")
    result = OrderedDict()
    result["city"] = city.title()
    result["checked_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    result["petrol"] = scrape_petrol(city)
    result["diesel"] = scrape_diesel(city)
    result["lpg"] = scrape_lpg(city)
    result["gold"] = scrape_gold()
    result["silver"] = scrape_silver()
    result["platinum"] = scrape_platinum()
    result["copyright"] = COPYRIGHT_STRING
    return app.response_class(response=json.dumps(result, ensure_ascii=False, indent=2), mimetype='application/json')

@app.route("/api/petrol")
def api_petrol():
    city = request.args.get("city", "murshidabad")
    result = scrape_petrol(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/diesel")
def api_diesel():
    city = request.args.get("city", "murshidabad")
    result = scrape_diesel(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/lpg")
def api_lpg():
    city = request.args.get("city", "murshidabad")
    result = scrape_lpg(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/gold")
def api_gold():
    result = scrape_gold()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/silver")
def api_silver():
    result = scrape_silver()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/platinum")
def api_platinum():
    result = scrape_platinum()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "copyright": COPYRIGHT_STRING}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

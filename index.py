# ------------------------------------------------------------
# All-in-One Fuel & Metal Price API - Nexxon Hackers Edition
# Developed by: Creator Shyamchand & Ayan
# Organization: CEO & Founder Of - Nexxon Hackers
# Purpose: Fetch Petrol, Diesel, LPG, Gold, Silver, Platinum Prices
# Data Source: GoodReturns.in
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

# City slug mapping for URLs
CITY_SLUGS = {
    "murshidabad": "murshidabad",
    "kolkata": "kolkata", 
    "delhi": "delhi",
    "mumbai": "mumbai",
    "chennai": "chennai",
    "bangalore": "bangalore",
    "hyderabad": "hyderabad",
    "pune": "pune",
    "ahmedabad": "ahmedabad",
    "jaipur": "jaipur",
    "lucknow": "lucknow",
    "patna": "patna",
    "bhopal": "bhopal",
    "chandigarh": "chandigarh",
    "bhubaneswar": "bhubaneswar"
}

# ---------------- HTML TEMPLATE ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fuel & Metal Price API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<script>tailwind.config={theme:{extend:{colors:{primary:'#f59e0b',secondary:'#d97706'},borderRadius:{'none':'0px','sm':'4px',DEFAULT:'8px','md':'12px','lg':'16px','xl':'20px','2xl':'24px','3xl':'32px','full':'9999px','button':'8px'}}}}</script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<style>
.loading-spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #f59e0b;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    display: inline-block;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.json-viewer {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.5;
    max-height: 500px;
}
.json-key { color: #9cdcfe; }
.json-string { color: #ce9178; }
.json-number { color: #b5cea8; }
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

    <!-- Live Test Section -->
    <section class="mb-8 bg-white rounded-3xl p-6 shadow-xl border border-amber-100">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <i class="ri-flask-line text-primary mr-2"></i>
            Live API Test
        </h2>
        
        <div class="flex gap-2 mb-4 border-b border-gray-200">
            <button id="tabAll" class="tab-active px-4 py-2 rounded-t-lg font-medium text-sm transition" onclick="switchTab('all')">
                <i class="ri-global-line mr-1"></i> All Prices
            </button>
            <button id="tabPetrol" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600 hover:bg-gray-100 transition" onclick="switchTab('petrol')">
                <i class="ri-gas-station-line mr-1"></i> Petrol
            </button>
            <button id="tabDiesel" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600 hover:bg-gray-100 transition" onclick="switchTab('diesel')">
                <i class="ri-truck-line mr-1"></i> Diesel
            </button>
            <button id="tabLPG" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600 hover:bg-gray-100 transition" onclick="switchTab('lpg')">
                <i class="ri-fire-line mr-1"></i> LPG
            </button>
            <button id="tabGold" class="px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600 hover:bg-gray-100 transition" onclick="switchTab('gold')">
                <i class="ri-copper-coin-line mr-1"></i> Gold
            </button>
        </div>
        
        <div id="allForm">
            <div class="flex flex-col sm:flex-row gap-3 mb-4">
                <select id="citySelect" class="px-4 py-3 border border-gray-300 rounded-lg">
                    <option value="murshidabad">Murshidabad</option>
                    <option value="kolkata">Kolkata</option>
                    <option value="delhi">Delhi</option>
                    <option value="mumbai">Mumbai</option>
                    <option value="chennai">Chennai</option>
                    <option value="bangalore">Bangalore</option>
                    <option value="hyderabad">Hyderabad</option>
                </select>
                <button id="allBtn" class="gradient-bg text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition flex items-center justify-center gap-2">
                    <i class="ri-search-line"></i>
                    <span>Get All Prices</span>
                </button>
            </div>
        </div>
        
        <div id="responseContainer" class="hidden">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Response:</span>
                <button id="copyBtn" class="text-xs text-primary hover:text-secondary flex items-center gap-1">
                    <i class="ri-file-copy-line"></i> Copy JSON
                </button>
            </div>
            <pre id="responseDisplay" class="json-viewer"></pre>
        </div>
        
        <div id="loadingIndicator" class="hidden text-center py-8">
            <div class="loading-spinner w-8 h-8"></div>
            <span class="ml-3 text-gray-500">Fetching price data...</span>
        </div>
        
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-xl p-4 text-red-700"></div>
    </section>

    <!-- Documentation -->
    <section class="mb-8 bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h2 class="text-xl font-bold text-gray-900 mb-4">API Endpoints</h2>
        
        <div class="space-y-4">
            <div class="border-l-4 border-amber-500 pl-4">
                <h3 class="font-semibold text-gray-900">Get All Prices</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/all?city=murshidabad</code>
                <p class="text-sm text-gray-600 mt-1">Returns Petrol, Diesel, LPG, Gold, Silver, Platinum prices</p>
            </div>
            <div class="border-l-4 border-green-500 pl-4">
                <h3 class="font-semibold text-gray-900">Petrol Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/petrol?city=murshidabad</code>
            </div>
            <div class="border-l-4 border-blue-500 pl-4">
                <h3 class="font-semibold text-gray-900">Diesel Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/diesel?city=murshidabad</code>
            </div>
            <div class="border-l-4 border-red-500 pl-4">
                <h3 class="font-semibold text-gray-900">LPG Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/lpg?city=murshidabad</code>
            </div>
            <div class="border-l-4 border-yellow-500 pl-4">
                <h3 class="font-semibold text-gray-900">Gold Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/gold</code>
            </div>
            <div class="border-l-4 border-gray-400 pl-4">
                <h3 class="font-semibold text-gray-900">Silver Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/silver</code>
            </div>
            <div class="border-l-4 border-purple-500 pl-4">
                <h3 class="font-semibold text-gray-900">Platinum Price</h3>
                <code class="text-sm bg-gray-100 px-2 py-1 rounded">GET /api/platinum</code>
            </div>
        </div>
    </section>

    <div class="text-center py-6">
        <div class="inline-block gradient-bg text-white px-8 py-4 rounded-2xl shadow-lg">
            <p class="font-bold text-lg">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-sm opacity-95">CEO & Founder Of - Nexxon Hackers</p>
        </div>
    </div>

</main>

<script>
function switchTab(tab) {
    document.querySelectorAll('[id^="tab"]').forEach(t => {
        t.className = 'px-4 py-2 rounded-t-lg font-medium text-sm text-gray-600 hover:bg-gray-100 transition';
    });
    document.getElementById('tab' + tab.charAt(0).toUpperCase() + tab.slice(1)).className = 'tab-active px-4 py-2 rounded-t-lg font-medium text-sm transition';
    
    // Update button action
    const btn = document.getElementById('allBtn');
    const citySelect = document.getElementById('citySelect');
    
    if (tab === 'all') {
        btn.onclick = () => fetchData('/api/all?city=' + citySelect.value);
    } else if (tab === 'gold' || tab === 'silver' || tab === 'platinum') {
        btn.onclick = () => fetchData('/api/' + tab);
        citySelect.disabled = true;
    } else {
        btn.onclick = () => fetchData('/api/' + tab + '?city=' + citySelect.value);
        citySelect.disabled = false;
    }
}

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {
        var cls = 'json-number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'json-key';
                match = match.slice(0, -1) + '</span>:';
                return '<span class="' + cls + '">' + match;
            } else {
                cls = 'json-string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'json-boolean';
        } else if (/null/.test(match)) {
            cls = 'json-null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

async function fetchData(url) {
    const responseContainer = document.getElementById('responseContainer');
    const responseDisplay = document.getElementById('responseDisplay');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorDisplay = document.getElementById('errorDisplay');
    
    responseContainer.classList.add('hidden');
    errorDisplay.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        loadingIndicator.classList.add('hidden');
        
        const jsonStr = JSON.stringify(data, null, 2);
        responseDisplay.innerHTML = syntaxHighlight(jsonStr);
        responseContainer.classList.remove('hidden');
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        errorDisplay.textContent = 'Error: ' + error.message;
        errorDisplay.classList.remove('hidden');
    }
}

document.getElementById('allBtn').addEventListener('click', () => fetchData('/api/all?city=' + document.getElementById('citySelect').value));
document.getElementById('copyBtn').addEventListener('click', function() {
    const text = document.getElementById('responseDisplay').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        btn.innerHTML = '<i class="ri-check-line"></i> Copied!';
        setTimeout(() => btn.innerHTML = '<i class="ri-file-copy-line"></i> Copy JSON', 2000);
    });
});
</script>
</body>
</html>
'''

# ---------------- SCRAPER FUNCTIONS ----------------
def extract_price_from_html(html, pattern, is_lpg=False):
    """Extract price from HTML using regex pattern"""
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        price_str = match.group(1).replace(',', '').replace('₹', '').strip()
        try:
            return float(price_str) if '.' in price_str else int(price_str)
        except:
            return price_str
    return None

def scrape_petrol(city="murshidabad"):
    """Scrape petrol price for a city"""
    city_slug = CITY_SLUGS.get(city.lower(), city.lower().replace(' ', '-'))
    url = f"https://www.goodreturns.in/petrol-price-in-{city_slug}.html"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract current price from the highlighted box
        price_elem = soup.find("div", class_="fuel-price")
        if not price_elem:
            price_elem = soup.find("strong", string=re.compile(r"₹"))
        
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', price_text)
            if match:
                price = float(match.group(1).replace(',', ''))
        
        # Extract last 10 days data
        history = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:11]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    date = cols[0].get_text(strip=True)
                    price_match = re.search(r'₹([\d,]+\.?\d*)', cols[1].get_text(strip=True))
                    if price_match:
                        history.append({
                            "date": date,
                            "price": float(price_match.group(1).replace(',', ''))
                        })
        
        return {
            "city": city.title(),
            "price_per_litre": price,
            "currency": "INR",
            "last_10_days": history[:10]
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_diesel(city="murshidabad"):
    """Scrape diesel price for a city"""
    city_slug = CITY_SLUGS.get(city.lower(), city.lower().replace(' ', '-'))
    url = f"https://www.goodreturns.in/diesel-price-in-{city_slug}.html"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_elem = soup.find("div", class_="fuel-price")
        if not price_elem:
            price_elem = soup.find("strong", string=re.compile(r"₹"))
        
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', price_text)
            if match:
                price = float(match.group(1).replace(',', ''))
        
        history = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:11]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    date = cols[0].get_text(strip=True)
                    price_match = re.search(r'₹([\d,]+\.?\d*)', cols[1].get_text(strip=True))
                    if price_match:
                        history.append({
                            "date": date,
                            "price": float(price_match.group(1).replace(',', ''))
                        })
        
        return {
            "city": city.title(),
            "price_per_litre": price,
            "currency": "INR",
            "last_10_days": history[:10]
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_lpg(city="murshidabad"):
    """Scrape LPG price for a city"""
    city_slug = CITY_SLUGS.get(city.lower(), city.lower().replace(' ', '-'))
    url = f"https://www.goodreturns.in/lpg-price-in-{city_slug}.html"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract domestic LPG price
        domestic_price = None
        commercial_price = None
        
        price_elems = soup.find_all("div", class_="fuel-price")
        for elem in price_elems:
            text = elem.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', text)
            if match:
                if "Domestic" in str(elem.parent) or not domestic_price:
                    domestic_price = float(match.group(1).replace(',', ''))
                else:
                    commercial_price = float(match.group(1).replace(',', ''))
        
        return {
            "city": city.title(),
            "domestic_14kg": domestic_price,
            "commercial_19kg": commercial_price,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_gold():
    """Scrape gold prices"""
    url = "https://www.goodreturns.in/gold-rates/"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        prices = {"24k": None, "22k": None, "18k": None}
        
        # Look for price elements
        price_divs = soup.find_all("div", class_="gold-price")
        for div in price_divs:
            text = div.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', text)
            if match:
                price = float(match.group(1).replace(',', ''))
                if "24K" in str(div.parent) or "24k" in text.lower():
                    prices["24k"] = price
                elif "22K" in str(div.parent) or "22k" in text.lower():
                    prices["22k"] = price
                elif "18K" in str(div.parent) or "18k" in text.lower():
                    prices["18k"] = price
        
        return {
            "prices_per_gram": prices,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_silver():
    """Scrape silver prices"""
    url = "https://www.goodreturns.in/silver-rates/"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_per_gram = None
        price_per_kg = None
        
        price_elems = soup.find_all("div", class_="silver-price")
        for elem in price_elems:
            text = elem.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', text)
            if match:
                price = float(match.group(1).replace(',', ''))
                if "kg" in text.lower() or price > 10000:
                    price_per_kg = price
                else:
                    price_per_gram = price
        
        return {
            "price_per_gram": price_per_gram,
            "price_per_kg": price_per_kg,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_platinum():
    """Scrape platinum prices"""
    url = "https://www.goodreturns.in/platinum-price.html"
    
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_per_gram = None
        price_per_10g = None
        
        price_elems = soup.find_all("div", class_="platinum-price")
        for elem in price_elems:
            text = elem.get_text(strip=True)
            match = re.search(r'₹([\d,]+\.?\d*)', text)
            if match:
                price = float(match.group(1).replace(',', ''))
                if price > 50000:
                    price_per_10g = price
                else:
                    price_per_gram = price
        
        return {
            "price_per_gram": price_per_gram,
            "price_per_10g": price_per_10g,
            "currency": "INR"
        }
    except Exception as e:
        return {"error": str(e)}

# ---------------- API ROUTES ----------------
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/all", methods=["GET"])
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
    
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=2),
        mimetype='application/json'
    )

@app.route("/api/petrol", methods=["GET"])
def api_petrol():
    city = request.args.get("city", "murshidabad")
    result = scrape_petrol(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/diesel", methods=["GET"])
def api_diesel():
    city = request.args.get("city", "murshidabad")
    result = scrape_diesel(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/lpg", methods=["GET"])
def api_lpg():
    city = request.args.get("city", "murshidabad")
    result = scrape_lpg(city)
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/gold", methods=["GET"])
def api_gold():
    result = scrape_gold()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/silver", methods=["GET"])
def api_silver():
    result = scrape_silver()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.route("/api/platinum", methods=["GET"])
def api_platinum():
    result = scrape_platinum()
    result["copyright"] = COPYRIGHT_STRING
    return jsonify(result)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "copyright": COPYRIGHT_STRING}), 404

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

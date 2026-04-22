# ------------------------------------------------------------
# All-in-One Fuel & Metal Price API - Nexxon Hackers Edition
# GOLD FULLY WORKING + Documentation with Java/Python/C++ Examples
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
    "hyderabad": "hyderabad", "pune": "pune", "ahmedabad": "ahmedabad",
    "jaipur": "jaipur", "lucknow": "lucknow", "patna": "patna"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# ---------------- HTML TEMPLATE (Beautiful Documentation) ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fuel & Metal Price API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-cpp.min.js"></script>
<style>
.gradient-bg { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); }
.gradient-gold { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
.gradient-silver { background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%); }
.gradient-platinum { background: linear-gradient(135deg, #E5E4E2 0%, #B9B8B6 100%); }
.endpoint-card { transition: all 0.3s ease; }
.endpoint-card:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.tab-btn.active { background: #f59e0b; color: white; }
.code-block { max-height: 300px; overflow-y: auto; }
</style>
</head>
<body class="bg-gradient-to-br from-amber-50 via-white to-orange-50 min-h-screen">
<main class="pt-8 pb-12 px-4 max-w-7xl mx-auto">
    
    <!-- Header -->
    <header class="text-center py-8">
        <div class="inline-flex items-center justify-center w-24 h-24 gradient-bg rounded-3xl mb-6 shadow-xl">
            <i class="ri-gas-station-line text-white ri-4x"></i>
        </div>
        <h1 class="text-5xl font-bold text-gray-900 mb-2">Fuel & Metal Price API</h1>
        <p class="text-xl text-gray-600 mb-2">All-in-One Real-time Price Tracker for India</p>
        <p class="text-md text-gray-500">⛽ Petrol • Diesel • LPG | 💰 Gold • Silver • Platinum</p>
        <div class="mt-4 inline-flex gap-2">
            <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">100% Free</span>
            <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">No API Key</span>
            <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">Real-time Data</span>
        </div>
    </header>

    <!-- Quick Stats -->
    <section class="mb-12 grid grid-cols-2 md:grid-cols-6 gap-3">
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">⛽</span><p class="text-xs font-medium">Petrol</p></div>
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">🚛</span><p class="text-xs font-medium">Diesel</p></div>
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">🔥</span><p class="text-xs font-medium">LPG</p></div>
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">🥇</span><p class="text-xs font-medium">Gold</p></div>
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">🥈</span><p class="text-xs font-medium">Silver</p></div>
        <div class="bg-white rounded-xl p-3 text-center shadow-sm"><span class="text-2xl">💍</span><p class="text-xs font-medium">Platinum</p></div>
    </section>

    <!-- API Endpoints Documentation -->
    <section class="mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">📡 API Endpoints</h2>
        
        <!-- GET ALL ENDPOINT -->
        <div class="bg-white rounded-2xl p-6 shadow-lg border border-amber-200 mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <span class="w-10 h-10 gradient-bg rounded-xl flex items-center justify-center text-white text-xl">🌐</span>
                    <div>
                        <h3 class="text-xl font-bold text-gray-900">Get All Prices</h3>
                        <p class="text-sm text-gray-500">Fetch all fuel and metal prices in one request</p>
                    </div>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-3 mb-4">
                <code class="text-green-400 text-sm">/api/all?city=murshidabad</code>
            </div>
            <p class="text-sm text-gray-600 mb-3"><strong>Parameters:</strong> <code>city</code> (optional, default: murshidabad)</p>
            
            <!-- Code Examples Tabs -->
            <div class="mt-4 border-t pt-4">
                <p class="text-sm font-medium mb-2">📋 Code Examples:</p>
                <div class="flex gap-2 mb-2">
                    <button onclick="showCode('all-python')" class="tab-btn active px-3 py-1 text-xs rounded-full bg-gray-200">Python</button>
                    <button onclick="showCode('all-java')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">Java</button>
                    <button onclick="showCode('all-cpp')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">C++</button>
                </div>
                <div id="all-python" class="code-block">
                    <pre class="language-python"><code>import requests

url = "https://api.example.com/api/all?city=murshidabad"
response = requests.get(url)
data = response.json()

print(f"Petrol: ₹{data['petrol']['price_per_litre']}/L")
print(f"Diesel: ₹{data['diesel']['price_per_litre']}/L")
print(f"Gold 24K: ₹{data['gold']['prices_per_gram']['24k']}/g")</code></pre>
                </div>
                <div id="all-java" class="code-block hidden">
                    <pre class="language-java"><code>import java.net.http.*;
import java.net.URI;

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/api/all?city=murshidabad"))
    .build();

client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenAccept(response -> System.out.println(response.body()));</code></pre>
                </div>
                <div id="all-cpp" class="code-block hidden">
                    <pre class="language-cpp"><code>#include &lt;curl/curl.h&gt;
#include &lt;iostream&gt;

// Use libcurl for HTTP requests
CURL* curl = curl_easy_init();
if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "https://api.example.com/api/all?city=murshidabad");
    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
}</code></pre>
                </div>
            </div>
            
            <!-- Sample Response -->
            <details class="mt-4">
                <summary class="text-sm text-blue-600 cursor-pointer hover:underline">📄 View Sample Response</summary>
                <pre class="text-xs bg-gray-100 p-3 rounded-lg mt-2 overflow-x-auto">{
  "city": "Murshidabad",
  "petrol": {"price_per_litre": 106.53},
  "diesel": {"price_per_litre": 93.06},
  "gold": {"prices_per_gram": {"24k": 15475}}
}</pre>
            </details>
        </div>

        <!-- PETROL ENDPOINT -->
        <div class="bg-white rounded-2xl p-6 shadow-lg border border-orange-200 mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <span class="w-10 h-10 bg-orange-500 rounded-xl flex items-center justify-center text-white text-xl">⛽</span>
                    <div>
                        <h3 class="text-xl font-bold text-gray-900">Petrol Price</h3>
                        <p class="text-sm text-gray-500">Get current petrol price and 10-day history</p>
                    </div>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-3 mb-4">
                <code class="text-green-400 text-sm">/api/petrol?city=murshidabad</code>
            </div>
            <div class="flex gap-2 mb-2">
                <button onclick="showCode('petrol-python')" class="tab-btn active px-3 py-1 text-xs rounded-full bg-gray-200">Python</button>
                <button onclick="showCode('petrol-java')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">Java</button>
                <button onclick="showCode('petrol-cpp')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">C++</button>
            </div>
            <div id="petrol-python" class="code-block">
                <pre class="language-python"><code>import requests

r = requests.get("https://api.example.com/api/petrol?city=kolkata")
data = r.json()
print(f"Petrol in Kolkata: ₹{data['price_per_litre']}/L")</code></pre>
            </div>
            <div id="petrol-java" class="code-block hidden">
                <pre class="language-java"><code>// Using OkHttp
OkHttpClient client = new OkHttpClient();
Request request = new Request.Builder()
    .url("https://api.example.com/api/petrol?city=kolkata")
    .build();
Response response = client.newCall(request).execute();</code></pre>
            </div>
            <div id="petrol-cpp" class="code-block hidden">
                <pre class="language-cpp"><code>// Using cpprestsdk
http_client client(U("https://api.example.com"));
client.request(methods::GET, U("/api/petrol?city=kolkata"))
    .then([](http_response response) {
        return response.extract_json();
    });</code></pre>
            </div>
        </div>

        <!-- DIESEL ENDPOINT -->
        <div class="bg-white rounded-2xl p-6 shadow-lg border border-blue-200 mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <span class="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center text-white text-xl">🚛</span>
                    <div>
                        <h3 class="text-xl font-bold text-gray-900">Diesel Price</h3>
                        <p class="text-sm text-gray-500">Get current diesel price and 10-day history</p>
                    </div>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-3 mb-4">
                <code class="text-green-400 text-sm">/api/diesel?city=murshidabad</code>
            </div>
            <div class="flex gap-2 mb-2">
                <button onclick="showCode('diesel-python')" class="tab-btn active px-3 py-1 text-xs rounded-full bg-gray-200">Python</button>
                <button onclick="showCode('diesel-java')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">Java</button>
                <button onclick="showCode('diesel-cpp')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">C++</button>
            </div>
            <div id="diesel-python" class="code-block">
                <pre class="language-python"><code>import requests
r = requests.get("https://api.example.com/api/diesel?city=mumbai")
print(f"Diesel: ₹{r.json()['price_per_litre']}/L")</code></pre>
            </div>
            <div id="diesel-java" class="code-block hidden"><pre class="language-java"><code>// Similar to petrol example</code></pre></div>
            <div id="diesel-cpp" class="code-block hidden"><pre class="language-cpp"><code>// Similar to petrol example</code></pre></div>
        </div>

        <!-- GOLD ENDPOINT -->
        <div class="bg-white rounded-2xl p-6 shadow-lg border border-yellow-300 mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <span class="w-10 h-10 gradient-gold rounded-xl flex items-center justify-center text-white text-xl">🥇</span>
                    <div>
                        <h3 class="text-xl font-bold text-gray-900">Gold Price</h3>
                        <p class="text-sm text-gray-500">Get 24K, 22K, and 18K gold rates per gram</p>
                    </div>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-3 mb-4">
                <code class="text-green-400 text-sm">/api/gold</code>
            </div>
            <div class="flex gap-2 mb-2">
                <button onclick="showCode('gold-python')" class="tab-btn active px-3 py-1 text-xs rounded-full bg-gray-200">Python</button>
                <button onclick="showCode('gold-java')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">Java</button>
                <button onclick="showCode('gold-cpp')" class="tab-btn px-3 py-1 text-xs rounded-full bg-gray-200">C++</button>
            </div>
            <div id="gold-python" class="code-block">
                <pre class="language-python"><code>import requests
data = requests.get("https://api.example.com/api/gold").json()
print(f"24K Gold: ₹{data['prices_per_gram']['24k']}/g")
print(f"22K Gold: ₹{data['prices_per_gram']['22k']}/g")</code></pre>
            </div>
            <div id="gold-java" class="code-block hidden"><pre class="language-java"><code>// Similar pattern</code></pre></div>
            <div id="gold-cpp" class="code-block hidden"><pre class="language-cpp"><code>// Similar pattern</code></pre></div>
            <details class="mt-4">
                <summary class="text-sm text-blue-600 cursor-pointer">📄 Sample Response</summary>
                <pre class="text-xs bg-gray-100 p-3 rounded-lg mt-2">{"prices_per_gram": {"24k": 15475, "22k": 14185, "18k": 11606}}</pre>
            </details>
        </div>

        <!-- SILVER & PLATINUM (Similar cards) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-300 endpoint-card">
                <div class="flex items-center gap-3 mb-4">
                    <span class="w-10 h-10 gradient-silver rounded-xl flex items-center justify-center text-white text-xl">🥈</span>
                    <div><h3 class="text-xl font-bold">Silver Price</h3></div>
                </div>
                <code class="text-sm bg-gray-900 text-green-400 p-2 rounded block mb-2">/api/silver</code>
                <pre class="language-python text-xs"><code>requests.get("/api/silver").json()
# {"price_per_gram": 264.90, "price_per_kg": 264900}</code></pre>
            </div>
            <div class="bg-white rounded-2xl p-6 shadow-lg border border-purple-200 endpoint-card">
                <div class="flex items-center gap-3 mb-4">
                    <span class="w-10 h-10 gradient-platinum rounded-xl flex items-center justify-center text-gray-700 text-xl">💍</span>
                    <div><h3 class="text-xl font-bold">Platinum Price</h3></div>
                </div>
                <code class="text-sm bg-gray-900 text-green-400 p-2 rounded block mb-2">/api/platinum</code>
                <pre class="language-python text-xs"><code>requests.get("/api/platinum").json()
# {"price_per_gram": 6236, "price_per_10g": 62360}</code></pre>
            </div>
        </div>
    </section>

    <!-- Developer Credit -->
    <div class="text-center py-8">
        <div class="inline-block gradient-bg text-white px-10 py-5 rounded-3xl shadow-xl">
            <p class="font-bold text-2xl">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-lg opacity-95">CEO & Founder Of - Nexxon Hackers</p>
        </div>
        <p class="text-sm text-gray-500 mt-4">Data sourced from GoodReturns.in | Updated daily</p>
    </div>

</main>

<script>
function showCode(id) {
    const parent = document.getElementById(id).parentElement;
    parent.querySelectorAll('.code-block').forEach(b => b.classList.add('hidden'));
    parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active', 'bg-amber-500', 'text-white'));
    document.getElementById(id).classList.remove('hidden');
    event.target.classList.add('active', 'bg-amber-500', 'text-white');
}
</script>
</body>
</html>
'''

# ---------------- WORKING SCRAPERS ----------------
def extract_price(text):
    """Extract price from text"""
    if not text:
        return None
    text = text.replace(',', '')
    match = re.search(r'₹\s*([\d,]+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return None

def scrape_petrol(city="murshidabad"):
    url = f"https://www.goodreturns.in/petrol-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        price = None
        text = soup.get_text()
        match = re.search(r"Today's petrol price.*?₹\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if match:
            price = float(match.group(1).replace(',', ''))
        history = []
        table = soup.find("table")
        if table:
            for row in table.find_all("tr")[1:11]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    p = extract_price(cols[1].get_text(strip=True))
                    if p:
                        history.append({"date": cols[0].get_text(strip=True), "price": p})
        return {"city": city.title(), "price_per_litre": price, "currency": "INR", "last_10_days": history}
    except Exception as e:
        return {"error": str(e)}

def scrape_diesel(city="murshidabad"):
    url = f"https://www.goodreturns.in/diesel-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        price = None
        text = soup.get_text()
        match = re.search(r"Today's diesel price.*?₹\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if match:
            price = float(match.group(1).replace(',', ''))
        return {"city": city.title(), "price_per_litre": price, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_lpg(city="murshidabad"):
    url = f"https://www.goodreturns.in/lpg-price-in-{city}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        domestic, commercial = None, None
        text = soup.get_text()
        dom_match = re.search(r"Domestic.*?14\.2.*?₹\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if dom_match:
            domestic = float(dom_match.group(1).replace(',', ''))
        com_match = re.search(r"Commercial.*?19.*?₹\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if com_match:
            commercial = float(com_match.group(1).replace(',', ''))
        return {"city": city.title(), "domestic_14kg": domestic, "commercial_19kg": commercial, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_gold():
    """FULLY WORKING GOLD SCRAPER"""
    url = "https://www.goodreturns.in/gold-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        
        prices = {"24k": None, "22k": None, "18k": None}
        
        # Method 1: Extract from the top display section
        # Looking for "24K Gold /g ₹15,475" pattern
        match_24k = re.search(r"24K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        match_22k = re.search(r"22K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        match_18k = re.search(r"18K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        
        if match_24k:
            prices["24k"] = float(match_24k.group(1).replace(',', ''))
        if match_22k:
            prices["22k"] = float(match_22k.group(1).replace(',', ''))
        if match_18k:
            prices["18k"] = float(match_18k.group(1).replace(',', ''))
        
        # Method 2: Alternative pattern from the page
        if not prices["24k"]:
            alt_match = re.search(r"24\s*karat.*?₹\s*([\d,]+)", text, re.IGNORECASE)
            if alt_match:
                prices["24k"] = float(alt_match.group(1).replace(',', ''))
        
        # Method 3: Look in the table
        if not all(prices.values()):
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    row_text = row.get_text(strip=True)
                    if "24K" in row_text or "24 Carat" in row_text:
                        p = extract_price(row_text)
                        if p:
                            prices["24k"] = p
                    elif "22K" in row_text or "22 Carat" in row_text:
                        p = extract_price(row_text)
                        if p:
                            prices["22k"] = p
                    elif "18K" in row_text or "18 Carat" in row_text:
                        p = extract_price(row_text)
                        if p:
                            prices["18k"] = p
        
        return {"prices_per_gram": prices, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_silver():
    url = "https://www.goodreturns.in/silver-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        gram, kg = None, None
        match_g = re.search(r"Silver\s*/g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_g:
            gram = float(match_g.group(1).replace(',', ''))
        match_kg = re.search(r"Silver\s*/kg\s*₹\s*([\d,]+\.?\d*)", text)
        if match_kg:
            kg = float(match_kg.group(1).replace(',', ''))
        return {"price_per_gram": gram, "price_per_kg": kg, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_platinum():
    url = "https://www.goodreturns.in/platinum-price.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        gram, ten_g = None, None
        match_g = re.search(r"Platinum\s*/g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_g:
            gram = float(match_g.group(1).replace(',', ''))
        match_10 = re.search(r"Platinum\s*/10g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_10:
            ten_g = float(match_10.group(1).replace(',', ''))
        return {"price_per_gram": gram, "price_per_10g": ten_g, "currency": "INR"}
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

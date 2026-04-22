# ------------------------------------------------------------
# All-in-One Fuel & Metal Price API - Nexxon Hackers Edition
# EVERYTHING WORKING + FULLY RESPONSIVE DOCS
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

# ---------------- HTML TEMPLATE (FULLY RESPONSIVE) ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
<title>Fuel & Metal Price API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-cpp.min.js"></script>
<script>tailwind.config={theme:{extend:{colors:{primary:'#f59e0b',secondary:'#ea580c'}}}}</script>
<style>
.gradient-bg { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); }
.gradient-gold { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
.gradient-silver { background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%); }
.gradient-platinum { background: linear-gradient(135deg, #E5E4E2 0%, #B9B8B6 100%); }
.endpoint-card { transition: all 0.3s ease; }
.endpoint-card:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.code-block { max-height: 300px; overflow-y: auto; }
pre { margin: 0 !important; border-radius: 8px !important; }
.tab-btn { transition: all 0.2s; }
.tab-btn.active { background: #f59e0b !important; color: white !important; }
</style>
</head>
<body class="bg-gradient-to-br from-amber-50 via-white to-orange-50 min-h-screen">
<main class="pt-4 md:pt-8 pb-8 md:pb-12 px-3 md:px-4 max-w-7xl mx-auto">
    
    <!-- Header -->
    <header class="text-center py-4 md:py-8">
        <div class="inline-flex items-center justify-center w-16 h-16 md:w-24 md:h-24 gradient-bg rounded-2xl md:rounded-3xl mb-4 md:mb-6 shadow-xl">
            <i class="ri-gas-station-line text-white text-2xl md:text-4xl"></i>
        </div>
        <h1 class="text-3xl md:text-5xl font-bold text-gray-900 mb-2">Fuel & Metal Price API</h1>
        <p class="text-base md:text-xl text-gray-600 mb-2">All-in-One Real-time Price Tracker for India</p>
        <p class="text-xs md:text-md text-gray-500">⛽ Petrol • Diesel • LPG | 💰 Gold • Silver • Platinum</p>
        <div class="mt-3 md:mt-4 inline-flex flex-wrap justify-center gap-1 md:gap-2">
            <span class="px-2 md:px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs md:text-sm">100% Free</span>
            <span class="px-2 md:px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs md:text-sm">No API Key</span>
            <span class="px-2 md:px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs md:text-sm">Real-time Data</span>
        </div>
    </header>

    <!-- Quick Stats -->
    <section class="mb-8 md:mb-12 grid grid-cols-3 md:grid-cols-6 gap-2 md:gap-3">
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">⛽</span><p class="text-xs font-medium">Petrol</p></div>
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">🚛</span><p class="text-xs font-medium">Diesel</p></div>
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">🔥</span><p class="text-xs font-medium">LPG</p></div>
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">🥇</span><p class="text-xs font-medium">Gold</p></div>
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">🥈</span><p class="text-xs font-medium">Silver</p></div>
        <div class="bg-white rounded-xl p-2 md:p-3 text-center shadow-sm"><span class="text-xl md:text-2xl">💍</span><p class="text-xs font-medium">Platinum</p></div>
    </section>

    <!-- API Endpoints Documentation -->
    <section class="mb-8 md:mb-12">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4 md:mb-6 text-center">📡 API Endpoints</h2>
        
        <!-- GET ALL ENDPOINT -->
        <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-amber-200 mb-4 md:mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-3 md:mb-4">
                <div class="flex items-center gap-2 md:gap-3">
                    <span class="w-8 h-8 md:w-10 md:h-10 gradient-bg rounded-xl flex items-center justify-center text-white text-base md:text-xl">🌐</span>
                    <div>
                        <h3 class="text-lg md:text-xl font-bold text-gray-900">Get All Prices</h3>
                        <p class="text-xs md:text-sm text-gray-500">Fetch all fuel and metal prices in one request</p>
                    </div>
                </div>
                <span class="px-2 md:px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-2 md:p-3 mb-3 md:mb-4 overflow-x-auto">
                <code class="text-green-400 text-xs md:text-sm whitespace-nowrap">/api/all?city=murshidabad</code>
            </div>
            <p class="text-xs md:text-sm text-gray-600 mb-3"><strong>Parameters:</strong> <code>city</code> (optional, default: murshidabad)</p>
            
            <div class="mt-3 md:mt-4 border-t pt-3 md:pt-4">
                <p class="text-xs md:text-sm font-medium mb-2">📋 Code Examples:</p>
                <div class="flex gap-1 md:gap-2 mb-2 flex-wrap">
                    <button onclick="showCode(this, 'all-python')" class="tab-btn active px-2 md:px-3 py-1 text-xs rounded-full bg-gray-200">Python</button>
                    <button onclick="showCode(this, 'all-java')" class="tab-btn px-2 md:px-3 py-1 text-xs rounded-full bg-gray-200">Java</button>
                    <button onclick="showCode(this, 'all-cpp')" class="tab-btn px-2 md:px-3 py-1 text-xs rounded-full bg-gray-200">C++</button>
                    <button onclick="showCode(this, 'all-curl')" class="tab-btn px-2 md:px-3 py-1 text-xs rounded-full bg-gray-200">cURL</button>
                </div>
                <div id="all-python" class="code-block">
                    <pre class="language-python"><code>import requests

url = "https://api.example.com/api/all?city=murshidabad"
response = requests.get(url)
data = response.json()

print(f"Petrol: ₹{data['petrol']['price_per_litre']}/L")
print(f"Diesel: ₹{data['diesel']['price_per_litre']}/L")
print(f"Gold 24K: ₹{data['gold']['prices_per_gram']['24k']}/g")
print(f"Silver: ₹{data['silver']['price_per_gram']}/g")
print(f"Platinum: ₹{data['platinum']['price_per_gram']}/g")</code></pre>
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

CURL* curl = curl_easy_init();
if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "https://api.example.com/api/all?city=murshidabad");
    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
}</code></pre>
                </div>
                <div id="all-curl" class="code-block hidden">
                    <pre class="language-bash"><code>curl "https://api.example.com/api/all?city=murshidabad"</code></pre>
                </div>
            </div>
        </div>

        <!-- PETROL & DIESEL (2 columns on desktop) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-4 md:mb-6">
            <!-- PETROL -->
            <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-orange-200 endpoint-card">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-8 h-8 bg-orange-500 rounded-xl flex items-center justify-center text-white text-base">⛽</span>
                        <h3 class="text-lg font-bold">Petrol Price</h3>
                    </div>
                    <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                    <code class="text-green-400 text-xs whitespace-nowrap">/api/petrol?city=murshidabad</code>
                </div>
                <div class="flex gap-1 mb-2 flex-wrap">
                    <button onclick="showCode(this, 'petrol-python')" class="tab-btn active px-2 py-1 text-xs rounded-full bg-gray-200">Python</button>
                    <button onclick="showCode(this, 'petrol-curl')" class="tab-btn px-2 py-1 text-xs rounded-full bg-gray-200">cURL</button>
                </div>
                <div id="petrol-python" class="code-block">
                    <pre class="language-python"><code>import requests
r = requests.get("https://api.example.com/api/petrol?city=kolkata")
print(f"Petrol: ₹{r.json()['price_per_litre']}/L")</code></pre>
                </div>
                <div id="petrol-curl" class="code-block hidden">
                    <pre class="language-bash"><code>curl "https://api.example.com/api/petrol?city=kolkata"</code></pre>
                </div>
            </div>

            <!-- DIESEL -->
            <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-blue-200 endpoint-card">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <span class="w-8 h-8 bg-blue-500 rounded-xl flex items-center justify-center text-white text-base">🚛</span>
                        <h3 class="text-lg font-bold">Diesel Price</h3>
                    </div>
                    <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                    <code class="text-green-400 text-xs whitespace-nowrap">/api/diesel?city=murshidabad</code>
                </div>
                <div class="flex gap-1 mb-2 flex-wrap">
                    <button onclick="showCode(this, 'diesel-python')" class="tab-btn active px-2 py-1 text-xs rounded-full bg-gray-200">Python</button>
                    <button onclick="showCode(this, 'diesel-curl')" class="tab-btn px-2 py-1 text-xs rounded-full bg-gray-200">cURL</button>
                </div>
                <div id="diesel-python" class="code-block">
                    <pre class="language-python"><code>import requests
r = requests.get("https://api.example.com/api/diesel?city=mumbai")
print(f"Diesel: ₹{r.json()['price_per_litre']}/L")</code></pre>
                </div>
                <div id="diesel-curl" class="code-block hidden">
                    <pre class="language-bash"><code>curl "https://api.example.com/api/diesel?city=mumbai"</code></pre>
                </div>
            </div>
        </div>

        <!-- LPG -->
        <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-red-200 mb-4 md:mb-6 endpoint-card">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                    <span class="w-8 h-8 bg-red-500 rounded-xl flex items-center justify-center text-white text-base">🔥</span>
                    <h3 class="text-lg font-bold">LPG Price</h3>
                </div>
                <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">GET</span>
            </div>
            <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                <code class="text-green-400 text-xs whitespace-nowrap">/api/lpg?city=murshidabad</code>
            </div>
            <div class="flex gap-1 mb-2 flex-wrap">
                <button onclick="showCode(this, 'lpg-python')" class="tab-btn active px-2 py-1 text-xs rounded-full bg-gray-200">Python</button>
                <button onclick="showCode(this, 'lpg-curl')" class="tab-btn px-2 py-1 text-xs rounded-full bg-gray-200">cURL</button>
            </div>
            <div id="lpg-python" class="code-block">
                <pre class="language-python"><code>import requests
r = requests.get("https://api.example.com/api/lpg?city=delhi")
data = r.json()
print(f"Domestic: ₹{data['domestic_14kg']}, Commercial: ₹{data['commercial_19kg']}")</code></pre>
            </div>
            <div id="lpg-curl" class="code-block hidden">
                <pre class="language-bash"><code>curl "https://api.example.com/api/lpg?city=delhi"</code></pre>
            </div>
        </div>

        <!-- GOLD, SILVER, PLATINUM (3 columns) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            <!-- GOLD -->
            <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-yellow-300 endpoint-card">
                <div class="flex items-center gap-2 mb-3">
                    <span class="w-8 h-8 gradient-gold rounded-xl flex items-center justify-center text-white text-base">🥇</span>
                    <h3 class="text-lg font-bold">Gold Price</h3>
                </div>
                <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                    <code class="text-green-400 text-xs">/api/gold</code>
                </div>
                <pre class="language-python text-xs"><code>requests.get("/api/gold").json()
# {"24k": 15475, "22k": 14185}</code></pre>
            </div>

            <!-- SILVER -->
            <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-gray-300 endpoint-card">
                <div class="flex items-center gap-2 mb-3">
                    <span class="w-8 h-8 gradient-silver rounded-xl flex items-center justify-center text-white text-base">🥈</span>
                    <h3 class="text-lg font-bold">Silver Price</h3>
                </div>
                <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                    <code class="text-green-400 text-xs">/api/silver</code>
                </div>
                <pre class="language-python text-xs"><code>requests.get("/api/silver").json()
# {"price_per_gram": 264.90}</code></pre>
            </div>

            <!-- PLATINUM -->
            <div class="bg-white rounded-2xl p-4 md:p-6 shadow-lg border border-purple-200 endpoint-card">
                <div class="flex items-center gap-2 mb-3">
                    <span class="w-8 h-8 gradient-platinum rounded-xl flex items-center justify-center text-gray-700 text-base">💍</span>
                    <h3 class="text-lg font-bold">Platinum Price</h3>
                </div>
                <div class="bg-gray-900 rounded-lg p-2 mb-3 overflow-x-auto">
                    <code class="text-green-400 text-xs">/api/platinum</code>
                </div>
                <pre class="language-python text-xs"><code>requests.get("/api/platinum").json()
# {"price_per_gram": 6236}</code></pre>
            </div>
        </div>
    </section>

    <!-- Developer Credit -->
    <div class="text-center py-6 md:py-8">
        <div class="inline-block gradient-bg text-white px-6 md:px-10 py-3 md:py-5 rounded-2xl md:rounded-3xl shadow-xl">
            <p class="font-bold text-lg md:text-2xl">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-sm md:text-lg opacity-95">CEO & Founder Of - Nexxon Hackers</p>
        </div>
        <p class="text-xs md:text-sm text-gray-500 mt-3 md:mt-4">Data sourced from GoodReturns.in | Updated daily</p>
    </div>

</main>

<script>
function showCode(btn, id) {
    const parent = btn.parentElement.parentElement;
    parent.querySelectorAll('.code-block').forEach(b => b.classList.add('hidden'));
    parent.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active', 'bg-amber-500', 'text-white');
        b.classList.add('bg-gray-200');
    });
    document.getElementById(id).classList.remove('hidden');
    btn.classList.add('active', 'bg-amber-500', 'text-white');
    btn.classList.remove('bg-gray-200');
}
// Initialize first tabs
document.querySelectorAll('.tab-btn.active').forEach(btn => {
    btn.classList.add('bg-amber-500', 'text-white');
    btn.classList.remove('bg-gray-200');
});
</script>
</body>
</html>
'''

# ---------------- WORKING SCRAPERS ----------------
def extract_price(text):
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
    url = "https://www.goodreturns.in/gold-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        prices = {"24k": None, "22k": None, "18k": None}
        
        match_24k = re.search(r"24K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        match_22k = re.search(r"22K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        match_18k = re.search(r"18K\s*Gold\s*/g\s*₹\s*([\d,]+)", text)
        
        if match_24k: prices["24k"] = float(match_24k.group(1).replace(',', ''))
        if match_22k: prices["22k"] = float(match_22k.group(1).replace(',', ''))
        if match_18k: prices["18k"] = float(match_18k.group(1).replace(',', ''))
        
        return {"prices_per_gram": prices, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_silver():
    """FIXED SILVER - Working!"""
    url = "https://www.goodreturns.in/silver-rates/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        gram, kg = None, None
        
        # Pattern 1: "Silver /g ₹264.90"
        match_g = re.search(r"Silver\s*/g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_g:
            gram = float(match_g.group(1).replace(',', ''))
        
        # Pattern 2: "Silver /kg ₹2,64,900"
        match_kg = re.search(r"Silver\s*/kg\s*₹\s*([\d,]+\.?\d*)", text)
        if match_kg:
            kg = float(match_kg.group(1).replace(',', ''))
        
        # Pattern 3: Look for ₹264.90 pattern near "Silver"
        if not gram:
            match = re.search(r"₹\s*([\d,]+\.\d{2})\s*.*?Silver", text, re.DOTALL)
            if match:
                gram = float(match.group(1).replace(',', ''))
        
        # Pattern 4: From the table
        if not gram:
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    row_text = row.get_text()
                    if "gram" in row_text.lower():
                        p = extract_price(row_text)
                        if p and p < 10000:
                            gram = p
                    elif "kg" in row_text.lower():
                        p = extract_price(row_text)
                        if p and p > 10000:
                            kg = p
        
        return {"price_per_gram": gram, "price_per_kg": kg, "currency": "INR"}
    except Exception as e:
        return {"error": str(e)}

def scrape_platinum():
    """FIXED PLATINUM - Working!"""
    url = "https://www.goodreturns.in/platinum-price.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        gram, ten_g = None, None
        
        # Pattern 1: "Platinum /g ₹6,236"
        match_g = re.search(r"Platinum\s*/g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_g:
            gram = float(match_g.group(1).replace(',', ''))
        
        # Pattern 2: "Platinum /10g ₹62,360"
        match_10 = re.search(r"Platinum\s*/10g\s*₹\s*([\d,]+\.?\d*)", text)
        if match_10:
            ten_g = float(match_10.group(1).replace(',', ''))
        
        # Pattern 3: Look for ₹6,236 pattern near "Platinum"
        if not gram:
            match = re.search(r"₹\s*([\d,]+\.?\d*)\s*.*?Platinum", text, re.DOTALL)
            if match:
                val = float(match.group(1).replace(',', ''))
                if val < 50000:
                    gram = val
        
        # Pattern 4: From the table
        if not gram:
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    row_text = row.get_text()
                    if "gram" in row_text.lower() and "10" not in row_text:
                        p = extract_price(row_text)
                        if p and p < 50000:
                            gram = p
                    elif "10 gram" in row_text.lower():
                        p = extract_price(row_text)
                        if p:
                            ten_g = p
        
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

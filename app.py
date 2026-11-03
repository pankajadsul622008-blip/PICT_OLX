"""
PICT Campus Marketplace (OLX for PICT)
--------------------------------------
A single-file, self-contained study material marketplace for PICT students.
Powered by Sarvam AI Vision (gemma4) and indicative Indic LLM capabilities.

Usage:
  python app.py              # Starts the web application at http://localhost:8000/
  python app.py --test       # Verifies connection to Sarvam AI API
  python app.py --cli <img_path>  # Scans an image and outputs structured JSON
"""

import os
import sys
import json
import sqlite3
import base64
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from sarvamai import SarvamAI

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 1. Environment & Configuration
# ---------------------------------------------------------------------------
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

DB_PATH = Path(__file__).parent / "listings.db"

def get_sarvam_client() -> SarvamAI:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not set. Please add it to your .env file or environment.")
    return SarvamAI(api_subscription_key=api_key)

# ---------------------------------------------------------------------------
# 2. Database Initialization
# ---------------------------------------------------------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT,
                department TEXT,
                target_year TEXT,
                semester TEXT,
                material_type TEXT,
                condition TEXT,
                price_inr INTEGER,
                original_mrp INTEGER,
                description TEXT,
                seller_name TEXT,
                seller_contact TEXT,
                image_data_uri TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# ---------------------------------------------------------------------------
# 3. Sarvam AI Vision & Indic Extraction
# ---------------------------------------------------------------------------
def analyze_study_material_image(data_uri: str, model: str = "gemma4") -> dict:
    """
    Sends study material image to Sarvam AI Vision and extracts SPPU/PICT metadata.
    """
    client = get_sarvam_client()
    system_prompt = (
        "You are an AI assistant for a college study material marketplace at PICT "
        "(Pune Institute of Computer Technology, affiliated with SPPU - Pune University). "
        "A senior student is listing used study material (textbook, handwritten notes, "
        "PYQ question booklet, lab manual, engineering drafter/kit).\n"
        "Analyze the provided image and extract accurate details.\n"
        "Return ONLY a valid JSON object with the following keys:\n"
        "{\n"
        '  "title": "Clean, descriptive title for the listing",\n'
        '  "subject": "Subject name according to SPPU curriculum (e.g. Data Structures, OS, CN, TOC, EM-3)",\n'
        '  "department": "One of: Computer Engineering, Information Technology, E&TC, AIDS, First Year (FE), General",\n'
        '  "target_year": "One of: FE, SE, TE, BE",\n'
        '  "semester": "Semester 1 through 8",\n'
        '  "material_type": "One of: Textbook, Handwritten Notes, Question Bank / PYQ, Lab Manual, Tool / Instrument",\n'
        '  "publisher_or_author": "e.g. Nirali Prakashan, TechKnowledge, Pearson, McGraw-Hill, or Senior Handwritten",\n'
        '  "detected_condition": "One of: Like New, Good, Annotated / Highlighted, Fair / Worn",\n'
        '  "suggested_price_inr": integer resale price in INR (40-60% off typical MRP),\n'
        '  "estimated_mrp_inr": integer estimated original MRP in INR,\n'
        '  "description": "A helpful 2-sentence description for juniors highlighting utility and condition",\n'
        '  "search_tags": ["list", "of", "relevant", "keywords"]\n'
        "}\n"
        "Do not include any markdown backticks or extra text outside JSON."
    )
    
    response = client.chat.completions_v2(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
        temperature=0.2
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return json.loads(content)

# ---------------------------------------------------------------------------
# 4. Embedded Frontend (HTML/JS/Tailwind CSS)
# ---------------------------------------------------------------------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PICT Campus Marketplace | Study Material OLX</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen">
  <!-- Header -->
  <header class="bg-gradient-to-r from-blue-900 to-indigo-900 text-white shadow-md sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center font-bold text-blue-950 text-xl shadow">
          P
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight">PICT Campus Marketplace</h1>
          <p class="text-xs text-blue-200">Seniors &rarr; Juniors P2P Study Material Hub (Powered by Sarvam AI)</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <button onclick="switchTab('browse')" id="tab-browse-btn" class="px-4 py-2 rounded-lg text-sm font-semibold transition bg-white/20 text-white hover:bg-white/30">
          <i class="fa-solid fa-book-open mr-1.5"></i> Browse Listings
        </button>
        <button onclick="switchTab('list')" id="tab-list-btn" class="px-4 py-2 rounded-lg text-sm font-semibold transition bg-amber-500 text-blue-950 hover:bg-amber-400 shadow">
          <i class="fa-solid fa-camera mr-1.5"></i> List Used Material
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto px-4 py-8">
    <!-- LISTING VIEW (SENIOR) -->
    <section id="view-list" class="space-y-6">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8">
        <div class="max-w-2xl">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 mb-3">
            <i class="fa-solid fa-wand-magic-sparkles"></i> AI Instant Scan
          </span>
          <h2 class="text-2xl font-bold text-slate-900">List Your Study Material with 1 Photo</h2>
          <p class="text-slate-500 text-sm mt-1">
            Upload or snap a photo of your textbook, notes, or drafter. Sarvam AI Vision will auto-detect the SPPU subject, branch, and suggested campus resale price.
          </p>
        </div>

        <div class="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          <!-- Upload Area -->
          <div class="lg:col-span-5 space-y-4">
            <div id="dropzone" 
                 class="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50/50 transition flex flex-col items-center justify-center min-h-[280px]">
              <input type="file" id="file-input" accept="image/*" class="hidden">
              <div id="upload-placeholder" class="space-y-3">
                <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto text-2xl">
                  <i class="fa-solid fa-cloud-arrow-up"></i>
                </div>
                <div>
                  <p class="font-semibold text-slate-700">Click to upload or drag & drop</p>
                  <p class="text-xs text-slate-400 mt-1">Book covers, handwritten notes pages, PYQs (JPG, PNG)</p>
                </div>
              </div>
              <img id="image-preview" class="hidden max-h-64 rounded-lg object-contain shadow-sm border border-slate-200">
            </div>

            <div id="ai-loading" class="hidden p-4 bg-indigo-50 border border-indigo-200 rounded-xl flex items-center space-x-3 text-indigo-900">
              <i class="fa-solid fa-circle-notch fa-spin text-xl text-indigo-600"></i>
              <div>
                <p class="text-sm font-semibold">Sarvam AI Vision Scanning...</p>
                <p class="text-xs text-indigo-700">Extracting subject, branch, condition, and price...</p>
              </div>
            </div>

            <button id="re-analyze-btn" class="hidden w-full py-2 px-4 rounded-lg border border-slate-300 text-slate-700 text-sm font-medium hover:bg-slate-100 transition">
              <i class="fa-solid fa-rotate-right mr-1.5"></i> Re-scan Photo
            </button>
          </div>

          <!-- Form Details -->
          <div class="lg:col-span-7">
            <form id="listing-form" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Listing Title</label>
                <input type="text" id="title" required placeholder="e.g. Data Structures & Algorithms - Nirali Prakashan" 
                       class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none transition">
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Subject (SPPU)</label>
                  <input type="text" id="subject" placeholder="e.g. Data Structures (DSA)" 
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Department</label>
                  <select id="department" class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none bg-white">
                    <option value="Computer Engineering">Computer Engineering</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="E&TC">Electronics & Telecom (E&TC)</option>
                    <option value="AIDS">Artificial Intelligence & DS</option>
                    <option value="First Year (FE)">First Year (FE)</option>
                    <option value="General">General / All Branches</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Year</label>
                  <select id="target_year" class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none bg-white">
                    <option value="FE">FE (First Year)</option>
                    <option value="SE">SE (Second Year)</option>
                    <option value="TE">TE (Third Year)</option>
                    <option value="BE">BE (Final Year)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Semester</label>
                  <input type="text" id="semester" placeholder="e.g. Semester 3" 
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Type</label>
                  <select id="material_type" class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none bg-white">
                    <option value="Textbook">Textbook</option>
                    <option value="Handwritten Notes">Handwritten Notes</option>
                    <option value="Question Bank / PYQ">Question Bank / PYQ</option>
                    <option value="Lab Manual">Lab Manual</option>
                    <option value="Tool / Instrument">Drafter / Tool</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Condition</label>
                  <select id="condition" class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none bg-white">
                    <option value="Like New">Like New</option>
                    <option value="Good">Good</option>
                    <option value="Annotated / Highlighted">Annotated / Notes</option>
                    <option value="Fair / Worn">Fair / Worn</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Resale Price (₹)</label>
                  <input type="number" id="price_inr" required placeholder="200" 
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none font-bold text-emerald-700">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Original MRP (₹)</label>
                  <input type="number" id="original_mrp" placeholder="450" 
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none text-slate-500">
                </div>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Description</label>
                <textarea id="description" rows="2" placeholder="Brief info for buyers (e.g. includes solved PYQs, highlighted topics)" 
                          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none"></textarea>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Your Name / Roll No.</label>
                  <input type="text" id="seller_name" placeholder="e.g. Rohan (TE Comp)" required
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">WhatsApp / Phone</label>
                  <input type="text" id="seller_contact" placeholder="e.g. 9876543210" required
                         class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 text-sm outline-none">
                </div>
              </div>

              <div class="pt-4">
                <button type="submit" id="submit-btn" class="w-full py-3 px-6 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-semibold shadow-md hover:shadow-lg transition flex items-center justify-center space-x-2">
                  <i class="fa-solid fa-check"></i>
                  <span>Publish to PICT Marketplace</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>

    <!-- BROWSE VIEW (JUNIOR) -->
    <section id="view-browse" class="space-y-6 hidden">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h2 class="text-2xl font-bold text-slate-900">Study Materials Available at PICT</h2>
          <p class="text-slate-500 text-sm">Affordable books, notes, and lab instruments from your seniors</p>
        </div>
        <div class="flex flex-wrap gap-2 text-xs">
          <button onclick="filterDept('All')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-blue-700 text-white">All</button>
          <button onclick="filterDept('Computer Engineering')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100">Comp</button>
          <button onclick="filterDept('Information Technology')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100">IT</button>
          <button onclick="filterDept('E&TC')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100">E&TC</button>
          <button onclick="filterDept('AIDS')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100">AIDS</button>
          <button onclick="filterDept('First Year (FE)')" class="dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100">FE</button>
        </div>
      </div>

      <div class="relative">
        <i class="fa-solid fa-magnifying-glass absolute left-4 top-3.5 text-slate-400"></i>
        <input type="text" id="search-input" oninput="renderListings()" placeholder="Search by subject (DSA, OS, TOC), book title, or author..." 
               class="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-blue-500 text-sm outline-none shadow-sm">
      </div>

      <div id="listings-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>
      
      <div id="empty-state" class="hidden text-center py-16 bg-white rounded-2xl border border-slate-200">
        <div class="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto text-2xl mb-3">
          <i class="fa-solid fa-box-open"></i>
        </div>
        <h3 class="text-base font-semibold text-slate-700">No study materials listed yet</h3>
        <p class="text-sm text-slate-400 mt-1">Be the first senior to list an item!</p>
        <button onclick="switchTab('list')" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          List an Item Now
        </button>
      </div>
    </section>
  </main>

  <script>
    let currentImageUri = "";
    let allListings = [];
    let selectedDepartment = "All";

    function switchTab(tab) {
      const viewList = document.getElementById('view-list');
      const viewBrowse = document.getElementById('view-browse');
      const btnList = document.getElementById('tab-list-btn');
      const btnBrowse = document.getElementById('tab-browse-btn');

      if (tab === 'list') {
        viewList.classList.remove('hidden');
        viewBrowse.classList.add('hidden');
        btnList.className = "px-4 py-2 rounded-lg text-sm font-semibold transition bg-amber-500 text-blue-950 shadow";
        btnBrowse.className = "px-4 py-2 rounded-lg text-sm font-semibold transition bg-white/20 text-white hover:bg-white/30";
      } else {
        viewList.classList.add('hidden');
        viewBrowse.classList.remove('hidden');
        btnBrowse.className = "px-4 py-2 rounded-lg text-sm font-semibold transition bg-amber-500 text-blue-950 shadow";
        btnList.className = "px-4 py-2 rounded-lg text-sm font-semibold transition bg-white/20 text-white hover:bg-white/30";
        fetchListings();
      }
    }

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const aiLoading = document.getElementById('ai-loading');
    const reAnalyzeBtn = document.getElementById('re-analyze-btn');

    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('border-blue-500', 'bg-blue-50/50');
    });
    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('border-blue-500', 'bg-blue-50/50');
    });
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-blue-500', 'bg-blue-50/50');
      if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleFile(e.target.files[0]);
      }
    });

    reAnalyzeBtn.addEventListener('click', () => {
      if (currentImageUri) analyzeImage(currentImageUri);
    });

    function handleFile(file) {
      if (!file.type.startsWith('image/')) {
        alert("Please upload an image file (JPG, PNG).");
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        currentImageUri = e.target.result;
        imagePreview.src = currentImageUri;
        imagePreview.classList.remove('hidden');
        uploadPlaceholder.classList.add('hidden');
        reAnalyzeBtn.classList.remove('hidden');
        analyzeImage(currentImageUri);
      };
      reader.readAsDataURL(file);
    }

    async function analyzeImage(dataUri) {
      aiLoading.classList.remove('hidden');
      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_data_uri: dataUri })
        });
        const data = await res.json();
        if (data.success && data.analysis) {
          const a = data.analysis;
          document.getElementById('title').value = a.title || '';
          document.getElementById('subject').value = a.subject || '';
          if (a.department) document.getElementById('department').value = a.department;
          if (a.target_year) document.getElementById('target_year').value = a.target_year;
          document.getElementById('semester').value = a.semester || '';
          if (a.material_type) document.getElementById('material_type').value = a.material_type;
          if (a.detected_condition) document.getElementById('condition').value = a.detected_condition;
          document.getElementById('price_inr').value = a.suggested_price_inr || '';
          document.getElementById('original_mrp').value = a.estimated_mrp_inr || '';
          document.getElementById('description').value = a.description || '';
        } else {
          alert("Sarvam AI could not parse the image: " + (data.error || "Unknown error"));
        }
      } catch (err) {
        console.error(err);
        alert("Error connecting to Sarvam AI server.");
      } finally {
        aiLoading.classList.add('hidden');
      }
    }

    document.getElementById('listing-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        title: document.getElementById('title').value,
        subject: document.getElementById('subject').value,
        department: document.getElementById('department').value,
        target_year: document.getElementById('target_year').value,
        semester: document.getElementById('semester').value,
        material_type: document.getElementById('material_type').value,
        condition: document.getElementById('condition').value,
        price_inr: document.getElementById('price_inr').value,
        original_mrp: document.getElementById('original_mrp').value,
        description: document.getElementById('description').value,
        seller_name: document.getElementById('seller_name').value,
        seller_contact: document.getElementById('seller_contact').value,
        image_data_uri: currentImageUri
      };

      try {
        const res = await fetch('/api/listings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          alert("Listing published to PICT Marketplace!");
          document.getElementById('listing-form').reset();
          imagePreview.classList.add('hidden');
          uploadPlaceholder.classList.remove('hidden');
          reAnalyzeBtn.classList.add('hidden');
          currentImageUri = "";
          switchTab('browse');
        } else {
          alert("Error saving listing: " + (data.error || "Unknown"));
        }
      } catch (err) {
        alert("Failed to save listing: " + err.message);
      }
    });

    async function fetchListings() {
      try {
        const res = await fetch('/api/listings');
        const data = await res.json();
        allListings = data.listings || [];
        renderListings();
      } catch (err) {
        console.error("Error loading listings", err);
      }
    }

    function filterDept(dept) {
      selectedDepartment = dept;
      document.querySelectorAll('.dept-btn').forEach(btn => {
        if (btn.innerText.includes(dept) || (dept === 'All' && btn.innerText === 'All')) {
          btn.className = "dept-btn px-3 py-1.5 rounded-full font-medium bg-blue-700 text-white";
        } else {
          btn.className = "dept-btn px-3 py-1.5 rounded-full font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-100";
        }
      });
      renderListings();
    }

    function renderListings() {
      const grid = document.getElementById('listings-grid');
      const empty = document.getElementById('empty-state');
      const query = (document.getElementById('search-input').value || "").toLowerCase();

      const filtered = allListings.filter(item => {
        const matchesDept = (selectedDepartment === "All" || item.department === selectedDepartment);
        const matchesQuery = !query || 
          (item.title && item.title.toLowerCase().includes(query)) ||
          (item.subject && item.subject.toLowerCase().includes(query)) ||
          (item.description && item.description.toLowerCase().includes(query));
        return matchesDept && matchesQuery;
      });

      if (filtered.length === 0) {
        grid.innerHTML = "";
        empty.classList.remove('hidden');
        return;
      }

      empty.classList.add('hidden');
      grid.innerHTML = filtered.map(item => `
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition flex flex-col">
          <div class="h-48 bg-slate-100 flex items-center justify-center overflow-hidden border-b border-slate-100">
            ${item.image_data_uri ? `<img src="${item.image_data_uri}" class="h-full w-full object-cover">` : `<i class="fa-solid fa-book text-slate-300 text-4xl"></i>`}
          </div>
          <div class="p-5 flex-1 flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between gap-2 mb-2">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                  ${item.department || 'General'}
                </span>
                <span class="text-xs font-medium text-slate-400">
                  ${item.target_year || 'FE'} ${item.semester ? '• ' + item.semester : ''}
                </span>
              </div>
              <h3 class="font-bold text-slate-900 text-base leading-tight">${item.title}</h3>
              <p class="text-xs text-slate-500 mt-1 line-clamp-2">${item.description || 'No description provided.'}</p>
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
              <div>
                <span class="text-lg font-black text-emerald-600">₹${item.price_inr}</span>
                ${item.original_mrp ? `<span class="text-xs text-slate-400 line-through ml-1.5">₹${item.original_mrp}</span>` : ''}
              </div>
              <a href="https://wa.me/91${(item.seller_contact||'').replace(/[^0-9]/g, '')}?text=Hi!%20I%20am%20interested%20in%20buying%20your%20${encodeURIComponent(item.title)}%20listed%20on%20PICT%20Marketplace." 
                 target="_blank" 
                 class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm transition">
                <i class="fa-brands fa-whatsapp"></i> Buy
              </a>
            </div>
          </div>
        </div>
      `).join('');
    }

    fetchListings();
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 5. HTTP Request Handler
# ---------------------------------------------------------------------------
class MarketplaceHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            content = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/listings":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM listings ORDER BY id DESC")
                rows = [dict(r) for r in cursor.fetchall()]
            self._send_json({"listings": rows})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        if self.path == "/api/analyze":
            data_uri = payload.get("image_data_uri")
            if not data_uri:
                self._send_json({"error": "image_data_uri is required"}, status=400)
                return
            try:
                analysis = analyze_study_material_image(data_uri)
                self._send_json({"success": True, "analysis": analysis})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        elif self.path == "/api/listings":
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO listings (
                            title, subject, department, target_year, semester,
                            material_type, condition, price_inr, original_mrp,
                            description, seller_name, seller_contact, image_data_uri
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        payload.get("title", "Untitled Listing"),
                        payload.get("subject", ""),
                        payload.get("department", "General"),
                        payload.get("target_year", "FE"),
                        payload.get("semester", ""),
                        payload.get("material_type", "Textbook"),
                        payload.get("condition", "Good"),
                        int(payload.get("price_inr") or 0),
                        int(payload.get("original_mrp") or 0),
                        payload.get("description", ""),
                        payload.get("seller_name", "PICT Senior"),
                        payload.get("seller_contact", ""),
                        payload.get("image_data_uri", "")
                    ))
                    conn.commit()
                    new_id = cursor.lastrowid
                self._send_json({"success": True, "id": new_id})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Not Found")

# ---------------------------------------------------------------------------
# 6. Main Entry Point
# ---------------------------------------------------------------------------
def run_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, MarketplaceHandler)
    print(f"PICT Marketplace running at: http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down server...")
        httpd.server_close()

def run_test():
    client = get_sarvam_client()
    print("Testing connection with sarvam-105b-conversations...")
    res = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("Response:", res.choices[0].message.content)

def run_cli_scan(image_path: str):
    path = Path(image_path)
    if not path.exists():
        print(f"File not found: {image_path}")
        return
    mime, _ = mimetypes.guess_type(image_path)
    mime = mime or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:{mime};base64,{b64}"
    print(f"Analyzing {image_path} with Sarvam AI Vision...")
    result = analyze_study_material_image(data_uri)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    elif len(sys.argv) > 2 and sys.argv[1] == "--cli":
        run_cli_scan(sys.argv[2])
    else:
        port = 8000
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
        run_server(port)

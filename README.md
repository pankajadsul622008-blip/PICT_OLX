<div align="center">

  <img src="static/logo.png" alt="PICT Campus Marketplace" width="100" height="100" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(37,99,235,0.25);" />

  # 🎓 PICT Campus Marketplace (PICT_OLX)
  ### The AI-Powered Study Material Hub for Pune Institute of Computer Technology

  [![Live App](https://img.shields.io/badge/Live_App-Render-2563EB?style=for-the-badge&logo=render&logoColor=white)](https://pict-olx-8tvs.onrender.com)
  [![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/pankajadsul622008-blip/PICT_OLX)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
  [![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
  [![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_CDN-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com)
  [![Sarvam AI](https://img.shields.io/badge/Sarvam_AI-Multimodal_Vision-FF6F00?style=for-the-badge)](https://sarvam.ai)

  <p align="center">
    <strong>A peer-to-peer study material exchange platform built exclusively for PICT students & faculty.</strong><br>
    Seniors list used textbooks, handwritten toppers' notes, and lab instruments in <strong>1 click with 1 photo</strong> using <strong>Sarvam AI Vision</strong>, and juniors buy directly via <strong>WhatsApp</strong>.
  </p>

  [Explore Live App](https://pict-olx-8tvs.onrender.com) &bull;
  [Documentation](documentation.md) &bull;
  [Report Bug](https://github.com/pankajadsul622008-blip/PICT_OLX/issues)

</div>

---

## 📸 Visual Showcase

### 1. Modern Glassmorphic Marketplace & SPPU Curriculum Hub
The home page features a clean sapphire/slate aesthetic, real-time search, department chips (`Comp`, `IT`, `E&TC`, `AI&DS`, `FE`), dynamic discount calculations (`60% OFF`), and 1-click WhatsApp checkout.

<div align="center">
  <img src="docs/screenshots/01_hero_marketplace.png" alt="PICT Marketplace Home" width="100%" style="border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(0,0,0,0.08);" />
</div>

<br>

### 2. 1-Photo AI Listing Flow (Powered by Sarvam AI Vision)
Sellers simply snap or drag a photo of their book cover. **Sarvam AI Vision (`gemma4`)** scans the cover, extracts the SPPU subject, branch, semester, condition, and auto-fills a fair campus resale price without manual typing.

<div align="center">
  <img src="docs/screenshots/02_sell_ai_vision.png" alt="Sell Study Material with AI" width="100%" style="border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(0,0,0,0.08);" />
</div>

<br>

### 3. Dedicated Campus Admin Moderation Portal & Mobile View
<div align="center">
  <table>
    <tr>
      <td width="60%" align="center">
        <strong>🛡️ Campus Admin Portal (`admin@pict.edu`)</strong><br>
        <img src="docs/screenshots/03_admin_portal.png" alt="Admin Portal Modal" width="100%" style="border-radius: 12px; border: 1px solid #e2e8f0;" /><br>
        <em>Full content moderation privileges: Edit, Delete, Toggle Sold Status</em>
      </td>
      <td width="40%" align="center">
        <strong>📱 100% Mobile Responsive</strong><br>
        <img src="docs/screenshots/04_mobile_view.png" alt="Mobile Responsive Interface" width="90%" style="border-radius: 12px; border: 1px solid #e2e8f0;" /><br>
        <em>Optimized for smartphones and campus browsing</em>
      </td>
    </tr>
  </table>
</div>

---

## 🎯 The Real Campus Problem & Our Solution

| The Traditional Struggle | The PICT Marketplace Solution |
|---|---|
| **Expensive Books**: Juniors spend ₹2,000–₹4,000 every semester buying brand-new books from Appa Balwant Chowk (ABC). | **Affordable Pre-Owned Deals**: Juniors get verified semester notes and books from seniors at 50%–70% discounts. |
| **Tedious Listing**: Seniors take 10 minutes typing title, author, edition, semester, branch, and price on generic apps. | **1-Photo AI Auto-Fill**: **Sarvam AI Vision** extracts all metadata and sets a suggested price in under 2 seconds. |
| **Generic Spam**: Platforms like OLX are filled with non-college spam and lack SPPU syllabus context. | **100% PICT Localized**: Categorized strictly by SPPU branches (`Computer`, `IT`, `EnTC`, `AI&DS`, `FE`). |
| **Escrow & Commission**: Payment gateways charge 2–3% + GST and delay bank payouts. | **Direct WhatsApp Meetup**: Zero platform fees; buyers and sellers meet directly in the PICT Canteen or Library. |

---

## ⚡ Core Technical Features

```mermaid
sequenceDiagram
    autonumber
    actor Senior as Senior (Seller)
    actor Junior as Junior (Buyer)
    participant Web as Web App (Tailwind CSS)
    participant Server as Python HTTP Server
    participant Sarvam as Sarvam AI (gemma4)
    participant Cloud as Cloudinary CDN
    participant DB as Supabase PostgreSQL
    participant WA as WhatsApp Web / App

    Senior->>Web: Uploads 1 book cover photo
    Web->>Server: POST /api/analyze (Base64)
    Server->>Sarvam: Vision Analysis
    Sarvam-->>Server: Title, Subject, Branch, Semester, Fair Price
    Server-->>Web: Auto-fill Form
    Senior->>Web: Clicks "Publish"
    Web->>Server: POST /api/listings
    Server->>Cloud: Stream Image
    Cloud-->>Server: Optimized HTTPS URL
    Server->>DB: INSERT into listings table
    Server-->>Web: Listing Live!
    
    Junior->>Web: Filters by Department & Subject
    Web->>DB: Fetch Active Listings
    Junior->>Web: Clicks "Buy on WhatsApp"
    Web->>WA: Opens wa.me/?text=... (Pre-filled Markdown)
    WA-->>Senior: "Hi Senior! Is this available to collect on campus?"
    Note over Senior,Junior: Meet at PICT Canteen & Pay via UPI!
```

---

## 🛠️ Technology Stack Deep Dive

### 1. 🇮🇳 Sarvam AI (Indian Multimodal Intelligence)
* **Vision Model (`gemma4`)**: Purpose-built for Indian regional textbooks (Nirali Prakashan, TechKnowledge, Technical Publications, Decode). Accurately extracts book titles, authors, and condition from smartphone photos.
* **Conversations Model (`sarvam-105b-conversations`)**: Structures extracted text into clean JSON schema matching SPPU syllabus branches and semesters.

### 2. 🐘 Supabase (Hosted PostgreSQL Database)
* **Persistent Relational DB**: Hosted on AWS ap-southeast (Mumbai/Singapore region) for ultra-low latency.
* **Dual-Mode Fallback (`src/database.py`)**:
  * **Production**: Connects to Supabase PostgreSQL using `psycopg2`.
  * **Offline Dev**: Seamlessly falls back to a local SQLite database (`listings.db`) if offline.

### 3. ☁️ Cloudinary (High-Performance Image CDN)
* Free cloud hosts have **ephemeral filesystems** (local files are deleted on restart).
* All user-uploaded images stream directly to Cloudinary, which compresses, optimizes, and serves them over a global HTTPS CDN.

### 4. 💬 WhatsApp Direct Commerce (`wa.me`)
* **Glitch-Free Protocol**: Eliminates 4-byte surrogate emojis that cause the famous Windows WhatsApp protocol bug (which renders emojis as black diamond question marks ``).
* Uses WhatsApp native Markdown `- *Item:* <Title>` for crisp bold headers and native bullet points.

### 5. 🚀 Anti-Cold Start Keep-Alive (Render + UptimeRobot)
* Free Render instances sleep after 15 minutes of inactivity.
* Implemented a lightweight `/api/health` route pinged every 5 minutes by **UptimeRobot**, keeping the server permanently warm and responsive 24/7.

---

## 📂 Project Architecture

```text
PICT_OLX/
├── app.py                      # Application server entry point & CLI tools
├── requirements.txt            # Python dependencies (sarvamai, psycopg2, cloudinary)
├── Procfile                    # Render cloud process runner
├── render.yaml                 # Render infrastructure configuration
├── README.md                   # Extraordinary project showcase & quickstart
├── documentation.md            # Comprehensive technical system documentation
├── .env.example                # Safe environment configuration template
├── .gitignore                  # Git ignore rules (.env, *.db, __pycache__)
│
├── docs/                       # Project documentation & media
│   └── screenshots/            # High-resolution UI captures
│       ├── 01_hero_marketplace.png
│       ├── 02_sell_ai_vision.png
│       ├── 03_admin_portal.png
│       └── 04_mobile_view.png
│
├── src/                        # Modular application source code
│   ├── config.py               # Environment variables & constants
│   ├── database.py             # Dual-mode database manager (Supabase / SQLite)
│   ├── handlers/
│   │   └── http_handler.py     # HTTP router & REST API endpoints
│   ├── services/
│   │   ├── auth_service.py     # PBKDF2 authentication & admin privileges
│   │   ├── cloudinary_service.py # Cloudinary CDN image upload
│   │   └── sarvam_service.py   # Sarvam AI vision & extraction pipeline
│   └── templates/
│       └── index.html          # Responsive Tailwind CSS + SweetAlert2 frontend
│
└── static/                     # Static brand assets
    ├── favicon.png             # Browser tab icon (Graduation Cap & Book)
    ├── logo.png                # Brand logo for header & footer
    └── sample_book.jpg         # Sample test textbook image
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/pankajadsul622008-blip/PICT_OLX.git
cd PICT_OLX
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure `.env`
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

```env
# Administrator
ADMIN_EMAIL=admin@pict.edu
ADMIN_PASSWORD=admin123

# Sarvam AI (Get from https://dashboard.sarvam.ai)
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_VISION_MODEL=gemma4
SARVAM_CHAT_MODEL=sarvam-105b-conversations

# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres.your_project:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres

# Cloudinary CDN (Get from https://cloudinary.com/console)
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

### 4. Run the Server
```bash
python app.py
```
Open your browser at **[http://localhost:8000/](http://localhost:8000/)**!

### 5. CLI Verification Commands
```bash
# Test Sarvam AI API connection
python app.py --test

# Scan a book image directly from terminal
python app.py --cli static/sample_book.jpg
```

---

## 🌐 Live Deployment Guide (Render)

1. Create a new **Web Service** on [Render](https://dashboard.render.com).
2. Connect your GitHub repository `PICT_OLX`.
3. Configure build settings:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python app.py`
4. Add environment variables from `.env` into Render's settings tab.
5. Setup free keep-alive monitor on [UptimeRobot](https://uptimerobot.com) targeting `https://<your-app>.onrender.com/api/health` every 5 minutes.

---

## 👥 Contributors & Acknowledgements

* **Built by**: Pankaj Adsul & Team for the **Sarvam AI Campus Bootcamp**
* **Institution**: [Pune Institute of Computer Technology (PICT)](https://pict.edu)
* **Affiliation**: Savitribai Phule Pune University (SPPU)
* **Powered by**: [Sarvam AI](https://sarvam.ai) &bull; [Supabase](https://supabase.com) &bull; [Cloudinary](https://cloudinary.com) &bull; [Render](https://render.com)

---

<div align="center">
  <sub>Made with ❤️ for PICT Students & Faculty &bull; Released under the MIT License</sub>
</div>

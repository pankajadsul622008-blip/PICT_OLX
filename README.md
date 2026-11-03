# 🎓 PICT Campus Marketplace (OLX for PICT)

A peer-to-peer study material marketplace built exclusively for students of **PICT (Pune Institute of Computer Technology)**. Seniors can list their used and unwanted study materials (textbooks, handwritten notes, PYQ booklets, lab manuals, and engineering drafters), and juniors can browse and buy them directly with 1-click WhatsApp messaging.

Powered by **Sarvam AI Vision** for automated, zero-typing study material listing.

---

## ⚡ Key Features

1. **AI Auto-Listing with 1 Photo (Sarvam AI Vision)**
   - Seniors snap a photo of their book cover, notes page, or syllabus booklet.
   - **Sarvam AI Vision (`gemma4`)** extracts:
     - Book Title, Subject & SPPU Curriculum mapping (DSA, OS, TOC, EM-3, CN, etc.)
     - Target Department (**Computer Engineering**, **IT**, **E&TC**, **AIDS**, **FE**)
     - Target Academic Year & Semester (FE to BE / Sem 1 to 8)
     - Material Category (Textbook, Handwritten Notes, PYQ booklet, Lab Manual, Drafter/Tool)
     - Detected physical condition & suggested campus resale price (₹)
   - Zero manual typing required.

2. **Junior Marketplace & Search**
   - Live grid of available study materials.
   - Filter by department or search by subject, title, or author.
   - 1-Click WhatsApp "Buy" button connects junior directly with the senior seller.

3. **Lightweight & Self-Contained**
   - Built with Python, SQLite, and responsive Tailwind CSS.
   - No complex database setup or heavy framework required.

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/pict-campus-marketplace.git
cd pict-campus-marketplace
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your Sarvam AI API Key
Create a `.env` file in the root directory:
```env
SARVAM_API_KEY=your_actual_sarvam_api_key_here
```
> Get your API key from [Sarvam AI Dashboard](https://dashboard.sarvam.ai).

### 4. Run the Web Marketplace
```bash
python server.py
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser.

---

## 🛠️ Project Structure

```
├── server.py           # Backend server handling Sarvam Vision (/api/analyze) and listings (/api/listings)
├── auto_lister.py      # Standalone CLI utility for extracting listing data from images
├── index.html          # Frontend marketplace UI (Tailwind CSS)
├── main.py             # Basic Sarvam AI connection test script
├── requirements.txt    # Project dependencies
├── .env.example        # Template for environment variables
└── .gitignore          # Keeps secrets and local database out of git
```

---

## 🔒 Security
- `.env` and `listings.db` are strictly ignored by `.gitignore` to prevent any sensitive API keys or student data from being pushed to version control.

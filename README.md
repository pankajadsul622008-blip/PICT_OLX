# 🎓 PICT Campus Marketplace (OLX for PICT)

A single-file, self-contained peer-to-peer study material marketplace built exclusively for students of **PICT (Pune Institute of Computer Technology)**. Seniors can list their used textbooks, handwritten notes, PYQ booklets, lab manuals, and engineering drafters, and juniors can browse and buy them directly with 1-click WhatsApp messaging.

Powered by **Sarvam AI Vision (`gemma4`)** for instant, zero-typing study material listing.

---

## ⚡ Key Features

1. **All-in-One Architecture (`app.py`)**
   - The entire application (Sarvam AI Vision logic, embedded responsive Tailwind frontend, SQLite database, REST API, and CLI tools) is packed into a **single, portable Python file**.
2. **AI Auto-Listing with 1 Photo**
   - Seniors snap a photo of their book cover or handwritten notes.
   - **Sarvam AI Vision** extracts:
     - Book Title & Subject according to SPPU syllabus (DSA, OS, TOC, EM-3, CN, etc.)
     - Target Department (**Computer Engineering**, **IT**, **E&TC**, **AIDS**, **FE**)
     - Target Academic Year & Semester (FE to BE / Sem 1 to 8)
     - Material Category (Textbook, Notes, PYQs, Lab Manual, Drafter)
     - Physical Condition & Fair Campus Resale Price (₹)
3. **Junior Marketplace & WhatsApp Connect**
   - Live grid of available study materials.
   - Filter by department or search by subject, title, or author.
   - 1-Click WhatsApp "Buy" button connects the junior directly with the senior seller.

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

### 3. Add your Sarvam AI API Key
Create a `.env` file in the project folder:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```
> Get your key from [Sarvam AI Dashboard](https://dashboard.sarvam.ai).

### 4. Run the Web Marketplace
```bash
python app.py
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser!

### Additional CLI Commands
```bash
python app.py --test            # Test API connection with sarvam-105b-conversations
python app.py --cli sample.jpg  # Scan a book image directly from the terminal
```

---

## 🔒 Security
- `.env` and `listings.db` are strictly ignored by `.gitignore` so your API keys and local student data are never uploaded to GitHub.

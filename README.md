# 🎓 PICT Campus Marketplace (OLX for PICT)

A single-file, self-contained peer-to-peer study material marketplace built exclusively for students of **PICT (Pune Institute of Computer Technology)**. Seniors can list their used textbooks, handwritten notes, PYQ booklets, lab manuals, and engineering drafters, and juniors can browse and buy them directly with 1-click WhatsApp messaging.

Powered by **Sarvam AI Vision (`gemma4`)** for instant, zero-typing study material listing.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pankajadsul622008-blip/PICT_OLX)

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

## 🚀 Quickstart (Local)

### 1. Clone the repository
```bash
git clone https://github.com/pankajadsul622008-blip/PICT_OLX.git
cd PICT_OLX
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

## 🌐 Cloud Deployment (Live Public Link via GitHub)

Because this app runs a dynamic Python backend (`app.py` with SQLite & Sarvam AI SDK), it cannot run on static-only hosts like **GitHub Pages**. Instead, it connects directly from your GitHub repository to **Render** for free 24/7 cloud hosting.

### Method 1: 1-Click Deploy via Render Blueprint
1. Click the button below:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pankajadsul622008-blip/PICT_OLX)
2. Sign in with GitHub (`pankajadsul622008-blip`).
3. Set your `SARVAM_API_KEY` under Environment Variables.
4. Click **Create Web Service**. Render will automatically build and assign a free HTTPS URL.

### Method 2: Manual Setup on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** > **Web Service**.
2. Connect your GitHub repository: `pankajadsul622008-blip/PICT_OLX`.
3. Set the following settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
4. Under **Advanced** > **Add Environment Variable**:
   - Key: `SARVAM_API_KEY`
   - Value: `<your_sarvam_api_key>`
5. Click **Create Web Service**. Your app is live!

---

## 🔒 Security
- `.env` and `listings.db` are strictly ignored by `.gitignore` so your API keys and local student data are never uploaded to GitHub.

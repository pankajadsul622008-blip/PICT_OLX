# 🎓 PICT Campus Marketplace (PICT_OLX)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_CDN-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com)
[![Sarvam AI](https://img.shields.io/badge/Sarvam_AI-Multimodal_Vision-FF6F00?style=for-the-badge)](https://sarvam.ai)

> **A peer-to-peer study material exchange platform built exclusively for students and faculty of Pune Institute of Computer Technology (PICT).**  
> Seniors can list used textbooks, handwritten notes, drafters, and question banks in seconds using Sarvam AI Vision, and juniors can buy directly via WhatsApp.

---

## 📂 Project Directory Structure

```text
PICT_OLX/
├── app.py                      # Application entry point & CLI commands
├── requirements.txt            # Python dependencies (sarvamai, psycopg2-binary, cloudinary)
├── Procfile                    # Render web process definition
├── render.yaml                 # Render infrastructure-as-code specification
├── README.md                   # Project overview & quickstart guide
├── documentation.md            # Comprehensive technical documentation
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore rules (.env, *.db, __pycache__)
│
├── src/                        # Modular application source code
│   ├── config.py               # Settings & environment variable loader
│   ├── database.py             # Dual-mode database manager (Supabase / SQLite)
│   ├── handlers/
│   │   └── http_handler.py     # HTTP request router & REST API endpoints
│   ├── services/
│   │   ├── auth_service.py     # Admin PBKDF2 authentication & sessions
│   │   ├── cloudinary_service.py # Cloudinary CDN image upload
│   │   └── sarvam_service.py   # Sarvam AI vision & extraction pipeline
│   └── templates/
│       └── index.html          # Responsive Tailwind CSS + SweetAlert2 frontend
│
└── static/                     # Static media & assets
    ├── favicon.png             # Browser tab icon (Graduation Cap & Book)
    ├── logo.png                # Brand logo for header & footer
    └── sample_book.jpg         # Sample textbook for testing
```

---

## ⚡ Key Highlights

1. **AI Auto-Listing with 1 Photo**:
   - Upload 1 photo of any textbook, notes, or drafter.
   - **Sarvam AI Vision (`gemma4`)** auto-extracts Title, SPPU Subject, Department (`Computer`, `IT`, `EnTC`, `AI&DS`), Semester, Condition, and suggested resale price.
2. **Direct Peer-to-Peer WhatsApp Commerce**:
   - Zero transaction cut, no escrow friction.
   - 1-Click WhatsApp messaging with clean native Markdown formatting (`wa.me`) for seamless on-campus meetups.
3. **Enterprise Cloud Stack**:
   - **Database**: Cloud-hosted **Supabase PostgreSQL** with automated SQLite offline fallback.
   - **Media CDN**: **Cloudinary** auto-optimizes and compresses all book photos.
4. **Friction-Free Student UX**:
   - Students browse and list freely without passwords or signup forms.
   - **Admin Portal (`admin@pict.edu`)**: Dedicated moderator login to edit, delete, or mark listings as sold.
5. **Anti-Cold Start Keep-Alive**:
   - `/api/health` route integrated with **UptimeRobot** keeps the free Render service awake 24/7.

---

## 🚀 Quickstart

### 1. Clone & Navigate
```bash
git clone https://github.com/pankajadsul622008-blip/PICT_OLX.git
cd PICT_OLX
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and enter your credentials:
```bash
cp .env.example .env
```

### 4. Run Locally
```bash
python app.py
```
Visit **[http://localhost:8000/](http://localhost:8000/)** in your browser!

### CLI Testing Commands
```bash
python app.py --test            # Verify connection to Sarvam AI API
python app.py --cli sample.jpg  # Scan an image from terminal and output JSON
```

---

## 📖 Complete Documentation
For full architectural details, database schemas, and API documentation, see [documentation.md](documentation.md).

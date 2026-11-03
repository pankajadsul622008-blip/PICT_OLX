# 📚 PICT Campus Marketplace (PICT_OLX) — System Documentation

> **A peer-to-peer study material exchange platform built specifically for students and faculty of Pune Institute of Computer Technology (PICT).**

---

## 📑 Table of Contents
1. [Project Overview & Motivation](#1-project-overview--motivation)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Technologies & Cloud Services Used](#3-technologies--cloud-services-used)
   - [Supabase (PostgreSQL Database)](#supabase-postgresql-database)
   - [Cloudinary (Image Storage & CDN)](#cloudinary-image-storage--cdn)
   - [Sarvam AI (Indian Multimodal Vision)](#sarvam-ai-multimodal-vision)
   - [WhatsApp Direct Commerce](#whatsapp-direct-commerce)
   - [Render & UptimeRobot (Hosting & Anti-Cold Start)](#render--uptimerobot-hosting--anti-cold-start)
4. [User Flow & Student Experience](#4-user-flow--student-experience)
5. [Admin & Moderation System](#5-admin--moderation-system)
6. [Database Schema & Design](#6-database-schema--design)
7. [API Endpoints Reference](#7-api-endpoints-reference)
8. [Environment Variables Guide (.env)](#8-environment-variables-guide-env)
9. [Local Setup & Deployment Guide](#9-local-setup--deployment-guide)
10. [Key Bugs Solved & Architectural Decisions](#10-key-bugs-solved--architectural-decisions)

---

## 1. Project Overview & Motivation

### The Problem
At engineering colleges like **PICT (Pune Institute of Computer Technology)**, each semester requires textbooks (TechKnowledge, Nirali, Decode), handwritten toppers' notes, question banks, and lab drawing instruments (drafters, sheets). 
* **Seniors** have piles of books from previous semesters that they no longer need.
* **Juniors** spend thousands of rupees buying new copies from Appa Balwant Chowk (ABC).
* Existing platforms like generic OLX are filled with non-college spam, require shipping, and do not understand SPPU (Savitribai Phule Pune University) curriculum branch codes (FE, SE, TE, BE, Comp, IT, EnTC, AI&DS).

### The Solution
**PICT Campus Marketplace** provides a **zero-friction, college-localized marketplace**:
1. **Sellers (Seniors)** take 1 photo of their book/notes. **Sarvam AI Vision** reads the cover and auto-fills title, author, SPPU semester, branch, and suggested resale price.
2. **Buyers (Juniors)** filter listings by Department and Year, click **"Buy on WhatsApp"**, which opens a pre-formatted chat with the seller to arrange an on-campus exchange at PICT canteen or library.
3. **No registration barrier**: Students do not need to create accounts or remember passwords. Only college moderators log in as **Admin**.

---

## 2. High-Level Architecture

```mermaid
flowchart TD
    User["Student (Browser / Mobile)"]
    Admin["College Moderator / Admin"]

    subgraph Frontend["Frontend SPA (Tailwind CSS + SweetAlert2)"]
        UI["Single Page Web App (Vanilla JS)"]
    end

    subgraph Backend["Python Standard Web Server (src/handlers/http_handler.py)"]
        Server["Zero-Dependency HTTP Server"]
        AuthSvc["Auth Service (PBKDF2 Hashing)"]
        DBSvc["Database Manager (Dual-Mode)"]
        AILogic["Sarvam AI Vision Client"]
        CloudLogic["Cloudinary Upload Client"]
    end

    subgraph CloudServices["Cloud Infrastructure"]
        Supabase[("Supabase PostgreSQL")]
        Cloudinary[("Cloudinary Media CDN")]
        Sarvam["Sarvam AI API (gemma4 vision)"]
        WhatsApp["WhatsApp Web / App (wa.me)"]
        UptimeRobot["UptimeRobot (Pings /api/health)"]
    end

    User -->|Browse / Sell| UI
    Admin -->|Admin Login / Moderate| UI
    UI -->|REST API Calls| Server
    Server --> AuthSvc
    Server --> DBSvc
    Server --> AILogic
    Server --> CloudLogic

    DBSvc -->|SQL Queries| Supabase
    CloudLogic -->|Store Images| Cloudinary
    AILogic -->|Analyze Cover| Sarvam
    UI -->|Click-to-Chat| WhatsApp
    UptimeRobot -->|Keep-Alive Ping| Server
```

---

## 3. Technologies & Cloud Services Used

### 🐘 Supabase (PostgreSQL Database)
* **What it is**: A managed, cloud-hosted PostgreSQL relational database service.
* **Why we use it**:
  * Provides a persistent, scalable SQL database in the cloud.
  * Allows live inspection and management of data via Supabase SQL Editor and Table Viewer.
* **Dual-Mode Implementation (`src/database.py`)**:
  * **Production Mode**: When `DATABASE_URL` is configured in `.env`, the app connects to Supabase PostgreSQL using `psycopg2`.
  * **Offline/Dev Fallback**: If `DATABASE_URL` is absent or the network is unavailable, the application automatically falls back to a local SQLite database (`listings.db`), ensuring zero downtime during local development.
* **Connection Details**:
  * Connected using standard PostgreSQL connection strings:
    `postgresql://postgres.<project_ref>:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres`
  * Special characters in passwords (e.g., `@`) are safely URL-encoded (`%40`).

---

### ☁️ Cloudinary (Image Storage & CDN)
* **What it is**: An enterprise media management and Content Delivery Network (CDN).
* **Why we use it**:
  * Cloud hosting platforms like Render have **ephemeral filesystems** (local files are erased on restart/redeploy).
  * Direct database BLOB storage bloats database backups and slows down query response times.
* **How it works (`src/services/cloudinary_service.py`)**:
  1. The user uploads a photo of their book on the frontend.
  2. The image is converted into a Base64 data URI in the browser.
  3. The server receives the data URI and streams it directly to Cloudinary using `cloudinary.uploader.upload()`.
  4. Cloudinary automatically compresses the image, strips metadata, and generates an optimized HTTPS CDN link (e.g., `https://res.cloudinary.com/axlacmp5/image/upload/v1234.../pict_books/...jpg`).
  5. Only this lightweight HTTPS link is stored in Supabase PostgreSQL.

---

### 🇮🇳 Sarvam AI (Multimodal Vision & Context Extraction)
* **What it is**: India's foundational AI platform specialized in Indian regional context and languages.
* **Why we use it**:
  * Indian engineering textbooks (Nirali Publications, TechKnowledge, Technical Publications, SPPU Decodes) have specific title layouts and regional syllabi that standard US models frequently misclassify.
* **Models Used (`src/services/sarvam_service.py`)**:
  * **Vision Model (`gemma4`)**: Extracts text, detected titles, subjects, and book condition from the book cover photo.
  * **Chat Model (`sarvam-105b-conversations`)**: Structures raw text into a strict JSON payload mapping directly to SPPU departments (`Computer`, `IT`, `EnTC`, `AI&DS`, `General`), semester (`Semester 1` to `Semester 8`), condition (`Like New`, `Good`, `Acceptable`), and estimated MRP vs suggested resale price.

---

### 💬 WhatsApp Direct Commerce (`wa.me`)
* **What it is**: Peer-to-peer instant messaging commerce.
* **Why we use it**:
  * Eliminates payment gateway transaction cuts (Razorpay/Stripe charge 2-3% + GST).
  * Students already meet on campus daily (PICT Canteen, Reading Hall, Audi, Main Building).
  * Zero security risk: Buyers inspect books in person before paying via UPI (GPay/PhonePe).
* **Glitch-Free Message Formatting**:
  * Avoids 4-byte UTF-8 emojis that cause the famous Windows WhatsApp protocol bug (which converts emojis into black question mark diamonds ``).
  * Uses WhatsApp native Markdown `- *Item:* <Title>` which automatically displays as bold headers and crisp bullet points across all desktop and mobile apps.

---

### 🚀 Render & UptimeRobot (Hosting & Anti-Cold Start)
* **Render**: Hosts the Python application as a live Web Service connected directly to the GitHub repository (`main` branch) for continuous automated deployment.
* **Cold-Start Elimination**:
  * Render's free tier puts services to sleep after 15 minutes of inactivity, causing a 50-second delay ("cold start") for the next user.
  * **Solution**: A dedicated `/api/health` endpoint was implemented.
  * **UptimeRobot Integration**: An external UptimeRobot HTTP monitor pings `https://pict-olx-8tvs.onrender.com/api/health` every 5 minutes, keeping the server permanently warm and responsive 24/7.

---

### 🎨 Frontend: Tailwind CSS & SweetAlert2
* **Tailwind CSS (via CDN)**: Fully responsive, mobile-first campus marketplace UI with PICT navy blue (`#0f172a`) and gold amber accents.
* **SweetAlert2 (`swal2`)**: Replaced ugly native browser `alert()` and `confirm()` popup boxes with stylish animated modals, non-blocking toast notifications, and destructive action confirmation dialogs.

---

## 4. User Flow & Student Experience

### Flow A: Buyer (Junior looking for books)
1. Visits `https://pict-olx-8tvs.onrender.com/`.
2. Filters by Department (`Computer`, `IT`, `EnTC`, `AI&DS`) or searches by subject keyword (e.g., `Data Structures`, `M3`, `Microprocessor`).
3. Clicks **"Buy on WhatsApp"** on any study material card.
4. WhatsApp immediately opens with a pre-formatted message:
   ```text
   Hi Senior!
   I saw your study material listing on PICT Campus Marketplace:

   - Item: Data Structures and Algorithms
   - Subject: DSA
   - Dept & Year: Computer (SE - Semester 3)
   - Type: Textbook (Condition: Like New)
   - Price: Rs. 180

   Is this still available to collect on campus?
   ```
5. Senior and Junior agree on a campus meeting spot (e.g., PICT Canteen) and finish the transaction.

### Flow B: Seller (Senior listing old books)
1. Opens the **"List Study Material"** tab.
2. Uploads or drags a photo of their book.
3. **Sarvam AI** automatically scans the image, auto-populating Title, Subject, Branch, Year, Condition, and suggested selling price.
4. Seller enters their name and WhatsApp number.
5. Clicks **"Publish to PICT Marketplace"**. The image is uploaded to Cloudinary, saved to Supabase, and live in under 2 seconds.

---

## 5. Admin & Moderation System

To keep the platform safe from non-academic spam without forcing regular students to register accounts:
* Normal students browse and post freely without passwords.
* **Campus Admin (`admin@pict.edu`)** logs in via the **"Admin Login"** portal button in the header.
* **Admin Privileges**:
  * <i class="fa-solid fa-pen"></i> **Edit Listing**: Edit titles, departments, price, or description of any post.
  * <i class="fa-solid fa-trash"></i> **Delete Listing**: Permanently remove inappropriate or duplicate items with SweetAlert2 confirmation.
  * <i class="fa-solid fa-check"></i> **Toggle Sold Status**: Mark items as `SOLD` or reactivate them as `Available`.
* **Password Security**: Admin passwords are encrypted using `PBKDF2-HMAC-SHA256` with individual cryptographic salt and session tokens stored in the `sessions` table.

---

## 6. Database Schema & Design

The database maintains 3 core relational tables:

### Table 1: `users`
Stores administrator and registered account details.
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique user ID |
| `name` | VARCHAR(255) | Name of user or administrator |
| `email` | VARCHAR(255) UNIQUE | Contact or admin email |
| `phone` | VARCHAR(50) | WhatsApp phone number |
| `password_hash` | VARCHAR(255) | Salted PBKDF2 hash |
| `is_admin` | BOOLEAN | `TRUE` for moderators, `FALSE` for regular users |
| `created_at` | TIMESTAMP | Account creation date |

### Table 2: `sessions`
Tracks active logged-in tokens.
| Column | Type | Description |
|---|---|---|
| `token` | VARCHAR(255) PRIMARY KEY | Cryptographic session token |
| `user_id` | INTEGER REFERENCES users(id) | Linked user ID |
| `created_at` | TIMESTAMP | Session issue timestamp |

### Table 3: `listings`
Stores study material listings.
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Listing identifier |
| `user_id` | INTEGER | Seller user ID (or NULL for guest sellers) |
| `title` | VARCHAR(255) | Title of book, notes, or instrument |
| `subject` | VARCHAR(255) | Subject name (e.g. CNS, DBMS, IIDTL) |
| `department` | VARCHAR(100) | SPPU Branch: Computer, IT, EnTC, AI&DS, General |
| `target_year` | VARCHAR(50) | Academic year: FE, SE, TE, BE |
| `semester` | VARCHAR(50) | Semester 1 through 8 |
| `material_type` | VARCHAR(100) | Textbook, Handwritten Notes, Drafter, Question Bank |
| `condition` | VARCHAR(50) | Like New, Good, Acceptable |
| `price_inr` | INTEGER | Selling price in Rupees |
| `original_mrp` | INTEGER | Original MRP on book cover |
| `description` | TEXT | Description or extra notes |
| `image_url` | TEXT | Cloudinary secure CDN URL |
| `seller_name` | VARCHAR(255) | Name of senior seller |
| `seller_contact`| VARCHAR(100) | WhatsApp contact number |
| `is_sold` | BOOLEAN | `TRUE` if sold out, default `FALSE` |
| `created_at` | TIMESTAMP | Post creation timestamp |

---

## 7. API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | Serves the single-page application frontend | No |
| `GET` | `/api/listings` | Returns all study material listings | No |
| `POST` | `/api/listings` | Creates a new study material listing (Cloudinary upload) | No |
| `POST` | `/api/analyze` | Scans uploaded book cover image using Sarvam AI | No |
| `GET` | `/api/config` | Returns public college configuration | No |
| `GET` | `/api/health` | Health endpoint for UptimeRobot monitoring | No |
| `POST` | `/api/auth/login` | Authenticates Admin and returns session token | No |
| `POST` | `/api/auth/logout` | Revokes the current session token | Yes (Bearer Token) |
| `GET` | `/api/auth/me` | Returns current user details and admin privileges | Yes (Bearer Token) |
| `POST` | `/api/listings/<id>/sold` | Toggles item sold status | Yes (Owner or Admin) |
| `DELETE`| `/api/listings/<id>` | Permanently removes listing | Yes (Owner or Admin) |
| `POST` | `/api/listings/<id>/edit` | Edits listing details | Yes (Owner or Admin) |

---

## 8. Environment Variables Guide (`.env`)

Create a `.env` file in the root directory (based on `.env.example`):

```env
# ===================================================
# Administrator Credentials
# ===================================================
ADMIN_EMAIL=admin@pict.edu
ADMIN_PASSWORD=admin123

# ===================================================
# Sarvam AI Vision & Chat Credentials
# https://dashboard.sarvam.ai
# ===================================================
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_VISION_MODEL=gemma4
SARVAM_CHAT_MODEL=sarvam-105b-conversations

# ===================================================
# Database Configuration (Supabase PostgreSQL)
# ===================================================
DATABASE_URL=postgresql://postgres.your_project:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
DATABASE_NAME=listings.db

# ===================================================
# Cloudinary Image Storage & CDN
# https://cloudinary.com/console
# ===================================================
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ===================================================
# College & Regional Settings
# ===================================================
COLLEGE_NAME=PICT
COLLEGE_FULL_NAME=Pune Institute of Computer Technology
UNIVERSITY_NAME=SPPU
WHATSAPP_DEFAULT_COUNTRY_CODE=91
DEFAULT_CURRENCY=INR
```

---

## 9. Local Setup & Deployment Guide

### Local Development Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/pankajadsul622008-blip/PICT_OLX.git
   cd PICT_OLX
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

4. **Run the server**:
   ```bash
   python app.py
   ```
   Open your browser at `http://localhost:8000/`.

---

### Deploying to Render

1. Create a new Web Service on [Render Dashboard](https://dashboard.render.com).
2. Connect your GitHub repository `PICT_OLX`.
3. Set the following build options:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python app.py`
4. Add all keys from your `.env` into Render's **Environment Variables** tab.
5. Click **Deploy**.

---

### Setting up UptimeRobot (Preventing Cold Starts)

1. Sign up for free at [UptimeRobot](https://uptimerobot.com).
2. Click **Add New Monitor**:
   * **Monitor Type**: `HTTP(s)`
   * **Friendly Name**: `PICT Marketplace Warm-up`
   * **URL**: `https://your-service-name.onrender.com/api/health`
   * **Monitoring Interval**: `Every 5 minutes`
3. Click **Create Monitor**. Your application will now stay permanently awake 24/7!

---

## 10. Key Bugs Solved & Architectural Decisions

1. **Windows WhatsApp Protocol Diamond Glitch (``)**:
   * *Problem*: Windows protocol handler decoded 4-byte UTF-8 emojis (`👋`, `📦`, `📚`, `💰`) as Latin-1, causing Unicode corruption into black question marks.
   * *Fix*: Replaced all emojis with native WhatsApp bullet Markdown (`- *Item:* ...`), which natively renders bold headers and bullets across all devices.

2. **Special Characters in Database Password**:
   * *Problem*: Supabase generated passwords containing `@` symbols, causing URL parsing failures in `psycopg2`.
   * *Fix*: Implemented URL encoding (`%40`) in database connection handlers.

3. **PostgreSQL DateTime JSON Serialization**:
   * *Problem*: `psycopg2` returns PostgreSQL `created_at` timestamps as native Python `datetime.datetime` objects, throwing `TypeError: Object of type datetime is not JSON serializable` in standard Python `json.dumps`.
   * *Fix*: Added `default=str` serialization parameter to the central JSON response writer.

4. **Ephemeral Filesystem on Cloud Hosting**:
   * *Problem*: Files uploaded to disk on free cloud hosts (Render, Heroku) disappear whenever the server restarts or deploys.
   * *Fix*: Routed all uploaded images directly through Cloudinary CDN, persisting only secure HTTPS URLs in Supabase PostgreSQL.

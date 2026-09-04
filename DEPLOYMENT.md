# 🚀 Hosting & Deployment Guide: CutoffGrid AI

This guide walks you through hosting both the **Frontend (React + Vite)** and **Backend (FastAPI + MongoDB Atlas)** for free/production environments.

---

## 🏗️ Architecture Overview

| Component | Technology | Recommended Host | Free Tier Available? |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 19 + Vite + Tailwind | **Vercel** / **Netlify** | ✅ Yes (100% Free) |
| **Backend** | Python FastAPI + Uvicorn | **Render** / **Railway** | ✅ Yes (Free tier) |
| **Database** | MongoDB Atlas Cluster | **MongoDB Atlas** | ✅ Yes (M0 Free Cluster) |

---

## ⚡ Option 1: Vercel (Frontend) + Render (Backend) [Recommended]

### Part 1: Deploy Backend on Render

1. **Push your repository** to GitHub.
2. Sign in to [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Fill in the settings:
   - **Name**: `cutoffgrid-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add the variables from `backend/.env`:
   - `MONGO_URI`: `your_mongodb_atlas_connection_string`
   - `JWT_SECRET_KEY`: `your_random_secret_key`
   - `FAST_TO_SMS_API_KEY`: `your_fast2sms_key`
   - `OTP_MODE`: `production` (or `development`)
   - `GROQ_API_KEY`: `your_groq_key`
   - `SMTP_USERNAME` & `SMTP_PASSWORD`: `your_email_credentials`
6. Click **Create Web Service**. Once deployed, copy your backend URL (e.g. `https://cutoffgrid-backend.onrender.com`).

---

### Part 2: Deploy Frontend on Vercel

1. Sign in to [Vercel.com](https://vercel.com) and click **Add New** -> **Project**.
2. Import your GitHub repository.
3. In the project configuration:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://cutoffgrid-backend.onrender.com` *(Replace with your live Render backend URL)*
5. Click **Deploy**.
6. Your site will be live instantly with global CDN and SSL!

---

## 🐳 Option 2: Docker / VPS Deployment

If you are hosting on a VPS (DigitalOcean, AWS EC2, Linode, Hetzner, etc.):

```bash
# 1. Clone your repository on your server
git clone <your-repo-url>
cd Cut-Off-Guide-AI1

# 2. Configure your environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your production credentials

# 3. Build and launch with Docker Compose
docker compose up -d --build
```

- **Frontend** will be served on port `5173` (or mapped to port `80`/`443`).
- **Backend** will run on port `8000`.

---

## 🧪 Local Running Instructions

Both servers can be started locally at any time:

### Quick Run (Windows)
Double-click `start_servers.bat` in the root folder.

### Manual Run
- **Backend**:
  ```bash
  cd backend
  venv\Scripts\activate
  python app.py
  ```
  Runs at: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)

- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```
  Runs at: `http://localhost:5173`

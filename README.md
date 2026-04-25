# Currency Exchange Backend

FastAPI backend service for the **Currency Exchange App**, providing user signup with OTP verification, login, currency conversion, and account management. Deployed on **Render Web Services** with a **Supabase Postgres database**.

---

## Features
- Sign up with OTP email verification
- Login with JWT tokens
- Currency conversion using live rates
- Account deletion with history cleanup
- Supabase Postgres integration with Alembic migrations
- Secure password hashing & environment variable management

---

## Project Structure
backend/
│── main.py                # FastAPI entrypoint
│── auth/                  # Authentication routes
│── currency.py            # Currency conversion routes
│── email_service.py       # OTP email sending
│── models.py              # Pydantic models
│── database.py            # DB session setup
│── database_models.py     # SQLAlchemy ORM models
│── utils.py               # Helper functions
│── alembic/               # Migration scripts
│── requirements.txt       # Dependencies
│── README.md              # Project documentation

---

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/Currency_Exchange_Backend.git
   cd Currency_Exchange_Backend
Create virtual environment & install dependencies:

bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt

Configure .env:
DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
SECRET_KEY=your_jwt_secret
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=YourName


Running Locally
uvicorn main:app --reload
Docs available at: http://127.0.0.1:8000/docs



Deployment (Render)
Push repo to GitHub
Create new Web Service on Render
Add environment variables in Render dashboard
Render builds & deploys automatically


API Endpoints
POST /signup → Register user, send OTP
POST /signup/verify_otp → Verify OTP, create account
POST /login → Login, get JWT token
POST /currency/currency_converter → Convert currency
DELETE /currency/delete → Delete account & history



License
MIT License — free to use and modify.



# 📚 Peer-to-Peer Book & Notes Exchange Platform

A feature-rich **Django** web application designed for students and readers to list, wishlist, match, and exchange physical books and study notes seamlessly through peer-to-peer trading.

---

## 🌟 Key Features

- **📖 Book & Notes Listings**: Post listings with details including item type (Book/Notes), condition (New, Good, Fair, Poor), course/subject, description, and images.
- **❤️ Wishlist System**: Express interest in listings posted by other users to trigger automated trade matching.
- **🔄 Algorithmic Smart Matching Engine**:
  - **Direct 2-Way Swaps**: Automatically identifies mutual trade opportunities when User A wants User B's item and User B wants User A's item.
  - **3-Way Circular Swaps**: Advanced circular matching algorithm ($A \rightarrow B \rightarrow C \rightarrow A$) that enables trades even when direct reciprocal interest isn't available!
- **📅 Pickup Scheduling & Conflict Validation**: Schedule in-person pickup times with built-in time validation that prevents scheduling conflicts for users within 30-minute windows.
- **✅ Multi-Party Verification**: Built-in verification workflow where all involved trade participants confirm pickup completion before updating item status.
- **👤 User Dashboard & Profiles**: Track active listings, wishlist items, pending swap matches, and upcoming pickup schedules in a unified view.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Django 5.x
- **Database**: SQLite3 (or PostgreSQL / MySQL compatible)
- **Frontend**: HTML5, CSS3, JavaScript, Django Templates
- **Authentication**: Custom Django User Model with authentication views

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` (Python package manager)
- `virtualenv` (recommended)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ManishPal91/Peer-to-Peer-Book-Notes-Exchange.git
   cd Peer-to-Peer-Book-Notes-Exchange
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django pillow
   ```

4. **Apply Database Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser (Optional for Admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 📂 Project Structure

```
Peer-to-Peer-Book-Notes-Exchange/
├── exchange/                 # Main Django Application
│   ├── migrations/           # Database Migration History
│   ├── admin.py              # Django Admin Configurations
│   ├── forms.py              # User & Listing Forms
│   ├── models.py             # Database Models (User, Listing, Wishlist, SwapMatch, PickupSchedule)
│   ├── urls.py               # Application URL Routing
│   ├── utils.py              # Matching Algorithm (2-Way & 3-Way Circular Swaps)
│   └── views.py              # View Functions & Business Logic
├── p2pexchange/              # Django Project Core Configuration
│   ├── settings.py           # Project Settings
│   ├── urls.py               # Main URL Dispatcher
│   └── wsgi.py               # WSGI Entry Point
├── static/                   # Static Assets (CSS, JS, Images)
├── templates/                # HTML Templates (Dashboard, Listings, Matches, Auth)
├── media/                    # User Uploaded Images
├── db.sqlite3                # Local SQLite Database
├── manage.py                 # Django Management CLI Tool
└── README.md                 # Project Documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a pull request.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

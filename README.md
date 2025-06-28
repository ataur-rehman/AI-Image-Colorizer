# Prismify – AI Image Colorizer

✨ **Prismify** is a modern web application that breathes life into black-and-white images using AI colorization. Beyond transforming photos with realistic colors, it offers advanced editing tools like contrast, blur, and saturation adjustments. Users can securely manage their images, compare results side-by-side, and keep a history of their creations—all from a sleek, responsive interface.

---

## Project Overview

The aim of Prismify is to simplify AI-driven image colorization for everyday users. Whether reviving old family photos or enhancing creative projects, Prismify provides a fast, intuitive solution. Users can upload grayscale images, instantly colorize them with an AI model, and fine-tune results with built-in editing tools—no technical expertise required.

---

## Screenshots
  <div style="display: flex; justify-content: space-between; gap: 10px;">
<img src="home.png" alt="Home Page" width="250" />
<img src="signup.png" alt="SignUp Page" width="250" />
<img src="dashboard.png" alt="Dashboard" width="250" />
</div>

<div style="display: flex; justify-content: space-between; gap: 10px; margin-top: 20px;">
<img src="upload.png" alt="Upload Page" width="250" />
<img src="canvas.png" alt="Editing Page" width="250" />
<img src="colorize.png" alt="Colorize Page" width="250" />
</div>

## Features

- **AI-Powered Colorization** – Transform black-and-white images into vivid color with a pre-trained AI model.
- **Advanced Editing Tools** – Adjust contrast, saturation, and blur for perfect results.
- **Before/After Comparison** – View original and colorized images.
- **User Authentication** – Sign up, log in, and manage personal accounts.
- **Image History & Gallery** – Access previously colorized and edited images.
- **Responsive Web Interface** – Smooth experience across devices.

---

## Problem Statement

Many users want to restore or creatively enhance old black-and-white photos but lack the technical skills or expensive software required for colorization and editing. **Prismify** provides a **centralized, user-friendly solution**, bringing AI colorization and image editing to everyone via an accessible web platform.

---

## Tech Stack

- **Backend:** Django
- **Frontend:** HTML, CSS, custom stylesheets
- **AI Model:** Pre-trained `colorization_release_v2.caffemodel` (Caffe framework)
- **Database:** SQLite (for development) → PostgreSQL recommended for production

---

##  Demo

*(Replace these with your actual links once available!)*

🌐 **Live Demo:** [Link here](#)  
🎥 **Video Demo on YouTube:** [Watch Demo](#)

---

##  Installation & Setup

1. Clone the Repository
git clone https://github.com/ataur-rehman/AI-Image-Colorizer.git
cd prismify

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Apply Migrations
python manage.py migrate

5. Download the AI Model
Prismify uses the pre-trained Caffe model:

Download:

colorization_release_v2.caffemodel (add your actual link here)

Place it in:
prismify/image_app/colorizer/

6. Run the Development Server
python manage.py runserver
Then visit:

http://127.0.0.1:8000/

📚 Resources & Documentation
If you’re new to Django or AI colorization:

Django Documentation

Richard Zhang’s Colorization Model

Python Virtual Environments

🌱 Future Enhancements
Deployment to cloud platforms (e.g. Heroku, AWS)

Support for additional editing effects

Batch processing of multiple images

🙌 Acknowledgements
Colorization model by Richard Zhang et al.

Django community for powerful web tools

📬 Contact & Support
💼 GitHub: https://github.com/ataur-rehman
📩 Email: ataurrehman3636@gmail.com

⭐ If you like this project, consider giving it a star on GitHub! ⭐

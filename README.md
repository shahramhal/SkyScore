##SkyScore
SkyScore is a machine learning application that analyzes and scores sky images based on their aesthetic quality, clarity, and celestial object visibility. The project enables both automated batch processing of sky images and an interactive web interface for real-time scoring.
Overview
SkyScore combines computer vision and machine learning techniques to evaluate sky photographs. It can detect and analyze various features including:

Cloud coverage and patterns
Sky clarity and visibility
Presence of celestial objects (stars, moon, planets)
Color distribution and light pollution
Overall aesthetic composition

The scoring algorithm produces both an overall quality score and specific subscores for different aspects of the image.
Features

Batch Processing: Process directories of images to generate score reports
Web Interface: Upload and score images through an intuitive browser-based UI
Detailed Analytics: Receive comprehensive breakdown of image qualities
Score Visualization: Visual representation of scoring metrics
Export Options: Save results in multiple formats (CSV, JSON, PDF)

Installation
Prerequisites

Python 3.8+
TensorFlow 2.5+
OpenCV 4.5+
Django 3.2+ (for web interface)

Setup

Clone the repository:
git clone https://github.com/shahramhal/SkyScore.git
cd SkyScore

Install dependencies:
pip install -r requirements.txt

Apply database migrations:
python manage.py migrate

Download pre-trained models:
python manage.py download_models

Create a superuser (optional):
python manage.py crea

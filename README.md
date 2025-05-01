# SkyScore

A Django-based web application for analyzing and scoring sky images using machine learning.

## Features

- Analyze sky photographs for clarity, celestial objects, and aesthetic quality
- Score images based on multiple metrics
- Process individual images or batch uploads
- View detailed score breakdowns and visualizations
- Export results in various formats

## Setup

```bash
# Clone repository
git clone https://github.com/shahramhal/SkyScore.git
cd SkyScore

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

## Usage

1. Upload sky images via the web interface at http://localhost:8000
2. View scores and detailed analytics
3. Export results as needed

## Requirements

- Python 3.8+
- Django 3.2+


## License

MIT

## Author

Shahram Hal - [GitHub](https://github.com/shahramhal)

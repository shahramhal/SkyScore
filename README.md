# SkyScore

SkyScore is a web-based application designed to streamline the "Health Check" technique used by SKY's Engineering Department to assess the operational health of their engineering teams. Inspired by Spotify's Squad Health Check model, this application replaces the traditional spreadsheet method with a dynamic, user-friendly interface that reduces data entry errors and improves data accessibility.
# Screenshots 
![image](https://github.com/user-attachments/assets/91278e11-df9f-4d43-8a87-ce523980cd24)
![image](https://github.com/user-attachments/assets/fc39cfdb-c85e-45e1-9a63-be63b5cdd00e)
![Uploading image.png…]()
![image](https://github.com/user-attachments/assets/cef2817d-2da9-416c-a945-f0e6ae58b594)
![image](https://github.com/user-attachments/assets/5c831b6f-d24e-41ab-8d86-353c8046212b)
![image](https://github.com/user-attachments/assets/ede6a14a-e52f-4275-b428-56aacab2b55f)
![image](https://github.com/user-attachments/assets/dcec55af-40db-47d3-b2b0-bfb8a90ac2cf)
![image](https://github.com/user-attachments/assets/998b59be-e245-49ae-9916-8f89c43dbdd4)

## Features
**User Roles**: Supports multiple user roles including Engineers, Team Leaders, Department Leaders, and Senior Managers, each with tailored functionalities.
- **Self-Registration**: Users can create accounts and log in securely to access the system.
- **Health Check Sessions**: Users can select sessions to record their team's health status using a traffic light system (Green, Amber, Red).
- **Progress Tracking**: Users can note whether progress is improving or declining and save their opinions.
- **Data Visualization**: Provides summaries and progress visualizations for teams, departments, and the entire organization.
- **Admin Panel**: Django admin interface for managing users, teams, departments, and health check cards.



## Setup


# Clone repository
```bash
git clone https://github.com/shahramhal/SkyScore.git
cd SkyScore
```
# Install dependencies
```bash
pip install -r requirements.txt
```
# Apply migrations
```bash
python manage.py migrate
```
# Run development server
```bash
python manage.py runserver
```

# Open http://127.0.0.1:8000 in your browser to access the application.

# Create a superuser for admin page 
```bash
python manage.py createsuperuser
```
# Access the admin panel at http://127.0.0.1:8000/admin


## Technical Stack
- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: JavaScript, Bootstrap
- **Version Control**: Git (hosted on GitHub)


## Requirements

- Python 3.8+
- Django 3.2+


## License

MIT

## Acknowledgments

Coursework brief by University of Westminster.

Inspired by Spotify's Health Check Model.

Mentorship from SKY Engineering Department.

## Authors

Shahram Halimzoda  - [GitHub](https://github.com/shahramhal)
Muhammad Khizr -  [GitHub](https://github.com/khiziii)
Imaad Malik -  [GitHub](https://github.com/Imaad117)
Hamza Hassan -  [GitHub](https://github.com/HamzaHassan21)
MD Tayefur Rahman Salman -  [GitHub](https://github.com/TRS-Salman)

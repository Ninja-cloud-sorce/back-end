# Back-End Project

This is a Python backend project powered by **FastAPI** and **Uvicorn**.  
It provides APIs for handling requests and is designed to run in a virtual environment.

Step 2: Create & Activate Virtual Environment
Make sure you have Python 3.9+ installed.
python -m venv .venv

Windows (PowerShell):
.venv\Scripts\activate

Step 3: Install Dependencies
pip install -r requirements.txt

uvicorn main:app --reload --reload-exclude ".venv/*"

🛠 Tech Stack
	•	Python
	•	FastAPI
	•	Uvicorn

 ✨ Features
	•	RESTful API development with FastAPI
	•	Hot-reload enabled with Uvicorn
	•	Environment isolation using .venv

 🤝 Contribution
	1.	Fork this repository
	2.	Create your feature branch (git checkout -b feature/my-feature)
	3.	Commit your changes (git commit -m 'Add new feature')
	4.	Push to the branch (git push origin feature/my-feature)
	5.	Open a Pull Request

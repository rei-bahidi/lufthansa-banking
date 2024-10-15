# Lufthansa Banking

A simple django project to imitate a banking process. Most of the testing is done and all functionalities as well. Unfortunately no frontend :(. Maybe I can whip something a bit later.

# Startup

- Start the venv with `python3 -m venv venv` (be careful with the python version, only python3.10+) 
- The project relies on docker for launching the database along with the adminer interface so you need to run `docker compose up -d`
- Log in to the environment with `source venv/bin/activate` if on linux and `./venv/bin/Activate.ps1` if on windows
- After activating the environment install the requirements in the requirements.txt file with `pip install -r requirements.txt`
- From the root of the directory run `python3 lufthansa_banking/manage.py migrate` to migrate the models to the postgres database
- To run tests get into the lufthansa_banking directory and run `pytest`


# Author

Rei Bahidi



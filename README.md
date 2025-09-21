# Python-Based Command Terminal
This project is a web-based terminal interface created using Python and Flask.  
It allows users to execute basic terminal commands (like `ls`, `cd`, `mkdir`, `rm`) via a web browser.

Problem Statement
Develop a fully functioning command terminal that mimics the behavior of a real system terminal. The backend of this terminal is built in Python, providing a web-based or command-line interface to execute standard system commands.

Description
This project implements a Python-powered terminal emulator capable of executing typical filesystem commands such as ls, cd, mkdir, rm, and pwd. It also handles invalid command errors gracefully and integrates system monitoring features to report CPU, memory, and process status. The system aims to closely mimic real terminal behavior with efficient and extensible design.

## Features

- Command execution through a clean web interface.
- Basic directory and file operations support.
- Flask used for backend and serving HTML templates.
- Easy to extend and customize commands.

## Project Structure
```bash
assignment-folder/
├── app.py or main.py # Main Flask app entry point
├── requirements.txt # Python package dependencies
├── templates/ # HTML templates folder
│ └── index.html # Main web interface HTML page
├── terminal.py # Command terminal implementation
└── README.md # This file
```
## Installation

1. Ensure Python 3.8+ is installed on your system.
2. Install dependencies by running:
```bash
python -m pip install -r requirements.txt
```
## Running the Application

Run the Flask app using:
```bash
python main.py
```

Then open your browser and navigate to 
```bash
[http://127.0.0.1:5000](http://127.0.0.1:5000) (or the URL shown in console).
```



## Contact

Your Name - srija_chakilam@srmap.edu.in




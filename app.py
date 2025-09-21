"""
Web-based Terminal Interface
A Flask web application for the Python terminal
"""

from flask import Flask, render_template, request, jsonify
from terminal import PythonTerminal
import threading
import time

app = Flask(__name__)
terminal = PythonTerminal()

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    command = data.get('command', '')
    
    exit_code, output = terminal.run_command(command)
    
    return jsonify({
        'exit_code': exit_code,
        'output': output,
        'prompt': terminal.display_prompt()
    })

@app.route('/status')
def status():
    return jsonify({
        'current_directory': terminal.current_directory,
        'prompt': terminal.display_prompt()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
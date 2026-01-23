
import sys
import os
import subprocess
import threading
from typing import Dict, Any

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from zk_stark_demo.gui.discovery import get_implementations, get_schema

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/implementations")
def list_implementations():
    return jsonify(get_implementations())

@app.route("/api/schema/<implementation>/<cli_type>")
def get_cli_schema(implementation, cli_type):
    if cli_type not in ["prover", "verifier"]:
        return jsonify({"error": "Invalid type. Must be 'prover' or 'verifier'"}), 400
        
    schema = get_schema(implementation, cli_type)
    if "error" in schema:
        return jsonify(schema), 404
    return jsonify(schema)

def run_process_and_stream(command: list[str], log_prefix: str):
    """
    Run a subprocess and stream its output to the websocket.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1, # Line buffered
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")) # Project root
        )
        
        for line in process.stdout:
            socketio.emit("log", {"source": log_prefix, "message": line.strip()})
            
        process.wait()
        socketio.emit("log", {"source": log_prefix, "message": f"Process exited with code {process.returncode}"})
            
    except Exception as e:
        socketio.emit("log", {"source": log_prefix, "message": f"Error starting process: {str(e)}"})

@app.route("/api/run", methods=["POST"])
def run_cli():
    data = request.json
    implementation = data.get("implementation")
    cli_type = data.get("type")
    args = data.get("args", {})
    
    if not implementation or cli_type not in ["prover", "verifier"]:
        return jsonify({"error": "Invalid request parameters"}), 400
        
    # Construct command
    # Assuming python -m zk_stark_demo.cli.<impl>.<type>_cli
    module_name = f"zk_stark_demo.cli.{implementation}.{cli_type}_cli"
    command = [sys.executable, "-m", module_name]
    
    # Add args
    for key, value in args.items():
        if value is True: # Flag
             command.append(f"--{key}")
        elif value is False or value is None:
             continue
        else:
             command.append(f"--{key}")
             command.append(str(value))
             
    log_prefix = f"[{implementation.capitalize()}-{cli_type.capitalize()}]"
    
    # Start in background thread
    thread = threading.Thread(target=run_process_and_stream, args=(command, log_prefix))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "command": " ".join(command)})

def run_server(debug=True, port=5000):
    socketio.run(app, debug=debug, port=port)

if __name__ == "__main__":
    run_server()

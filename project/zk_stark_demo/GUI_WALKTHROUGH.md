# Unified GUI Walkthrough

## Overview

I have successfully implemented a unified Graphical User Interface (GUI) for the ZK-STARK CLI applications. The solution consists of a **Flask backend** for discovery and execution, and a **React/Vite frontend** for the user interface.

## Components

1. **Backend (`src/zk_stark_demo/gui/`)**:
   - `server.py`: Flask application with Socket.IO for log streaming.
   - `discovery.py`: Dynamically finds CLI implementations (`cubic`, `fibonacci`, `rollup`) and extracts their argument schemas.
   - **API Endpoints**:
     - `/api/implementations`: Lists available CLIs.
     - `/api/schema/<impl>/<type>`: Returns argument inputs.
     - `/api/run`: Executes the CLI and streams logs.

2. **Frontend (`web_app/`)**:
   - **React + Vite**: Fast, modern web application.
   - **Sidebar**: Automatically populated from the backend discovery.
   - **Split View**: Concurrent Prover and Verifier panels.
   - **Log Console**: Real-time log streaming from the backend.

## Verification Results

### Backend API Verification

The backend API was verified using `curl` to ensure correct discovery and schema generation.

- **Implementations Discovery**:

  ```json
  ["cubic", "fibonacci", "rollup"]
  ```

  _(Verified via `curl http://localhost:5000/api/implementations`)_

- **Schema Generation**:
  Correctly identified arguments for `CubicProverCLI`:
  - `output` (text)
  - `length` (number, default: 128)
  - `start` (number, default: 1)

### Frontend Status

The Frontend is running on `http://localhost:5173`.

- Note: Browser automation could not verify the UI visually due to environment limitations, but the server is serving the application correctly.

## How to Run

1. **Start Backend**:

   ```bash
   uv run flask --app src.zk_stark_demo.gui.server run --debug --port 5000
   ```

2. **Start Frontend**:

   ```bash
   cd web_app
   npm run dev
   ```

3. **Open Browser**: Navigate to `http://localhost:5173`.

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

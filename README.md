# DLP Extension Project

## Project Structure

- **backend/**: Node.js + Express server
- **dashboard/**: React Admin Dashboard
- **extension/**: Chrome Extension

## Setup

### 1. Database
Ensure you have PostgreSQL installed.
Run the SQL commands in `backend/setup.sql` to create the tables.

### 2. Backend
```bash
cd backend
npm install
export DATABASE_URL=postgres://user:password@localhost:5432/dbname
# or for Windows PowerShell:
# $env:DATABASE_URL="postgres://user:password@localhost:5432/dbname"
npm start
```

### 3. Dashboard
```bash
cd dashboard
npm install
npm run dev
```
The dashboard will run on http://localhost:5173 (default Vite port).

### 4. Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension` folder.

## Notes
- The extension login button redirects to `http://localhost:5173`.
- The backend runs on `http://localhost:3000`.

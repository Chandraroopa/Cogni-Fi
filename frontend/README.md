# CogniFi  — Frontend (Vite + React)

## Setup

```bash
npm install
npm run dev
```

App runs at `http://localhost:5173` by default.

## Structure

- `src/App.jsx` — routing (Member 1: Ankitha)
- `src/components/common/` — Navbar, Footer, ProtectedRoute (Member 1)
- `src/components/pages/Home.jsx` — landing page (Member 1)
- `src/components/pages/Login.jsx` — placeholder, Member 2 to build
- `src/components/pages/SignUp.jsx` — placeholder, Member 3 to build
- `src/components/pages/Dashboard.jsx` — placeholder, Member 4 to build
- `src/context/AuthContext.jsx` — placeholder stub, Member 2 to build real auth logic
- `src/services/api.js` — placeholder stub, Member 2 to configure real backend URL + interceptors

Each placeholder file has a comment block showing the expected structure so the
app compiles and runs before that member's real code is merged in.

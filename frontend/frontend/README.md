````markdown
# CogniFi

### Smart Public Wi-Fi Trust & Risk Scoring System

CogniFi is a smart cybersecurity system designed to analyze public Wi-Fi networks and determine their trustworthiness using behavioral network analysis and machine learning.

The system studies network metadata such as DNS response behavior, gateway latency, beacon intervals, packet-flow patterns, encryption status, and other network characteristics to identify potentially suspicious networks.

---

## 👥 Team Development Instructions

This repository is a shared project. Every member must follow the workflow below to avoid merge conflicts and accidentally overwriting another member's work.

### Before starting work

Always pull the latest changes before modifying anything:

```bash
git checkout main
git pull origin main
````

Then create your own feature branch:

```bash
git checkout -b feature/your-feature-name
```

Example:

```bash
git checkout -b feature/dashboard
```

Do NOT directly develop on `main`.

---

## 📁 Project Structure

```text
Cogni-Fi/
│
├── frontend/
│   ├── public/
│   │   ├── android-chrome-192x192.png
│   │   ├── android-chrome-512x512.png
│   │   ├── apple-touch-icon.png
│   │   ├── favicon-16x16.png
│   │   ├── favicon-32x32.png
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   └── cognifi-logo.png
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── Navbar.jsx
│   │   │   │   └── ProtectedRoute.jsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │
│   │   │   ├── home/
│   │   │   │   ├── CTASection.jsx
│   │   │   │   ├── FeaturesSection.jsx
│   │   │   │   ├── HeroSection.jsx
│   │   │   │   ├── HowItWorks.jsx
│   │   │   │   └── TrustScoreSection.jsx
│   │   │   │
│   │   │   └── pages/
│   │   │       ├── Dashboard.jsx
│   │   │       ├── Home.jsx
│   │   │       ├── Login.jsx
│   │   │       └── SignUp.jsx
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
└── README.md
```

---

# 🛠️ Technology Stack

### Frontend

* React.js
* Vite
* JavaScript
* Tailwind CSS
* React Router
* Lucide React
* Axios

### Backend

Backend development will be maintained separately from the frontend.

Expected technologies include:

* Node.js
* Express.js
* MongoDB
* REST API

### Cybersecurity / ML

The main CogniFi system is planned to use:

* Python
* Scapy / PyShark
* Wireshark
* Random Forest
* XGBoost
* Network behavioral analysis

---

# ⚙️ Initial Setup

## 1. Clone the repository

```bash
git clone https://github.com/Chandraroopa/Cogni-Fi.git
```

Enter the project:

```bash
cd Cogni-Fi
```

Enter the frontend:

```bash
cd frontend
```

---

## 2. Install dependencies

Run:

```bash
npm install
```

Do NOT delete `package-lock.json`.

Do NOT run unnecessary package installation commands without informing the team.

---

## 3. Start the development server

```bash
npm run dev
```

Vite will provide a local URL, usually:

```text
http://localhost:5173
```

---

# 🔄 Git Workflow

## IMPORTANT

Never directly push unfinished work to `main`.

### Step 1 — Get latest code

Before starting:

```bash
git checkout main
git pull origin main
```

### Step 2 — Create a branch

```bash
git checkout -b feature/feature-name
```

Examples:

```bash
git checkout -b feature/dashboard
git checkout -b feature/login
git checkout -b feature/risk-score
git checkout -b feature/network-scanner
```

---

# 💾 Commit Rules

Use clear and meaningful commit messages.

Follow this format:

```text
type: description
```

### Common types

```text
feat:     New functionality
fix:      Bug fix
style:    Styling/UI changes
refactor: Code restructuring
docs:     Documentation
chore:    Configuration/dependency changes
```

### Examples

```bash
git add .
git commit -m "feat: add responsive navigation bar"
```

```bash
git commit -m "feat: add CogniFi hero section"
```

```bash
git commit -m "feat: add network trust score section"
```

```bash
git commit -m "fix: resolve invalid icon import"
```

```bash
git commit -m "style: improve home page spacing"
```

```bash
git commit -m "refactor: split home page into reusable components"
```

---

# 🚀 Push Your Branch

After committing:

```bash
git push origin feature/your-feature-name
```

Example:

```bash
git push origin feature/dashboard
```

Then create a Pull Request on GitHub.

---

# 🔀 Pull Request Rules

Before creating a Pull Request:

```bash
git checkout main
git pull origin main
```

Then return to your branch:

```bash
git checkout feature/your-feature-name
```

Update your branch if necessary:

```bash
git merge main
```

Resolve any conflicts before creating the Pull Request.

---

# ⚠️ Important: Avoiding Merge Conflicts

### Before editing a file

Check whether another member is currently modifying it.

For example, do not simultaneously modify:

```text
Navbar.jsx
App.jsx
AuthContext.jsx
```

without informing the team.

### Avoid unnecessary changes

Do NOT:

* Reformat someone else's entire file
* Change indentation throughout unrelated code
* Rename files without informing the team
* Delete components created by another member
* Change package versions unnecessarily
* Modify configuration files unless required

Keep commits focused on your assigned task.

---

# ❌ Never Do This

Do NOT use:

```bash
git push --force
```

on `main`.

Do NOT use:

```bash
git reset --hard
```

unless you understand exactly what will be deleted.

Do NOT delete another member's changes to resolve a conflict without discussing it.

Do NOT commit:

```text
node_modules/
.env
.env.local
dist/
```

---

# 🔐 Environment Variables

If environment variables are required, create:

```text
.env
```

locally.

Never commit `.env` to GitHub.

Example:

```env
VITE_API_URL=http://localhost:5000/api
```

Each member should maintain their own local `.env`.

---

# 🧩 Component Organization

Reusable components should be placed according to their purpose.

### Common components

```text
src/components/common/
```

Examples:

```text
Navbar.jsx
Footer.jsx
ProtectedRoute.jsx
```

### Home page components

```text
src/components/home/
```

Examples:

```text
HeroSection.jsx
FeaturesSection.jsx
HowItWorks.jsx
TrustScoreSection.jsx
CTASection.jsx
```

### Page components

```text
src/components/pages/
```

Examples:

```text
Home.jsx
Login.jsx
SignUp.jsx
Dashboard.jsx
```

---

# 🏠 Home Page Structure

The Home page currently consists of:

```text
Navbar
   ↓
Hero Section
   ↓
Features Section
   ↓
How It Works
   ↓
Trust Score
   ↓
CTA Section
   ↓
Footer
```

The sections are kept as separate React components so that different team members can work independently.

---

# 🎨 UI Guidelines

CogniFi uses a cybersecurity-inspired visual theme.

### Primary colors

```text
Black
White
Cyan
Blue
Red
Glitch Pink
```

### General design style

* Dark UI
* Glassmorphism
* Cyan/blue glowing effects
* Subtle gradients
* Minimal borders
* Smooth hover transitions
* Responsive layouts
* Clean typography

Avoid introducing unrelated color schemes unless discussed with the team.

---

# 🧭 Navigation IDs

Sections that need to be accessible from the navigation should have the appropriate IDs.

Example:

```jsx
<section id="features">
```

```jsx
<section id="how-it-works">
```

```jsx
<section id="trust-score">
```

If adding a new section that needs navigation, inform the team before changing the navigation component.

---

# 📱 Responsive Design

Every component should work on:

* Mobile
* Tablet
* Laptop
* Desktop

Use Tailwind responsive utilities:

```text
sm:
md:
lg:
xl:
```

Test your changes at different screen widths before committing.

---

# 🧪 Before Pushing

Always check:

```bash
npm run build
```

If ESLint is configured:

```bash
npm run lint
```

Fix errors before pushing.

Also manually check:

* Navigation
* Buttons
* Links
* Mobile layout
* Desktop layout
* Authentication-dependent UI
* Console errors

---

# 🐛 If You Get a Git Conflict

Do NOT panic.

First check:

```bash
git status
```

Open the conflicted file.

You may see:

```text
<<<<<<< HEAD
your changes
=======
remote changes
>>>>>>> ...
```

Decide which changes should remain, then remove the conflict markers.

After fixing:

```bash
git add <filename>
```

Then continue according to whether you were merging or rebasing.

If unsure, STOP and ask the team before running destructive Git commands.

---

# 🔄 Recommended Daily Workflow

Every time you start working:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
```

Work on your feature.

Then:

```bash
git status
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

Create a Pull Request.

After your PR is merged, delete the old branch if no longer needed.

---

# 👥 Team Responsibilities

Each member should:

* Work primarily on their assigned components
* Pull before starting new work
* Use feature branches
* Make small focused commits
* Use meaningful commit messages
* Test before pushing
* Inform the team before modifying shared files
* Never force-push to `main`

---

# 📌 Current Development Status

### Frontend

* [x] React + Vite setup
* [x] Tailwind CSS setup
* [x] React Router setup
* [x] Authentication context structure
* [x] Responsive Navbar
* [x] Responsive mobile navigation
* [x] Home page structure
* [x] Hero Section
* [x] Features Section
* [x] How It Works section
* [x] Trust Score section
* [x] CTA section
* [x] Footer
* [ ] Login implementation
* [ ] Sign Up implementation
* [ ] Dashboard implementation
* [ ] Network scanning
* [ ] Network behavioral analysis
* [ ] Trust score calculation
* [ ] Alerts
* [ ] ML integration
* [ ] Backend API integration

---

# 🚨 Golden Rules

### 1. Never push directly to `main`.

### 2. Always pull before starting work.

```bash
git pull origin main
```

### 3. Create a feature branch.

```bash
git checkout -b feature/name
```

### 4. Make focused commits.

```bash
git commit -m "feat: add ..."
```

### 5. Test before pushing.

```bash
npm run build
npm run lint
```

### 6. Never force-push to `main`.

### 7. Communicate before modifying shared files.

---

# 📄 Project

**Project:** CogniFi
**Title:** Smart Public Wi-Fi Trust & Risk Scoring System
**Institution:** Canara Engineering College
**Department:** Computer Science & Engineering
**Academic Year:** 2025–2026
**Project ID:** CEC/CSE/2025-2026/P-09

````

### One change I'd recommend for your actual repository

Since this README is specifically for **team instructions**, keep it at:

```text
Cogni-Fi/
└── README.md
````

rather than only `frontend/README.md`.

That way, when a member clones the repository, the **Git workflow and setup instructions are immediately visible**, even before entering `frontend`.

Also, make sure your `.gitignore` contains at least:

```gitignore
node_modules/
dist/
.env
.env.local
*.log
```

And **don't commit `node_modules`**. Each member should run `npm install` after pulling the project.
````
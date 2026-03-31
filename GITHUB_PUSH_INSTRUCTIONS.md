# GitHub Authentication Guide

## Push Code to GitHub

Your code is ready to be pushed! Follow one of these methods:

### Method 1: Using Personal Access Token (RECOMMENDED)

1. **Create GitHub Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - Copy the token (you'll only see it once!)

2. **Push to GitHub**
   ```bash
   cd C:\Users\reddym1\Documents\Playwright_QA_Dashboard
   git remote set-url origin https://YOUR_TOKEN@github.com/Madhu123123/QA_Dashboard.git
   git push -u origin main
   ```
   Replace `YOUR_TOKEN` with your actual token

3. **Verify Push**
   - Go to https://github.com/Madhu123123/QA_Dashboard
   - You should see all your files there!

### Method 2: Using SSH (More Secure)

1. **Generate SSH Key** (if you don't have one)
   ```bash
   ssh-keygen -t ed25519 -C "m.madhu1256@gmail.com"
   ```
   - Press Enter for default location
   - Enter passphrase (optional)

2. **Add SSH Key to GitHub**
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/ssh/new
   - Paste the key and save

3. **Update Remote and Push**
   ```bash
   cd C:\Users\reddym1\Documents\Playwright_QA_Dashboard
   git remote set-url origin git@github.com:Madhu123123/QA_Dashboard.git
   git push -u origin main
   ```

### Method 3: Using Git Credentials Manager

Windows automatically prompts for credentials the first time you push. Just run:
```bash
git push -u origin main
```
Then enter your GitHub username and a Personal Access Token when prompted.

## What Gets Pushed

✅ All source code
- Backend (Flask API)
- Frontend (HTML/CSS/JS)
- Test files

✅ Documentation
- README_COMPREHENSIVE.md (full docs)
- QUICKSTART.md (5-minute setup)
- README.md (main overview)

✅ Configuration
- requirements.txt (Python dependencies)
- .gitignore (ignore files)

❌ NOT pushed (due to .gitignore)
- __pycache__/
- *.pyc
- venv/
- .env
- qa_test_runner.db

## After Push

1. **Verify on GitHub**
   ```
   https://github.com/Madhu123123/QA_Dashboard
   ```

2. **Clone for others**
   ```bash
   git clone https://github.com/Madhu123123/QA_Dashboard.git
   ```

3. **Future Pushes**
   ```bash
   git add .
   git commit -m "Your message"
   git push
   ```

---

Need help? Check GitHub's official guides:
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- https://docs.github.com/en/authentication/connecting-to-github-with-ssh

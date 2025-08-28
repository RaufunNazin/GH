# GitHub Deployment Guide for Girls' Hall Search Portal

This guide will help you deploy your Girls' Hall Search Portal to GitHub and make it accessible online using free hosting services.

## Option 1: Deploy to Heroku (Recommended)

### Prerequisites
- GitHub account
- Heroku account (free tier available)
- Git installed on your computer

### Step 1: Prepare for Deployment

1. **Create a Procfile** (for Heroku):
```bash
echo "web: python app.py" > Procfile
```

2. **Update app.py for production**:
```python
# At the end of app.py, replace the last lines with:
if __name__ == '__main__':
    # Load data on startup
    if load_excel_data():
        print("Data loaded successfully!")
    else:
        print("Failed to load data!")
    
    # Use environment variable for port (required for Heroku)
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
```

3. **Create runtime.txt** (specify Python version):
```bash
echo "python-3.9.18" > runtime.txt
```

### Step 2: Initialize Git Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Girls' Hall Search Portal"
```

### Step 3: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and create a new repository
2. Name it `girls-hall-search-portal` (or any name you prefer)
3. Don't initialize with README (since you already have files)
4. Copy the repository URL

### Step 4: Push to GitHub

```bash
# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/girls-hall-search-portal.git

# Push to GitHub
git push -u origin main
```

### Step 5: Deploy to Heroku

1. **Install Heroku CLI**:
   - Download from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**:
```bash
heroku login
```

3. **Create Heroku App**:
```bash
heroku create your-app-name
```

4. **Deploy**:
```bash
git push heroku main
```

5. **Open your app**:
```bash
heroku open
```

## Option 2: Deploy to Railway

### Step 1: Prepare Files

1. **Create railway.json**:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

2. **Update requirements.txt** (add gunicorn for production):
```
flask==2.3.3
pandas==2.1.1
openpyxl==3.1.2
flask-cors==4.0.0
gunicorn==21.2.0
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically deploy your app

## Option 3: Deploy to Render

### Step 1: Prepare Files

1. **Create render.yaml**:
```yaml
services:
  - type: web
    name: girls-hall-search-portal
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
```

### Step 2: Deploy to Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically deploy your app

## Important Notes

### File Structure for Deployment
```
girls-hall-search-portal/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # For Heroku
├── runtime.txt           # Python version for Heroku
├── railway.json          # For Railway
├── render.yaml           # For Render
├── Emails Latest (1).xlsx # Your data file
├── templates/
│   └── index.html        # HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # JavaScript
├── README.md             # Documentation
└── DEPLOYMENT.md         # This file
```

### Environment Variables (if needed)
Some platforms might require environment variables:
- `PORT`: Automatically set by hosting platforms
- `FLASK_ENV`: Set to `production` for production deployments

### Data Persistence
- Contact status is saved in `contact_status.json`
- This file will persist between deployments on most platforms
- For production, consider using a database like PostgreSQL

### Security Considerations
- The app runs in debug mode locally but should use `debug=False` in production
- Consider adding authentication if the data is sensitive
- Use HTTPS in production (most platforms provide this automatically)

## Troubleshooting

### Common Issues

1. **Port Issues**:
   - Make sure your app uses `os.environ.get('PORT', 5001)` for the port
   - Don't hardcode port numbers

2. **Dependencies**:
   - Ensure all dependencies are in `requirements.txt`
   - Use specific versions to avoid conflicts

3. **File Paths**:
   - Use relative paths for files
   - Make sure your Excel file is included in the repository

4. **Memory Issues**:
   - Large Excel files might cause memory issues on free tiers
   - Consider optimizing data loading

### Getting Help

- Check platform-specific documentation
- Look at deployment logs for error messages
- Test locally before deploying
- Use platform-specific debugging tools

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Heroku | Limited hours/month | $7+/month | Full-featured apps |
| Railway | $5 credit/month | $5+/month | Modern deployment |
| Render | 750 hours/month | $7+/month | Static sites & APIs |

Choose the platform that best fits your needs and budget!

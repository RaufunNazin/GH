#!/bin/bash

# Girls' Hall Search Portal - Deployment Setup Script

echo "🚀 Setting up Girls' Hall Search Portal for deployment..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files to git
echo "📝 Adding files to Git..."
git add .

# Make initial commit
echo "💾 Making initial commit..."
git commit -m "Initial commit: Girls' Hall Search Portal with contact tracking"

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Add the GitHub remote: git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Follow the deployment instructions in DEPLOYMENT.md"
echo ""
echo "🌐 Your app is currently running at: http://localhost:5001"
echo "📖 Read DEPLOYMENT.md for detailed deployment instructions"

#!/usr/bin/env python3
"""
GitHub Deployment Script for Eldorado Automation
Deploys all files to a new GitHub repository
"""

import os
import sys

def deploy_to_github():
    """
    Instructions for manual GitHub deployment
    """
    print("=" * 60)
    print("GITHUB DEPLOYMENT GUIDE")
    print("=" * 60)
    print()
    print("Follow these steps to upload to GitHub:")
    print()
    print("1. CREATE REPOSITORY")
    print("   - Go to https://github.com/new")
    print("   - Repository name: eldorado-automation")
    print("   - Description: Automated scraping and uploading for Eldorado.gg")
    print("   - Choose Public or Private")
    print("   - DO NOT initialize with README (we already have one)")
    print()
    print("2. PREPARE FILES")
    print("   - Rename gitignore.txt to .gitignore")
    print("   - Rename env.example.txt to .env.example")
    print()
    print("3. INITIALIZE AND PUSH")
    print("   Run these commands in your project folder:")
    print()
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit: Eldorado automation system'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/YOUR_USERNAME/eldorado-automation.git")
    print("   git push -u origin main")
    print()
    print("4. VERIFY")
    print("   - Visit your repository")
    print("   - Check all files are uploaded")
    print("   - Update README with your specific setup")
    print()
    print("=" * 60)
    print("FILES TO UPLOAD:")
    print("=" * 60)
    files = [
        "scraper.py",
        "uploader.py", 
        "monitor.py",
        "automation.py",
        "setup_triggers.py",
        "README.md",
        "QUICKSTART.md",
        "DEPLOYMENT.md",
        "API.md",
        "TROUBLESHOOTING.md",
        "requirements.txt",
        ".gitignore (rename from gitignore.txt)",
        ".env.example (rename from env.example.txt)"
    ]
    
    for i, file in enumerate(files, 1):
        print(f"{i:2}. {file}")
    
    print()
    print("=" * 60)
    print("ALTERNATIVE: Use GitHub Desktop")
    print("=" * 60)
    print("1. Download GitHub Desktop: https://desktop.github.com/")
    print("2. File > New Repository")
    print("3. Drag and drop your project folder")
    print("4. Commit and push")
    print()

if __name__ == "__main__":
    deploy_to_github()

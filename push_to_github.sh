#!/bin/bash
# Script to push to GitHub repository greek_mapping_p1

# Replace YOUR_USERNAME with your actual GitHub username
GITHUB_USERNAME="YOUR_USERNAME"
REPO_NAME="greek_mapping_p1"

echo "Setting up remote for GitHub..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Check https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"


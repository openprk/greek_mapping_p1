#!/bin/bash
# Push to GitHub - Run this script to push your code

echo "Pushing to https://github.com/openprk/greek_mapping_p1"
echo ""

# Ensure we're on main branch
git branch -M main

# Push to GitHub (will prompt for credentials)
git push -u origin main

echo ""
echo "Done! Your code should now be at:"
echo "https://github.com/openprk/greek_mapping_p1"


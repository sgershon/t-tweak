"""Vercel serverless function entry point for T-Tweak FastAPI application."""

import sys
import os

# Add parent directory to path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel will use this app instance
# The app variable is automatically detected by Vercel's Python runtime
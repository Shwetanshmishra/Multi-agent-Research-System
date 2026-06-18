@echo off
rd /s /q __pycache__ 2>nul
streamlit run app.py
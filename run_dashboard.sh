#!/bin/bash

echo "Starting AICockpit Dashboard..."
echo ""
echo "Make sure you have installed the requirements:"
echo "pip install -r requirements.txt"
echo ""
echo "Opening dashboard in your browser..."

# Make the script executable
chmod +x run_dashboard.sh

# Run the Streamlit app
streamlit run app.py

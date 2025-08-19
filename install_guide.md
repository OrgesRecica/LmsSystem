# Installation Guide for LMS System

If you're getting build errors, try these solutions:

## Step 1: Update pip and build tools
\`\`\`bash
pip install --upgrade pip setuptools wheel
\`\`\`

## Step 2: Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## If you still get errors, try installing individually:
\`\`\`bash
pip install streamlit
pip install fastapi uvicorn
pip install sqlalchemy pydantic
pip install requests pandas plotly
pip install passlib bcrypt
pip install python-multipart python-dateutil python-dotenv
\`\`\`

## Common Solutions:
- **Windows**: Install Microsoft C++ Build Tools
- **macOS**: Run `xcode-select --install`
- **Linux**: Run `sudo apt-get install build-essential python3-dev`

## Run the application:
\`\`\`bash
# Start FastAPI backend
python main.py

# In another terminal, start Streamlit frontend
streamlit run streamlit_app.py

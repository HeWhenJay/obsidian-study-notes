# Install inside the project virtual environment.
pip install -U "autogenstudio"
playwright install

# Start AutoGen Studio, then open http://127.0.0.1:8080.
autogenstudio ui --port 8080 --appdir ./my-app

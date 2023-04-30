# ClubSystem-new
## How to deploy
```
source /path/to/venv/bin/active
pip install -r requirements.txt
gunicorn --workers 2 --bind 0.0.0.0:5000 --daemon server.app:app
```
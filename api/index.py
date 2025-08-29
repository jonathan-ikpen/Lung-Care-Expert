from app import app  # Import your Flask app object

# Vercel looks for a handler called "app"
# In Flask, "app" is already a WSGI app, so we just expose it

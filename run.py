# this contains our __main__ function and super function to be called
from .app import app

if __name__ == '__main__':
  app.run(debug=True)

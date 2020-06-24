# export FLASK_APP=run.p
# flask shel

from .models import User, Posts, Comments, Friendships

__all__ = [
  "User",
  "Posts",
  "Comments",
  "Friendships"
] # to access the table from view.py

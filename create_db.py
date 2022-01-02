import app

# Create tables
appl = app.create_app()
app.models.db.drop_all()
app.models.db.create_all()

# Add a new user
from werkzeug.security import check_password_hash, generate_password_hash
new_user = app.models.User('Elo',generate_password_hash('a'))
app.models.db.session.add(new_user)
app.models.db.session.commit()
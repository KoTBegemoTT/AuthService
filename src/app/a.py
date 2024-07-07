from app.logic import AuthService
from app.models import User

u1 = User(username="u1", password="p1")
u2 = User(username="u1", password="p2")
print(u1 == u2)

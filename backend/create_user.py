from passlib.context import CryptContext
from database.session import SessionLocal
from database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(nickname, email, password):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email '{email}' already exists.")
            return

        hashed_password = get_password_hash(password)
        new_user = User(
            nickname=nickname,
            email=email,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        print(f"Successfully created user: {nickname} ({email})")
    finally:
        db.close()

if __name__ == "__main__":
    
    print("Creating the first user...")
    create_user(
        nickname="Devang",
        email="devang@example.com",
        password="password123"  
    )
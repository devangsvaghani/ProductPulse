# For first-time user (Admin) creation

from passlib.context import CryptContext
from database.session import SessionLocal, engine
from database.models import User, Base
import logging
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(nickname, email, password, is_admin: bool = False):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            logger.info(f"User with email '{email}' already exists. Updating admin status.")
            user.is_admin = is_admin
        else:
            logger.info(f"Creating new user: {email}")
            hashed_password = get_password_hash(password)
            user = User(
                nickname=nickname,
                email=email,
                hashed_password=hashed_password,
                is_admin=is_admin 
            )
            db.add(user)
        
        db.commit()
        logger.info(f"Successfully configured user: {nickname} ({email}) with admin_status={is_admin}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Making sure database tables exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Configuring admin user...")
    create_user(
        nickname="Devang",
        email="devang@example.com",
        password="password123",
        is_admin=True 
    )
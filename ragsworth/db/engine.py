from sqlmodel import SQLModel,Session, create_engine, select
from fastapi import HTTPException
from ragsworth.models.users import User

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.create_tables()

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        with Session(self.engine) as session:
            yield session


    def get_user(self, user_id: int):
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    def get_all_users(self):
        with Session(self.engine) as session:
            users = session.exec(select(User)).all()
            return users

    def add_user(self, user: User):
        with Session(self.engine) as session:
            # Check if user with same username already exists
            existing_username = session.exec(
                select(User).where(User.username == user.username)
            ).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Username already registered")

            # Check if user with same email already exists
            if user.email:
                existing_email = session.exec(
                    select(User).where(User.email == user.email)
                ).first()
                if existing_email:
                    raise HTTPException(status_code=400, detail="Email already registered")

            # Add the user if no duplicates found
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update_user(self, user: User):
        with Session(self.engine) as session:
            db_user = session.get(User, user.id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
            db_user.username = user.username
            db_user.email = user.email
            db_user.full_name = user.full_name
            db_user.disabled = user.disabled
            session.commit()
            session.refresh(db_user)
            return db_user

    def delete_user(self, user_id: int):
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}

    def get_user_by_username(self, username: str):
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            return user

    def get_user_by_email(self, email: str):
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            return user

    def get_user_by_full_name(self, full_name: str):
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.full_name == full_name)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    def close(self):
        self.engine.dispose()

class DatabaseManager:
    def __init__(self, db_url: str):
        self.db = Database(db_url)
        self.session = self.db.get_session()
    def close(self):
        self.db.close()


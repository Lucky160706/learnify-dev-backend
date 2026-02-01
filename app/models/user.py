
from sqlalchemy import Column, String, Text
from app.database import Base

class User(Base):
    __tablename__ = "user" # Matches Drizzle table name

    id = Column(Text, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=False)
    image = Column(Text)

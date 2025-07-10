from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from ..database import Base

class AuthProvider(Base):
    __tablename__ = "auth_providers"

    id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    provider = Column(String(50))
    provider_id = Column(String(255))

    __table_args__ = (UniqueConstraint('provider', 'provider_id', name='_provider_uc'),)
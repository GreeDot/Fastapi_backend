from sqlalchemy import Column, Integer, String, DATETIME, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import RoleEnum, StatusEnum, GradeEnum, LogTypeEnum
from .base import Base

class Member(Base):
    __tablename__ = 'member'

    id = Column('member_id', Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    grade = Column(Enum(GradeEnum), nullable=False)
    register_at = Column(DATETIME, nullable=False)

    gree = relationship("Gree", back_populates="member")
    logs = relationship("Logs", back_populates="member")

class Gree(Base):
    __tablename__ = 'gree'

    id = Column('gree_id', Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('member.member_id'), nullable=False)
    gree_name = Column(String(255), nullable=False)
    root_path = Column(String(255), nullable=False)
    prompt_character = Column(String(255))  # 대체될 수 있습니다
    prompt_age = Column(Integer)
    prompt_mbti = Column(String(255))  # 대체될 수 있습니다
    register_at = Column(DATETIME, nullable=False)

    member = relationship("Member", back_populates="gree")
    logs = relationship("Logs", back_populates="gree")

class Logs(Base):
    __tablename__ = 'logs'

    id = Column('log_id', Integer, primary_key=True, autoincrement=True)
    gree_id = Column(Integer, ForeignKey('gree.gree_id'), nullable=False)
    member_id = Column(Integer, ForeignKey('member.member_id'), nullable=False)
    log_type = Column(Enum(LogTypeEnum), nullable=False)
    talk = Column(String(255))
    register_at = Column(DATETIME, nullable=False)

    member = relationship("Member", back_populates="logs")
    gree = relationship("Gree", back_populates="logs")

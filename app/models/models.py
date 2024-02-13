# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.enums import RoleEnum, StatusEnum, GradeEnum, LogTypeEnum, FileTypeEnum
from app.models.base import Base
from datetime import datetime


class Member(Base):
    __tablename__ = 'member'

    id = Column('member_id', Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    grade = Column(Enum(GradeEnum), nullable=False)
    refresh_token = Column(String(255))
    register_at = Column(DateTime, nullable=False, default=datetime.now())
    gree = relationship("Gree", back_populates="member")


class Gree(Base):
    __tablename__ = 'gree'

    id = Column('gree_id', Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('member.member_id'), nullable=False)
    gree_name = Column(String(255))
    raw_img = Column(String(255), nullable=False)
    prompt_character = Column(String(255))
    prompt_age = Column(Integer)
    prompt_mbti = Column(String(255))
    status = Column(Enum(StatusEnum))
    isFavorite = Column(Boolean, default=False)
    register_at = Column(DateTime, nullable=False, default=datetime.now())

    member = relationship("Member", back_populates="gree")
    log = relationship("Log", back_populates="gree")
    greefile = relationship("GreeFile", back_populates="gree")
    emotion_report = relationship("EmotionReport", back_populates="gree")


class GreeFile(Base):
    __tablename__ = 'greefile'

    id = Column('greefile_id', Integer, primary_key=True, autoincrement=True)
    gree_id = Column(Integer, ForeignKey('gree.gree_id'), nullable=False)
    file_type = Column(Enum(FileTypeEnum), nullable=False)
    file_name = Column(String(255), nullable=False)
    real_name = Column(String(255), nullable=False)
    register_at = Column(DateTime, nullable=False, default=datetime.now())

    gree = relationship("Gree", back_populates="greefile")


class Log(Base):
    __tablename__ = 'log'

    id = Column('log_id', Integer, primary_key=True, autoincrement=True)
    gree_id = Column(Integer, ForeignKey('gree.gree_id'), nullable=False)
    log_type = Column(Enum(LogTypeEnum), nullable=False)
    talk = Column(String(255))
    content = Column(String(255))
    register_at = Column(DateTime, nullable=False, default=datetime.now())

    gree = relationship("Gree", back_populates="log")


class EmotionReport(Base):
    __tablename__ = 'emotion_report'

    id = Column('emotion_report_id', Integer, primary_key=True, autoincrement=True)
    gree_id = Column(Integer, ForeignKey('gree.gree_id'), nullable=False)
    content = Column(String(255))
    emotion_type = Column(Enum(LogTypeEnum), nullable=False)
    talk = Column(String(255))
    register_at = Column(DateTime, nullable=False, default=datetime.now())

    gree = relationship("Gree", back_populates="emotion_report")

import datetime
from config import *

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Text, Boolean, ForeignKey, Float, func, desc, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


DATABASE_NAME = 'trainEGE_db.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    t_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    name = Column(String)
    surname = Column(String)
    year = Column(Integer)
    admin = Column(Boolean, default=False)
    verify = Column(Boolean, default=False)

    exams = relationship('Exam', back_populates='user')


class Topic(Base):
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    desc = Column(String)
    index = Column(Integer)

    subtopics = relationship('Subtopic', back_populates='topic')


class Subtopic(Base):
    __tablename__ = 'subtopic'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topic.id'))
    title = Column(String)
    desc = Column(String)
    index = Column(Integer)

    topic = relationship('Topic', back_populates='subtopics')
    questions = relationship('Question', back_populates='subtopic')


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopic.id'))
    link = Column(String)
    answer = Column(String)
    index = Column(Integer)
    showing = Column(Boolean, default=True)

    subtopic = relationship('Subtopic', back_populates='questions')
    tasks = relationship('Task', back_populates='question')


class Exam(Base):
    __tablename__ = 'exam'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.t_id'))
    type = Column(String)
    start = Column(DateTime)
    stop = Column(DateTime)

    user = relationship('User', back_populates='exams')
    tasks = relationship('Task', back_populates='exam')


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exam.id'))
    question_id = Column(Integer, ForeignKey('question.id'))
    answer_text = Column(String)
    answer_point = Column(Integer)
    start = Column(DateTime)
    stop = Column(DateTime)

    exam = relationship('Exam', back_populates='tasks')
    question = relationship('Question', back_populates='tasks')




Base.metadata.create_all(engine)

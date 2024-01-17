from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


# DB part
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Определение моделей данных
class Keywords(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, nullable=False)

class RefKeywords(Base):
    __tablename__ = 'ref_keywords'
    symptom = Column(Integer, ForeignKey('symptoms.id'), primary_key=True)
    keyword = Column(Integer, ForeignKey('keywords.id'), primary_key=True)

class Symptoms(Base):
    __tablename__ = 'symptoms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    page = Column(Integer)
    yes = Column(Integer, ForeignKey('symptoms.id'))
    no = Column(Integer, ForeignKey('symptoms.id'))
    keywords = relationship('Keywords', secondary='ref_keywords')

class Users(Base):
    __tablename__ = 'users'
    name = Column(String(30), primary_key=True)
    password = Column(String(30), nullable=False)

# Read functions
def read_keywords():
    return session.query(Keywords).all()

def read_ref_keywords():
    return session.query(RefKeywords).all()

def read_symptoms():
    return session.query(Symptoms).all()

def read_users():
    return session.query(Users).all()

def show_keywords():
    # Чтение ключевых слов
    all_keywords = read_keywords()
    print("All Keywords:")
    for keyword in all_keywords:
        print(f"ID: {keyword.id}, Word: {keyword.word}")

def show_ref_keywords():
    all_ref_keywords = read_ref_keywords()
    print("All Ref Keywords:")
    for ref_keyword in all_ref_keywords:
        print(f"Symptom ID: {ref_keyword.symptom}, Keyword ID: {ref_keyword.keyword}")

def show_symptoms():
    all_symptoms = read_symptoms()
    print("All Symptoms:")
    for symptom in all_symptoms:
        print(f"ID: {symptom.id}, Name: {symptom.name}, Description: {symptom.description}")

def show_users():
    all_users = read_users()
    print("All Users:")
    for user in all_users:
        print(f"Name: {user.name}, Password: {user.password}")

def insert_keyword(word):
    new_keyword = Keywords(word=word)
    session.add(new_keyword)
    session.commit()

def insert_ref_keyword(symptom_id, keyword_id):
    new_ref_keyword = RefKeywords(symptom=symptom_id, keyword=keyword_id)
    session.add(new_ref_keyword)
    session.commit()

def insert_symptom(name, description, page, yes, no):
    new_symptom = Symptoms(name=name, description=description, page=page, yes=yes, no=no)
    session.add(new_symptom)
    session.commit()

def insert_user(name, password):
    new_user = Users(name=name, password=password)
    session.add(new_user)
    session.commit()

# Определение функций обновления данных
def update_keyword(keyword_id, new_word):
    keyword = session.query(Keywords).filter_by(id=keyword_id).first()
    if keyword:
        keyword.word = new_word
        session.commit()
        return True
    return False

def update_ref_keyword(symptom_id, keyword_id, new_symptom_id, new_keyword_id):
    ref_keyword = session.query(RefKeywords).filter_by(symptom=symptom_id, keyword=keyword_id).first()
    if ref_keyword:
        ref_keyword.symptom = new_symptom_id
        ref_keyword.keyword = new_keyword_id
        session.commit()
        return True
    return False

def update_symptom(symptom_id, new_name, new_description, new_page, new_yes, new_no):
    symptom = session.query(Symptoms).filter_by(id=symptom_id).first()
    if symptom:
        symptom.name = new_name
        symptom.description = new_description
        symptom.page = new_page
        symptom.yes = new_yes
        symptom.no = new_no
        session.commit()
        return True
    return False

def update_user_password(username, new_password):
    user = session.query(Users).filter_by(name=username).first()
    if user:
        user.password = new_password
        session.commit()
        return True
    return False

def delete_keyword(keyword_id):
    keyword = session.query(Keywords).filter_by(id=keyword_id).first()
    if keyword:
        session.delete(keyword)
        session.commit()
        return True
    return False

def delete_ref_keyword(symptom_id, keyword_id):
    ref_keyword = session.query(RefKeywords).filter_by(symptom=symptom_id, keyword=keyword_id).first()
    if ref_keyword:
        session.delete(ref_keyword)
        session.commit()
        return True
    return False

def delete_symptom(symptom_id):
    symptom = session.query(Symptoms).filter_by(id=symptom_id).first()
    if symptom:
        session.delete(symptom)
        session.commit()
        return True
    return False

def delete_user(username):
    user = session.query(Users).filter_by(name=username).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

# Закрываем соединение
def close_session():
    session.close()
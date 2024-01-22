import json

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


# DB part

f = open('./data/connection/connection.json')
data = None
if f:
    data = json.load(f)
if data:
    # engine = create_engine(f"postgresql://postgres:zukosuper2003@localhost:5432/HomeDoctor")
    engine = create_engine(
        f"postgresql://{data['username']}:{data['password']}@{data['host']}:{data['port']}/{data['dbname']}")

Base = declarative_base()


def open_session():
    Session = sessionmaker(bind=engine)
    global session
    session = Session()

# Определение моделей данных


class Keywords(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, nullable=False)

    def tuple(self):
        res = []

        if (self.id):
            res.append(str(self.id))
        else:
            res.append('-')

        if (self.word):
            res.append(self.word)
        else:
            res.append('-')

        return tuple(res)


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
    yes = Column(Integer, ForeignKey('symptoms.id'), nullable=True)
    yes_obj = relationship('Symptoms', remote_side=[
                           id], primaryjoin='Symptoms.id==Symptoms.yes')
    no = Column(Integer, ForeignKey('symptoms.id'), nullable=True)
    no_obj = relationship('Symptoms', remote_side=[
                          id], primaryjoin='Symptoms.id==Symptoms.no')

    keywords = relationship('Keywords', secondary='ref_keywords')

    # Oh God I'm so sorry for this code
    # Should use __iter__ here, but too lazy I'M SORRY

    def tuple(self):
        res = []

        if (self.id):
            res.append(str(self.id))
        else:
            res.append('-')

        if (self.name):
            res.append(self.name)
        else:
            res.append('-')

        if (self.yes_obj):
            res.append(self.yes_obj.name)
        else:
            res.append('-')

        if (self.no_obj):
            res.append(self.no_obj.name)
        else:
            res.append('-')

        if (self.page):
            res.append(self.page)
        else:
            res.append('-')

        return tuple(res)


def keywords_string(keywords):
    res = ''
    if keywords:
        for keyword in keywords:
            res += f'{keyword.word}, '
        return res
    return ('')


class Users(Base):
    __tablename__ = 'users'
    name = Column(String(30), primary_key=True)
    password = Column(String(30), nullable=False)

    def tuple(self):
        res = []

        if (self.name):
            res.append(self.name)
        else:
            res.append('-')

        if (self.password):
            res.append(self.password)
        else:
            res.append('-')

        return tuple(res)

# Read functions


def read_keywords():
    return session.query(Keywords).all()


def get_keyword(id):
    return session.query(Keywords).get(id)


def get_keyword_by_word(word):
    all_keywords = read_keywords()
    for keyword in all_keywords:
        if keyword.word == word:
            return keyword


def read_ref_keywords():
    return session.query(RefKeywords).all()


def read_symptoms():
    return session.query(Symptoms).all()


def get_symptom(id):
    return session.query(Symptoms).get(id)


def get_symptom_by_name(name):
    all_symptoms = read_symptoms()
    for symptom in all_symptoms:
        if symptom.name == name:
            return symptom


def read_users():
    return session.query(Users).all()


def get_user(username):
    return session.query(Users).filter_by(name=username).first()


def show_keywords():
    # Чтение ключевых слов
    all_keywords = read_keywords()
    print("All Keywords:")
    for keyword in all_keywords:
        print(f"ID: {keyword.id}, Word: {keyword.word}")


def keywords_list():
    res = []
    all_keywords = read_keywords()
    for keyword in all_keywords:
        res.append(keyword.word)
    return res


def show_ref_keywords():
    all_ref_keywords = read_ref_keywords()
    print("All Ref Keywords:")
    for ref_keyword in all_ref_keywords:
        print(f"Symptom ID: {ref_keyword.symptom}, Keyword ID: {
              ref_keyword.keyword}")


def show_symptoms():
    all_symptoms = read_symptoms()
    print("All Symptoms:")
    for symptom in all_symptoms:
        print(f"ID: {symptom.id}, Name: {
              symptom.name}, Description: {symptom.description}")


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


def insert_symptom(name, description, page, yes=None, no=None):
    new_symptom = Symptoms(
        name=name, description=description, page=page, yes=yes, no=no)
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
    ref_keyword = session.query(RefKeywords).filter_by(
        symptom=symptom_id, keyword=keyword_id).first()
    if ref_keyword:
        ref_keyword.symptom = new_symptom_id
        ref_keyword.keyword = new_keyword_id
        session.commit()
        return True
    return False


def update_symptom(symptom_id, new_name, new_description, new_page, new_yes=None, new_no=None):
    symptom = session.query(Symptoms).get(symptom_id)
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
    keyword = session.query(Keywords).get(keyword_id)
    if keyword:
        for r in read_ref_keywords():
            if r.keyword == keyword.id:
                delete_ref_keyword(r.symptom, r.keyword)
        session.delete(keyword)
        session.commit()
        return True
    return False


def delete_ref_keyword(symptom_id, keyword_id):
    ref_keyword = session.query(RefKeywords).filter_by(
        symptom=symptom_id, keyword=keyword_id).first()
    if ref_keyword:
        session.delete(ref_keyword)
        session.commit()
        return True
    return False


def delete_symptom(symptom_id):
    symptom = session.query(Symptoms).get(symptom_id)
    if symptom:
        for s in read_symptoms():
            if s.yes == symptom.id:
                s.yes = None
            if s.no == symptom.id:
                s.no = None
        for r in read_ref_keywords():
            if r.symptom == symptom.id:
                delete_ref_keyword(r.symptom, r.keyword)
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

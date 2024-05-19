from contextlib import contextmanager

import json

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func

from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# DB part
f = open("./connection/connection.json")
data = None
if f:
    data = json.load(f)
if data:
    engine = create_engine(
        f"postgresql://{data['username']}:{data['password']}@{data['host']}:{data['port']}/{data['dbname']}"
    )
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = None


@contextmanager
def session_manager():
    global session
    try:
        session = Session()
        yield
    except:
        raise
    finally:
        session.close()
        session = None


@contextmanager
def transaction_manager():
    global session
    if not session:
        with session_manager():
            try:
                yield session
                session.commit()
            except:
                session.rollback()
                raise
    else:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise


def d_transaction(func):
    def wrapper(*args, **kwargs):
        with transaction_manager():
            return func(*args, **kwargs)

    return wrapper


@d_transaction
def d_insert(func):
    def wrapper(*args, **kwargs):
        return session.add(func(*args, **kwargs))

    return wrapper


# Models
class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, nullable=False)

    def tuple(self):
        return (str(x) if x is not None else "-" for x in (self.id, self.word))


class SymptomKeywordMapping(Base):
    __tablename__ = "symptom_keyword_mappings"
    symptom_id = Column(Integer, ForeignKey("symptoms.id"), primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True)


class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    page = Column(Integer)

    yes_id = Column(Integer, ForeignKey("symptoms.id"), nullable=True)
    yes = relationship(
        "Symptom", remote_side=[id], primaryjoin="Symptom.id==Symptom.yes_id"
    )
    no_id = Column(Integer, ForeignKey("symptoms.id"), nullable=True)
    no = relationship(
        "Symptom", remote_side=[id], primaryjoin="Symptom.id==Symptom.no_id"
    )

    keywords = relationship("Keyword", secondary="symptom_keyword_mappings")

    def tuple(self):
        return (
            str(self.id) if self.id else "-",
            self.name or "-",
            self.yes.name if self.yes else "-",
            self.no.name if self.no else "-",
            self.page or "-",
        )


def keywords_string(keywords):
    return ", ".join(keyword.word for keyword in keywords) if keywords else ""


class User(Base):
    __tablename__ = "users"
    name = Column(String(30), primary_key=True)
    password = Column(String(30), nullable=False)

    def tuple(self):
        return (self.name or "-", self.password or "-")


# Select
def select_symptoms(
    id=None,
    name=None,
    description=None,
    page=None,
    yes_id=None,
    no_id=None,
    limit=None,
    order="id",
):
    return (
        session.query(Symptom)
        .filter(
            (Symptom.id.cast(String) == str(id) if id else True),
            (func.lower(Symptom.name).contains(name.lower()) if name else True),
            (
                func.lower(Symptom.description).contains(description)
                if description
                else True
            ),
            (Symptom.yes_id.cast(String) == str(yes_id) if yes_id else True),
            (Symptom.no_id.cast(String) == str(no_id) if no_id else True),
            (Symptom.page.cast(String) == str(page) if page else True),
        )
        .order_by(order)
        .limit(limit)
        .all()
    )


def select_symptom(
    id=None,
    name=None,
    description=None,
    page=None,
    yes_id=None,
    no_id=None,
):
    return (
        session.query(Symptom)
        .filter(
            (Symptom.id.cast(String) == str(id) if id else True),
            (Symptom.name == name if name else True),
            (Symptom.description == description if description else True),
            (Symptom.page.cast(String) == str(page) if page else True),
            (Symptom.yes_id.cast(String) == str(yes_id) if yes_id else True),
            (Symptom.no_id.cast(String) == str(no_id) if no_id else True),
        )
        .first()
    )


def select_keywords(id=None, word=None, limit=None, order="word"):
    return (
        session.query(Keyword)
        .filter(
            (Keyword.id.cast(String) == str(id) if id else True),
            (func.lower(Keyword.word).contains(word) if word else True),
        )
        .order_by(order)
        .limit(limit)
        .all()
    )


def select_keyword(id=None, word=None):
    return (
        session.query(Keyword)
        .filter(
            (Keyword.id.cast(String) == str(id) if id else True),
            (Keyword.word == word if word else True),
        )
        .first()
    )


def select_symptom_keyword_mappings(
    symptom_id=None, keyword_id=None, limit=None, order="symptom_id"
):
    return (
        session.query(SymptomKeywordMapping)
        .filter(
            (SymptomKeywordMapping.symptom_id == symptom_id if symptom_id else True),
            (SymptomKeywordMapping.keyword_id == keyword_id if keyword_id else True),
        )
        .order_by(order)
        .limit(limit)
        .all()
    )


def select_symptom_keyword_mapping(symptom_id=None, keyword_id=None):
    return (
        session.query(SymptomKeywordMapping)
        .filter(
            (SymptomKeywordMapping.symptom_id == symptom_id if symptom_id else True),
            (SymptomKeywordMapping.keyword_id == keyword_id if keyword_id else True),
        )
        .first()
    )


def select_users(name=None, password=None, limit=None, order="name"):
    return (
        session.query(User)
        .where(
            (func.lower(User.name).contains(name) if name else True),
            (func.lower(User.password).contains(password) if password else True),
        )
        .order_by(order)
        .limit(limit)
        .all()
    )


def select_user(name=None, password=None):
    return (
        session.query(User)
        .filter(
            (name == User.name if name else True),
            (password == User.password if password else True),
        )
        .first()
    )


def keywords_list():
    res = []
    all_keywords = select_keywords()
    for keyword in all_keywords:
        res.append(keyword.word)
    return res


# Transactions
#
# Insert
@d_insert
def insert_keyword(word):
    return Keyword(word=word)


@d_insert
def insert_symptom_keyword_mapping(symptom_id, keyword_id):
    return SymptomKeywordMapping(symptom_id=symptom_id, keyword_id=keyword_id)


@d_insert
def insert_symptom(name, description, page, yes=None, no=None):
    return Symptom(name=name, description=description, page=page, yes=yes, no=no)


@d_insert
def insert_user(name, password):
    return User(name=name, password=password)


# Update
@d_transaction
def update_symptom(
    id=None,
    name=None,
    new_name=None,
    new_description=None,
    new_page=None,
    new_yes_id=None,
    new_no_id=None,
):
    if not (id, name):
        return
    symptom = select_symptom(id=id) if id else select_symptom(name=name)
    symptom.name = new_name
    symptom.description = new_description
    symptom.page = new_page
    symptom.yes_id = new_yes_id
    symptom.no_id = new_no_id


@d_transaction
def update_keyword(id, new_word):
    keyword = select_keyword(id=id)
    keyword.word = new_word


@d_transaction
def update_symptom_keyword_mapping(
    symptom_id, keyword_id, new_symptom_id, new_keyword_id
):
    symptom_keyword_mapping = select_symptom_keyword_mapping(
        symptom_id=symptom_id, keyword_id=keyword_id
    )
    symptom_keyword_mapping.symptom_id = new_symptom_id
    symptom_keyword_mapping.keyword_id = new_keyword_id


@d_transaction
def update_user(name, new_password):
    user = select_user(name=name)
    user.password = new_password


# Delete


@d_transaction
def delete_keyword(keyword_id):
    delete_symptom_keyword_mapping(keyword_id=keyword_id)
    session.delete(select_keyword(id=keyword_id))


@d_transaction
def delete_symptom_keyword_mapping(symptom_id=None, keyword_id=None):
    session.delete(
        select_symptom_keyword_mapping(symptom_id=symptom_id, keyword_id=keyword_id)
    )


@d_transaction
def delete_symptom(id):
    for linked_symptom in session.query(Symptom).filter(
        id == Symptom.yes.id or id == Symptom.no.id
    ):
        linked_symptom.yes = None if not linked_symptom.yes else linked_symptom.yes
        linked_symptom.no = None if not linked_symptom.no else linked_symptom.no

    session.delete(select_symptom_keyword_mappings(symptom_id=id))

    session.delete(select_symptom(id=id))


@d_transaction
def delete_user(name):
    session.delete(select_user(name=name))


if __name__ == "__main__":
    with session_manager():
        update_keyword(id=9, new_word="teasdsfst")

from contextlib import contextmanager

import json

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select

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

    keywords = relationship("Keyword", secondary="symptom_keyword_mapping")

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
            (Symptom.id.cast(String).like(str(id)) if id else True)
            and (Symptom.name.like(name) if name else True)
            and (Symptom.description.like(description) if description else True)
            and (Symptom.yes_id.cast(String) == str(yes_id) if yes_id else True)
            and (Symptom.no_id.cast(String) == no_id if no_id else True)
            and (Symptom.page.cast(String) == page if page else True)
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
            (Symptom.id.cast(String) == str(id) if id else True)
            and (Symptom.name == name if name else True)
            and (Symptom.description == description if description else True)
            and (Symptom.page.cast(String) == str(page) if page else True)
            and (Symptom.yes_id.cast(String) == str(yes_id) if yes_id else True)
            and (Symptom.no_id.cast(String) == str(no_id) if no_id else True)
        )
        .first()
    )


def select_keywords(id=None, word=None, limit=None, order="word"):
    return (
        session.query(Keyword)
        .filter(
            (Keyword.id.cast(String) == str(id) if id else True),
            (Keyword.word.like(word) if word else True),
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
            (User.name.like(name) if name else True),
            (User.password.like(password) if password else True),
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
    return SymptomKeywordMapping(symptom=symptom_id, keyword=keyword_id)


@d_insert
def insert_symptom(name, description, page, yes=None, no=None):
    return Symptom(name=name, description=description, page=page, yes=yes, no=no)


@d_insert
def insert_user(name, password):
    return User(name=name, password=password)


# Update
@d_transaction
def update_symptom(
    symptom_id, new_name, new_description, new_page, new_yes=None, new_no=None
):
    with select_symptom(id=symptom_id) as symptom:
        symptom.name = new_name
        symptom.description = new_description
        symptom.page = new_page
        symptom.yes = new_yes
        symptom.no = new_no


@d_transaction
def update_keyword(keyword_id, new_word):
    with select_keyword(id=keyword_id) as keyword:
        keyword.word = new_word


@d_transaction
def update_symptom_keyword_mapping(
    symptom_id, keyword_id, new_symptom_id, new_keyword_id
):
    with select_symptom_keyword_mapping(
        symptom_id=symptom_id, keyword_id=keyword_id
    ) as symptom_keyword_mapping:
        symptom_keyword_mapping.symptom_id = new_symptom_id
        symptom_keyword_mapping.keyword_id = new_keyword_id


@d_transaction
def update_user(name, new_password):
    with select_user(name=name) as user:
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
        id in [Symptom.yes.id, Symptom.no.id]
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
        print(select_user(name="User2"))

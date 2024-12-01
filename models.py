from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import BYTEA  # Исправленный импорт для Bytea
from sqlalchemy.dialects.postgresql import JSONB
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Инициализация базы данных
DATABASE_URI = 'postgresql://postgres:2612@localhost/sport'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Пример для Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'

    id_client = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))

    participations = db.relationship("Participation", back_populates="client")
    secret_data = db.relationship("SecretData", back_populates="client")

    def __repr__(self):
        return f"<Client(id_client={self.id_client}, username='{self.username}')>"

from flask_login import UserMixin

class Admin(db.Model, UserMixin):
    tablename = 'admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def repr(self):
        return f"<Admin(id={self.id}, username='{self.username}')>"

    # Flask-Login требует наличие этих методов
    def get_id(self):
        return str(self.id)  # Возвращаем уникальный идентификатор как строку

    @property
    def is_active(self):
        # Возвращает True, если пользователь активен, иначе False
        return True  # В данном примере считаем всех пользователей активными

    @property
    def is_authenticated(self):
        # Возвращает True, если пользователь аутентифицирован
        return True

    @property
    def is_anonymous(self):
        # Возвращает False, если пользователь не анонимный
        return False

class Coach(db.Model):
    __tablename__ = 'coach'

    id_coach = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))

    occupancy = db.relationship("Occupancy", back_populates="coach")
    trainings = db.relationship("Training", back_populates="coach")

    def __repr__(self):
        return f"<Coach(id_coach={self.id_coach}, username='{self.username}')>"

class MainLog(db.Model):
    __tablename__ = 'main_log'

    log_item_id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.Text)
    operation_date = db.Column(db.TIMESTAMP)
    user_operator = db.Column(db.Text)
    table_name = db.Column(db.Text)
    changed_data = db.Column(db.JSON)

class Occupancy(db.Model):
    __tablename__ = 'occupancy'

    id_occupancy = db.Column(db.Integer, primary_key=True)
    id_coach = db.Column(db.Integer, db.ForeignKey('coach.id_coach'))
    date = db.Column(db.TIMESTAMP)
    status = db.Column(db.String(20))
    id_training = db.Column(db.Integer, db.ForeignKey('trainings.id_training'))

    coach = db.relationship("Coach", back_populates="occupancy")
    training = db.relationship("Training", back_populates="occupancy")

class Participation(db.Model):
    __tablename__ = 'participations'

    id_participation = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
    id_training = db.Column(db.Integer, db.ForeignKey('trainings.id_training'))
    status = db.Column(db.String(20))
    registration_date = db.Column(db.TIMESTAMP)

    client = db.relationship("Client", back_populates="participations")
    training = db.relationship("Training", back_populates="participations")
    payments = db.relationship("Payment", back_populates="participation")

class Payment(db.Model):
    __tablename__ = 'payments'

    id_payment = db.Column(db.Integer, primary_key=True)
    id_participation = db.Column(db.Integer, db.ForeignKey('participations.id_participation'))
    date = db.Column(db.TIMESTAMP)
    amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20))

    participation = db.relationship("Participation", back_populates="payments")

class SecretData(db.Model):
    __tablename__ = 'secret_data'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.Text)
    encrypted_phone_number = db.Column(db.LargeBinary)  # BYTEA аналог
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id_client'))

    client = db.relationship("Client", back_populates="secret_data")

class Training(db.Model):
    __tablename__ = 'trainings'

    id_training = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    start_date = db.Column(db.TIMESTAMP)
    end_date = db.Column(db.TIMESTAMP)
    location = db.Column(db.String(50))
    id_coach = db.Column(db.Integer, db.ForeignKey('coach.id_coach'))
    training_type = db.Column(db.String(50))
    training_cost = db.Column(db.Numeric(10, 2))

    coach = db.relationship("Coach", back_populates="trainings")
    occupancy = db.relationship("Occupancy", back_populates="training")
    participations = db.relationship("Participation", back_populates="training")



# Database setup
DATABASE_URI = 'postgresql://postgres:2612@localhost/sport'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
Base.metadata.create_all(engine)
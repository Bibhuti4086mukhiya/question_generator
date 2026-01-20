import json
import os
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL environment variable if available (Heroku), else local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data.db')

# Fix for Heroku's postgres:// URL (SQLAlchemy requires postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

class AppData(Base):
    __tablename__ = 'app_data'
    id = Column(Integer, primary_key=True)
    content = Column(Text, default='{}')

class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._migrate_from_json()

    def _migrate_from_json(self):
        """Migrate existing JSON file to DB if DB is empty."""
        session = self.Session()
        try:
            # Check if DB is empty
            if session.query(AppData).count() == 0 and os.path.exists('data.json'):
                with open('data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                record = AppData(content=json.dumps(data, ensure_ascii=False))
                session.add(record)
                session.commit()
                print("Migrated data.json to database.")
        except Exception as e:
            print(f"Migration warning: {e}")
        finally:
            session.close()

    def load(self):
        """Loads data from the database."""
        session = self.Session()
        try:
            record = session.query(AppData).first()
            if record and record.content:
                return json.loads(record.content)
            return {}
        except Exception as e:
            print(f"Error loading database: {e}")
            return {}
        finally:
            session.close()

    def save(self, data):
        """Saves data to the database."""
        session = self.Session()
        try:
            record = session.query(AppData).first()
            if not record:
                record = AppData(content=json.dumps(data, ensure_ascii=False))
                session.add(record)
            else:
                record.content = json.dumps(data, ensure_ascii=False)
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            session.rollback()
            return False
        finally:
            session.close()

# Singleton instance to be used by the app
db = Database()

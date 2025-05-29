from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import DATABASE_URL


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def see_table(table_name):
    users = text(f"SELECT * FROM {table_name}")
    return users



def update_prices(title, price):
    query = text('update Books set price = :price where title = :title')
    param = {
        "price": title,
        "title": price
    }
    return query, param



def insert(*args):
    sql = text(
        "INSERT INTO WishLists (title, Author, username) VALUES (:title,:author, :username)"
    )
    paramtr = {"title": args[0],
               "author": args[1],
               "username": args[2]
               }
    return sql, paramtr






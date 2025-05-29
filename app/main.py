from sys import exception

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, fields
from sqlalchemy import text
from sqlalchemy.orm import Session
from Database import SessionLocal, insert, see_table, update_prices
from Practice6 import *
from fastapi import Depends

app = FastAPI()



@app.get("/")               #Complete
def greet():
    return {"message": "Welcome to books collection api"}


class Signup(BaseModel):
    username: str = fields.Field(...,min_length=5, max_length=20)
    password: str = fields.Field(...,min_length=6)
    name: str = fields.Field(...,min_length=3)
    age: int = fields.Field(..., gt=5)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





class Books(BaseModel):
    title : str = fields.Field(...,min_length=3)
    author : str = fields.Field(...,min_length=3)
    year : int = fields.Field(...,gt=1500,le = 2025)
    price : int = fields.Field(...,gt=0)


class Wishlist(BaseModel):
    title : str = fields.Field(...,min_length=3)
    author : str = fields.Field(...,min_length=3)



class Review(BaseModel):
    title: str = fields.Field(...,min_length=3)
    review: str = fields.Field(...,min_length=3)
    rating: float = fields.Field(...,gt=0)


@app.post("/books/signup")                            #complete
def signup(signup_c: Signup,
           db: Session = Depends(get_db)):
    users = db.execute(text("SELECT * FROM users")).mappings().all()
    for i in users:
        if i['username'] == signup_c.username:
            raise HTTPException(status_code=400, detail="Username already exists")
    sql = text(
        "INSERT INTO users (username, hashed_password, name, age) VALUES (:username, :hashed_password, :name, :age)"
    )
    parameter = {"username": signup_c.username,
               "hashed_password": hashing_p(signup_c.password),
               "name": signup_c.name,
               "age": signup_c.age}
    db.execute(sql, parameter)

    db.commit()
    return {"message": "User created successfully"}



@app.post("/login", include_in_schema=False)                      #Complete
def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    users = db.execute(text("SELECT * FROM users")).mappings().all()
    for i in users:
        if i['username'] == form_data.username and check_pwd(i["hashed_password"], form_data.password):
            token = create_token({"user": form_data.username, "role": i["role"]})
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")



@app.get("/users")                                        #Complete
def get_users(db: Session = Depends(get_db),
              admin = Depends(verify_admin)):
    if admin:
        users = db.execute(text("SELECT username, name, age, role FROM users")).mappings().all()
        return users
    else:
        raise HTTPException(status_code=401, detail="You are not authorized to see this page")



@app.post("/books")                                           #Complete
def create_book(book: Books,
                db: Session = Depends(get_db),
                admin = Depends(verify_admin)):
    if admin:
        books_s = db.execute(text("SELECT * FROM Books")).mappings().all()
        for bk in books_s:
            if bk['title'] == book.title and bk['author'] == book.author:
                raise HTTPException(status_code=400, detail="Book already exists")
        sql = text(
            "INSERT INTO Books (title, author, year, price) VALUES (:title, :author, :year, :price)"
        )
        parameter = {"title": book.title,
                   "author": book.author,
                   "year": book.year,
                   "price": book.price
                   }
        db.execute(sql, parameter)
        db.commit()
        return{f"{book.title} is Added in the collection"}
    else:
        raise HTTPException(status_code=401, detail="You are not authorized to see this page")


@app.post("/reset")                              #Complete
def reset_books(token = Depends(oauth2_scheme),
                db: Session = Depends(get_db)):
    if verify_admin(token):
        db.execute(text("delete from Books"))
        db.commit()
        return {"status":"The Books Collection has been Reset"}
    else:
        raise HTTPException(status_code=401, detail="Access Denied")



@app.get("/books/view")                                    # Complete
def Show_books(db: Session = Depends(get_db)):
    books = db.execute(text("SELECT title, author, year, price FROM Books")).mappings().all()
    if not books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books


@app.get("/books/by_author")                                #Complete
def Show_books_by_author(author:str,
                         db: Session = Depends(get_db)):
    query = (text("SELECT title, year, price FROM Books WHERE author = :author"))
    books = db.execute(query, {"author": author}).mappings().all()
    if not books:
        return {"Detail":f"No books found by author {author}"}
    else:
        return books




@app.post("/reviews")                                   #Complete
def add_review(review: Review,
               token = Depends(oauth2_scheme),
               db:Session = Depends(get_db)):
    query = (text("SELECT * FROM Book_Reviews WHERE username = :username"))
    param = {"username": verify_token(token)}
    try:
        reviews = db.execute(query, param).mappings().all()
    except:
        raise HTTPException(status_code=404, detail="Review not found")
    for j in reviews:
        username = verify_token(token)
        if j['username'] == username:
            if j['title'] == review.title:
                raise HTTPException(status_code=400, detail="Review already exists")
            else:
                pass
    books_s = db.execute(text("SELECT * FROM Books")).mappings().all()
    for i in books_s:
        if review.title.strip().lower() == i['title'].strip().lower():
            sql = text(
                "INSERT INTO Book_Reviews (title, username, review, rating) VALUES (:title, :username, :review, :rating)"
            )
            parameter = {"title": review.title,
                       "username": verify_token(token),
                       "review": review.review,
                       "rating": review.rating
                       }
            db.execute(sql, parameter)
            db.commit()
            return {"status" : f"The Review is Added by {verify_token(token)}"}
    raise HTTPException(status_code=404, detail="Book not Available")


@app.get("/reviews/view")                                   #Complete
def show_review(token = Depends(oauth2_scheme),
                db:Session = Depends(get_db)):
    query = (text("SELECT title, review, rating FROM Book_Reviews WHERE username = :username"))
    param = {"username": verify_token(token)}
    reviews = db.execute(query, param).mappings().all()
    if reviews:
        return reviews
    else:
        raise HTTPException(status_code=404, detail="Review directory empty")


@app.post("/wishlist")
def add_wishlist(wishlist: Wishlist,
                 db: Session = Depends(get_db),
                 token: Depends = Depends(oauth2_scheme)):
    query = (text("SELECT * FROM WishLists WHERE username = :username"))
    param = {"username": verify_token(token)}
    try:
        wish = db.execute(query, param).mappings().all()
    except:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    for Feedback in wish:
        if wishlist.title.strip().lower() == Feedback['title'].strip().lower():
            if Feedback['username'] == verify_token(token) and wishlist.author.strip().lower() == Feedback['author'].strip().lower():
                raise HTTPException(status_code=401, detail="Wishlist already exists")
            else:
                try:
                    db.execute(insert(wishlist.title, wishlist.author, verify_token(token)))
                    db.commit()
                    return {"status": "The Book is Added to your wishlist"}
                except exception:
                    return {"status": "An error occurred"}
    else:
        try:
            query, params = insert(wishlist.title, wishlist.author, verify_token(token))
            db.execute(query, params)
            db.commit()
            return {"status": "The Book is Added to your wishlist"}
        except exception() as e:
            print(str(e))
            return {"status": "An error occurred"}





@app.get("/wishlist/show")                                  # Complete
def show_wishlist(token = Depends(oauth2_scheme),
                  db: Session = Depends(get_db),
                  is_admin = Depends(verify_token)):

    wishlists = (
        db.execute(text(f"SELECT title, author FROM WishLists")).mappings().all())
    result = []
    if not is_admin:
        for user in wishlists:
            if user['username'] == verify_token(token):
                result.append(user)
        if len(result) == 0:
            return {"status": "No Books Added In Wishlists"}
        else:
            return result
    else:
        return wishlists


@app.put("/books/update/price")                                 #Complete
def update_price(title,
                 author,
                 price: int,
                 db: Session = Depends(get_db),
                 is_admin = Depends(verify_token)):
    if is_admin:
        table = db.execute(see_table('Books')).mappings().all()
        db.commit()
        for j in table:
            if title.strip().lower() == j['title'].strip().lower() and author.strip().lower() == j['author'].strip().lower():
                query, params = update_prices(price, title)
                db.execute(query, params)
                db.commit()
                return {"status" : f"Price is Updated Successfully for {j['title']} by {price}"}
        raise HTTPException(status_code=404, detail="Book not Found")
    else:
        raise HTTPException(status_code=404, detail="Access Denied...")


@app.delete("/books/delete")                            #Complete
def delete_book(title, author,
                db: Session = Depends(get_db),
                is_admin = Depends(verify_admin)):
    if is_admin:
        try:
            query = text("delete from Books where title = :title and author = :author")
            db.execute(query, {"title": title, "author": author})
            db.commit()
            return { 'status' :"Book Deleted Successfully"}
        except:
            raise HTTPException(status_code=404, detail="Book not Found")
    else:
        raise HTTPException(status_code=401, detail="Access Denied....")


@app.get("/books/wishlist/by")                            #Complete
def show_wishlist_admin(is_admin = Depends(verify_admin),
                        db:Session = Depends(get_db)):
    if is_admin:
        query = (text("SELECT * FROM WishLists"))
        table = db.execute(query).mappings().all()
        return table
    else:
        raise HTTPException(status_code=401, detail="Access Denied....")





@app.get('/books/update/rating')
def update_ratings(title,
                   author,
                   rating,
                   db: Session = Depends(get_db),
                   is_admin = Depends(verify_admin)):
    if is_admin:
        table = db.execute(see_table('Books')).mappings().all()
        db.commit()
        for j in table:
            if title.strip().lower() == j['title'].strip().lower() and author.strip().lower() == j['author'].strip().lower():
                query = text("update Books set rating = :rating where title = :title")
                db.execute(query, {
                    'rating': rating,
                    'title': title,
                })
                db.commit()
                return {"status": f"Rating is Updated Successfully for {j['title']} by {rating}"}
        raise HTTPException(status_code=404, detail="Book not Found")
    else:
        raise HTTPException(status_code=401, detail="Access Denied....")

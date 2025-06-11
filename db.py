from fastapi import FastAPI,Body,HTTPException,status
from typing import List,Optional
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from fastapi.responses import JSONResponse
import os


app=FastAPI()

class User(BaseModel):
    user_name:str
    user_phoneno: int
    user_address: str

class Users(BaseModel):
    user_id:Optional[int]
    user_name:str
    user_phoneno: int
    user_address: str

class Product(BaseModel):
    product_id: Optional[int]  
    product_name: str
    price: float
    stock: int

class Products(BaseModel):
    product_name: str
    price: float
    stock: int

class Order(BaseModel):
    user_id: int
    product_id: int
    total_amount: float
    order_status: Optional[str] = "Pending"
    delivery_address: Optional[str] = None
    order_date: Optional[datetime] = None

class ProductToDelete(BaseModel):
    user_id: int
    product_id: int

class Cart(BaseModel):
    cart_id: Optional[int]  
    user_id: int
    product_id: int
    quantity: int


def get_db_connections():
    return psycopg2.connect(
        dbname="ecommerce_bx3f",
        user="muzifa",
        password="QZ1rEEY6pRiaYdtGNAsiNoW5lqmp0oY2",
        host="dpg-d14hvru3jp1c73begj3g-a.singapore-postgres.render.com",
        port="5432"  
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("db:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ecommerce API"}

@app.post("/create-user")
def create_user(users: List[User]):
    conn = get_db_connections()
    cursor = conn.cursor()
    for user in users:
        cursor.execute(
            "INSERT INTO users (user_name, user_phoneno, user_address) VALUES (%s, %s, %s)",
            (user.user_name, user.user_phoneno, user.user_address)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success", "message": "Users added"}


@app.put("/update-users")
def update_users(users: List[Users]):
    conn = get_db_connections()
    cursor = conn.cursor()
    updated = []

    for user in users:
        cursor.execute(
            """
            UPDATE users
            SET user_name = %s, user_phoneno = %s, user_address = %s
            WHERE user_id = %s
            RETURNING user_id, user_name, user_phoneno, user_address
            """,
            (user.user_name, user.user_phoneno, user.user_address, user.user_id)
        )
        result = cursor.fetchone()
        if result:
            updated.append({
                "user_id": result[0],
                "user_name": result[1],
                "user_phoneno": result[2],
                "user_address": result[3]
            })

    conn.commit()
    cursor.close()
    conn.close()

    if not updated:
        return {
            "status":"error",
            "status_code": 400,
            "updated_users": updated
        }

    return {
        "status": "success",
        "updated_users": updated
    }


@app.get("/fetch-user")
def fetch_user():
    conn=get_db_connections()
    cursor=conn.cursor()
    cursor.execute("Select * from users")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    result = [dict(zip(col_names, row)) for row in rows]
    return {"users": result}


@app.delete("/delete-user/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connections()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        return {
            "status": "error",
            "status_code": 400,
            "message": f"User with ID {user_id} not exist"
        }

    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "status": "success",
        "status_code": 200,
        "message": f"User with ID {user_id} deleted successfully"
    }

@app.post("/create-product")
def create_product(products:List[Products]):
    conn=get_db_connections()
    cursor=conn.cursor()
    for product in products:
        cursor.execute(
        "Insert into products(product_name, price, stock) VALUES (%s,%s,%s)",
        (product.product_name,product.price,product.stock)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "status":"sucess",
        "status_code": 200,
        "message":"the given product is updated"
    }

@app.get("/fetch-product")
def fetch():
    conn=get_db_connections()
    cursor=conn.cursor()
    cursor.execute("Select * from products")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    result = [dict(zip(col_names, row)) for row in rows]
    return {"products": result}


@app.put("/update-product")
def prod_update(products: List[Product]):
    for product in products:
        if not product.product_id:
            return {
                "status": "error",
                "status_code": 400,
                "message": "Provide product_id for all products to update"
            }

    updated = []
    conn = get_db_connections()
    cursor = conn.cursor()

    for product in products:
        cursor.execute(
            "UPDATE products SET product_name=%s, price=%s, stock=%s WHERE product_id=%s RETURNING product_id, product_name, price, stock",
            (product.product_name, product.price, product.stock, product.product_id)
        )
        result = cursor.fetchone()
        if result:
            updated.append({
                "product_id": result[0],
                "product_name": result[1],
                "price": result[2],
                "stock": result[3]
            })

    conn.commit()
    cursor.close()
    conn.close()

    if not updated:
        return {
            "status": "error",
            "status_code": 400,
            "updated_users": updated
        }

    return {
        "status": "success",
        "status_code": 200,
        "updated_users": updated
    }


@app.delete("/delete-product/{product_id}")
def del_product(product_id:int):
    conn=get_db_connections()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return{
            "status":"error",
            "status_code":400,
            "message":f"The product with product id {product_id} not available "
        }
    cursor.execute("delete from products where product_id=%s",(product_id,))
    conn.commit()
    cursor.close()
    cursor.close()
    return {
        "status":"sucess",
        "status_code":200,
        "message":f"Deleted product id {product_id} from product table "
    }

@app.get("/fetch-order")
def fetch_order():
    conn=get_db_connections()
    cursor=conn.cursor()
    cursor.execute("Select * from orders")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    result = [dict(zip(col_names, row)) for row in rows]
    return {"orders": result}
   

@app.post("/place-order")
def place_order(orders: List[Order]):
    conn = get_db_connections()
    cursor = conn.cursor()

    order_ids = []

    for order in orders:
        order_date = order.order_date or datetime.now()

        delivery_address = order.delivery_address
        if not delivery_address:
            cursor.execute(
                "SELECT user_address FROM users WHERE user_id = %s",
                (order.user_id,)
            )
            result = cursor.fetchone()
            delivery_address = result[0] if result else "Unknown"

        cursor.execute(
            """
            INSERT INTO orders (user_id, product_id, order_date, total_amount, order_status, delivery_address)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING order_id
            """,
            (
                order.user_id,
                order.product_id,
                order_date,
                order.total_amount,
                order.order_status,
                delivery_address
            )
        )
        order_id = cursor.fetchone()[0]
        order_ids.append(order_id)

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "status": "success",
        "status_code": 200,
        "order_ids": order_ids,
        "message": f"Orders placed successfully."
    }

@app.delete("/cancel-order")
def cancel_order(products: List[ProductToDelete]):
    conn = get_db_connections()
    cursor = conn.cursor()

    deleted_products = []
    not_found_products = []

    for p in products:
        cursor.execute(
            "SELECT * FROM cart WHERE product_id = %s AND user_id = %s",
            (p.product_id, p.user_id)
        )
        if cursor.fetchone() is None:
            not_found_products.append(p.product_id)
        else:
            cursor.execute(
                "DELETE FROM cart WHERE product_id = %s AND user_id = %s",
                (p.product_id, p.user_id)
            )
            deleted_products.append(p.product_id)

    conn.commit()
    cursor.close()
    conn.close()

    return {
            "status": "success",
            "status_code": 200,
            "message": f"Deleted products from user's cart.",
        }




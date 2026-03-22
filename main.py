from fastapi import FastAPI, Query, HTTPException  # FastAPI imports
from pydantic import BaseModel, Field  # Pydantic validation
from typing import Optional  # Optional typing

app = FastAPI()  # create FastAPI app

# -------------------- DATA --------------------

items = [  # grocery items dataset
    {"id":1,"name":"Tomato","price":30,"unit":"kg","category":"Vegetable","in_stock":True},
    {"id":2,"name":"Potato","price":25,"unit":"kg","category":"Vegetable","in_stock":True},
    {"id":3,"name":"Milk","price":60,"unit":"litre","category":"Dairy","in_stock":True},
    {"id":4,"name":"Apple","price":120,"unit":"kg","category":"Fruit","in_stock":False},
    {"id":5,"name":"Rice","price":50,"unit":"kg","category":"Grain","in_stock":True},
    {"id":6,"name":"Eggs","price":70,"unit":"dozen","category":"Dairy","in_stock":True}
]

orders = []  # orders list
order_counter = 1  # order id counter

cart = []  # cart list

# -------------------- HELPERS --------------------

def find_item(item_id):  # helper to find item by id
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def calculate_order_total(price, quantity, delivery_slot, bulk=False):  # helper to calculate bill
    original = price * quantity
    discount = 0

    if bulk and quantity >= 10:
        discount = original * 0.08

    subtotal = original - discount

    delivery_charge = 0
    if delivery_slot.lower() == "morning":
        delivery_charge = 40
    elif delivery_slot.lower() == "evening":
        delivery_charge = 60

    total = subtotal + delivery_charge

    return original, discount, total


def filter_items_logic(category, max_price, unit, in_stock):  # helper for filtering items
    result = items

    if category is not None:
        result = [i for i in result if i["category"].lower()==category.lower()]

    if max_price is not None:
        result = [i for i in result if i["price"] <= max_price]

    if unit is not None:
        result = [i for i in result if i["unit"].lower()==unit.lower()]

    if in_stock is not None:
        result = [i for i in result if i["in_stock"] == in_stock]

    return result

# -------------------- MODELS --------------------

class OrderRequest(BaseModel):  # order request model
    customer_name: str = Field(min_length=2)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)
    delivery_address: str = Field(min_length=10)
    delivery_slot: str = "Morning"
    bulk_order: bool = False


class CheckoutRequest(BaseModel):  # checkout model
    customer_name: str = Field(min_length=2)
    delivery_address: str = Field(min_length=10)
    delivery_slot: str


class NewItem(BaseModel):  # new item model
    name: str = Field(min_length=2)
    price: int = Field(gt=0)
    unit: str = Field(min_length=2)
    category: str = Field(min_length=2)
    in_stock: bool = True

# -------------------- DAY 1 GET --------------------

@app.get("/")  # home route
def home():
    return {"message":"Welcome to FreshMart Grocery"}

@app.get("/items")  # get all items
def get_items():
    in_stock_count = len([i for i in items if i["in_stock"]])
    return {"items":items,"total":len(items),"in_stock_count":in_stock_count}

@app.get("/items/summary")  # items summary route
def summary():
    categories={}
    in_stock=0
    out_stock=0

    for i in items:
        categories[i["category"]] = categories.get(i["category"],0)+1
        if i["in_stock"]:
            in_stock+=1
        else:
            out_stock+=1

    return {
        "total":len(items),
        "in_stock":in_stock,
        "out_of_stock":out_stock,
        "categories":categories
    }

@app.get("/orders")  # get all orders
def get_orders():
    return {"orders":orders,"total":len(orders)}

# -------------------- DAY 3 FILTER --------------------

@app.get("/items/filter")  # filter items api
def filter_items(category:str=None,max_price:int=None,unit:str=None,in_stock:bool=None):
    result=filter_items_logic(category,max_price,unit,in_stock)
    return {"results":result,"count":len(result)}

@app.get("/items/search")  # search items api
def search_items(keyword:str):
    result=[i for i in items if keyword.lower() in i["name"].lower()
            or keyword.lower() in i["category"].lower()]
    return {"results":result,"total_found":len(result)}

@app.get("/items/sort")  # sort items api
def sort_items(sort_by:str="price",order:str="asc"):
    if sort_by not in ["price","name","category"]:
        raise HTTPException(status_code=400,detail="Invalid sort field")

    reverse = True if order=="desc" else False
    sorted_items = sorted(items,key=lambda x:x[sort_by],reverse=reverse)

    return {"sorted":sorted_items}

@app.get("/items/page")  # pagination api
def paginate(page:int=1,limit:int=4):
    start=(page-1)*limit
    end=start+limit
    total_pages = (len(items)+limit-1)//limit

    return {
        "page":page,
        "total_pages":total_pages,
        "data":items[start:end]
    }

@app.get("/items/browse")  # combined browse api
def browse(keyword:str=None,category:str=None,in_stock:bool=None,sort_by:str="price",order:str="asc",page:int=1,limit:int=3):

    result=items

    if keyword:
        result=[i for i in result if keyword.lower() in i["name"].lower()]

    if category:
        result=[i for i in result if i["category"].lower()==category.lower()]

    if in_stock is not None:
        result=[i for i in result if i["in_stock"]==in_stock]

    reverse=True if order=="desc" else False
    result=sorted(result,key=lambda x:x[sort_by],reverse=reverse)

    start=(page-1)*limit
    end=start+limit

    return {"total":len(result),"page":page,"results":result[start:end]}

@app.get("/items/{item_id}")  # get item by id
def get_item(item_id:int):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found")
    return item

# -------------------- DAY 4 CRUD --------------------

@app.post("/items",status_code=201)  # create item api
def create_item(new_item:NewItem):
    for i in items:
        if i["name"].lower()==new_item.name.lower():
            raise HTTPException(status_code=400,detail="Duplicate item")

    new_id = items[-1]["id"] + 1
    item_dict = new_item.dict()
    item_dict["id"]=new_id

    items.append(item_dict)
    return item_dict

@app.put("/items/{item_id}")  # update item api
def update_item(item_id:int,price:int=None,in_stock:bool=None):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found")

    if price is not None:
        item["price"]=price
    if in_stock is not None:
        item["in_stock"]=in_stock

    return item

@app.delete("/items/{item_id}")  # delete item api
def delete_item(item_id:int):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found")

    for o in orders:
        if o["item_id"]==item_id:
            raise HTTPException(status_code=400,detail="Active orders exist")

    items.remove(item)
    return {"message":"Item deleted"}

# -------------------- DAY 2/3 POST ORDER --------------------

@app.post("/orders")  # create order api
def create_order(req:OrderRequest):
    global order_counter

    item=find_item(req.item_id)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found")

    if not item["in_stock"]:
        raise HTTPException(status_code=400,detail="Item out of stock")

    original,discount,total = calculate_order_total(item["price"],req.quantity,req.delivery_slot,req.bulk_order)

    order={"order_id":order_counter,"customer":req.customer_name,"item_id":req.item_id,"item":item["name"],
           "quantity":req.quantity,"unit":item["unit"],"slot":req.delivery_slot,
           "original":original,"discount":discount,"total_cost":total,"status":"confirmed"}

    orders.append(order)
    order_counter+=1

    return order

# -------------------- DAY 5 CART --------------------

@app.post("/cart/add")  # add to cart api
def add_cart(item_id:int,quantity:int=1):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404,detail="Item not found")

    if not item["in_stock"]:
        raise HTTPException(status_code=400,detail="Out of stock")

    for c in cart:
        if c["item_id"]==item_id:
            c["quantity"]+=quantity
            return {"message":"Quantity merged","cart":cart}

    cart.append({"item_id":item_id,"name":item["name"],"price":item["price"],"quantity":quantity})
    return {"message":"Added","cart":cart}

@app.get("/cart")  # view cart api
def view_cart():
    total=0
    for c in cart:
        c["subtotal"]=c["price"]*c["quantity"]
        total+=c["subtotal"]

    return {"cart":cart,"grand_total":total}

@app.delete("/cart/{item_id}")  # remove cart item api
def remove_cart(item_id:int):
    for c in cart:
        if c["item_id"]==item_id:
            cart.remove(c)
            return {"message":"Removed"}
    raise HTTPException(status_code=404,detail="Not in cart")

@app.post("/cart/checkout",status_code=201)  # checkout api
def checkout(req:CheckoutRequest):
    global order_counter

    if not cart:
        raise HTTPException(status_code=400,detail="Cart empty")

    placed=[]
    grand=0

    for c in cart:
        original,discount,total = calculate_order_total(c["price"],c["quantity"],req.delivery_slot)

        order={"order_id":order_counter,"customer":req.customer_name,"item_id":c["item_id"],
               "item":c["name"],"quantity":c["quantity"],"total_cost":total,"status":"confirmed"}

        orders.append(order)
        placed.append(order)

        grand+=total
        order_counter+=1

    cart.clear()

    return {"orders":placed,"grand_total":grand}

# -------------------- DAY 6 ADVANCED --------------------

@app.get("/orders/search")  # search orders api
def search_orders(customer_name:str):
    result=[o for o in orders if customer_name.lower() in o["customer"].lower()]
    return {"results":result}

@app.get("/orders/sort")  # sort orders api
def sort_orders():
    return {"sorted":sorted(orders,key=lambda x:x["total_cost"])}

@app.get("/orders/page")  # orders pagination api
def order_page(page:int=1,limit:int=3):
    start=(page-1)*limit
    end=start+limit
    return {"data":orders[start:end]}

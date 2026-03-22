 fastapi_grocery_delivery
 🛒 Grocery Delivery Backend (FastAPI)

 📌 Project Overview

Grocery Delivery is a FastAPI backend system developed as part of an internship project.
The application simulates a real-world grocery delivery backend where users can browse grocery items, add them to cart, place orders, and manage delivery workflows.

This project demonstrates core backend development concepts including API design, data validation, CRUD operations, helper functions, multi-step workflows, search, sorting, pagination, and combined browsing logic.



🚀 Features Implemented

✅ Basic GET APIs

* Home route
* List all grocery items
* Get item by ID
* Items summary endpoint
* View all orders

 ✅ POST APIs with Validation

* Order creation with Pydantic validation
* Bulk order discount logic
* Delivery charge calculation

 ✅ Helper Functions

* `find_item()` to locate items
* `calculate_order_total()` for billing logic
* `filter_items_logic()` for flexible filtering

 ✅ CRUD Operations

* Create new grocery item
* Update item price or stock
* Delete item with active order protection

 ✅ Multi-Step Workflow (Cart → Checkout → Orders)

* Add item to cart
* Merge cart quantities
* Remove item from cart
* Checkout cart and create multiple orders
* Clear cart after successful checkout

 ✅ Advanced APIs

* Keyword search (name & category)
* Sorting (price, name, category)
* Pagination for items and orders
* Combined browse endpoint (search + filter + sort + paginate)

---

 🧰 Tech Stack

* FastAPI
* Python
* Pydantic
* Uvicorn

---

 📂 Project Structure

```
fastapi_grocery_delivery/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
```

---

 ▶️ How to Run the Project

 Step 1: Install Dependencies

```
pip install -r requirements.txt
```

 Step 2: Run FastAPI Server

```
uvicorn main:app --reload
```

 Step 3: Open Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

 🧪 Testing

All APIs were tested using Swagger UI.
Screenshots for each task (Q1–Q20) are available inside the `screenshots` folder.

---

 🎯 Learning Outcomes

* Designed structured REST APIs
* Implemented real backend workflows
* Applied validation and error handling
* Built modular helper logic
* Implemented search, sorting and pagination
* Developed combined data browsing pipelines


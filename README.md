# Online Shopping Platform

> [!IMPORTANT]
> The project is still work in progress

A half-baked mock online shopping platform that simulates the process of Shopee, one of the largest online shopping platform in South East Asia, without the transportation layer of the process.

## Features

- [x] User Service: user authentication, user authorization and user access control with JWT token
- [x] Product Service: Only users that are identified as vendors are allowed to create a product and no duplicate product could be created
- [x] Cart Service: Users that are identified as customers could perform CRUD operation on a cart and checkout whenever they want
- [x] Order Service: When the cart is checked out, the items within a cart will be converted into an invoice
- [ ] Product Search Service: This service is currently based on regex. In the future, it will be updated into using elastic search

## How to use

1. Login as a vendor -> Create some products
2. Login as a customer -> Search for the products -> Add some products into the cart -> Checkout the cart -> View the Order

## Local Development

- Python: 3.12+
- PostgreSQL: 16.1

1. Install Dependencies

```shell
pip install -r requirements.txt
```

2. Install PostgreSQL and Pgadmin and create a database `db` in Pgadmin

3. Copy `.env.example` to `.env`

4. Run `openssl rand hex -32` and store the data generated into `REFRESH_TOKEN_SECRET_KEY` in `.env`

5. Within your terminal run 

```shell
uvicorn main:app --reload
```

6. Navigate to http://127.0.0.1:8000/docs to see all the services that is provided

## Future Improvement

1. Create elastic search
2. Rate Limiting
3. Pagination as a middleware
4. Logger
5. Additional services for vendor to manage the orders
6. Create a Ticketing system so that users could share the problems of the product with the vendor
7. Additional services for admin
8. Use HTTPS for security consideration
9. Casbin RBAC Access Control Model

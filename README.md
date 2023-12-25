# Online Shopping Platform

> [!IMPORTANT]
> The project is still work in progress

A half-baked mock online shopping platform that simulates the process of Shopee, one of the largest online shopping platform in South East Asia, without the transportation layer and order management system of the process.

## Features

- [x] User Service: user authentication, user authorization and user access control with JWT token.
- [x] Product Service: Only users that are identified as vendors are allowed to create a product and no duplicate product could be created. Customers could add desired product into their shopping cart.
- [x] Cart Service: Users that are identified as customers could perform CRUD operation on a cart and checkout whenever they want.
- [x] Order Service: When the cart is checked out, the items within a cart will be converted a sales order.
- [x] Search Service: Allow users to search for specified product through query parameter or filter products into a specified category

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
5. Create a Ticketing system so that users could share the problems of the product with the vendor
6. Additional services for admin
7. Use HTTPS for security consideration
8. Casbin RBAC Access Control Model
9. Once checkout, send an invoice email for the order confirmation
10. Email verification flow and send invoice email once payment is made

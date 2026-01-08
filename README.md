## Django + Stripe Checkout test task

### Features
- Item model: name, description, price, currency
- GET /buy/<id>/ returns Stripe Session id (or PaymentIntent client_secret, depending on STRIPE_PAYMENT_MODE)
- GET /item/<id>/ renders HTML page with Stripe Checkout redirect
- Order model: multiple items with quantities
- Discount and Tax models for Order (shown in Stripe Checkout)
- Django Admin enabled
- Docker + Postgres
- Env vars only

### Local run (Docker)
1) Copy env
   - cp .env.example .env
   - Fill Stripe keys

2) Run
   - docker compose up -d --build

3) Migrate and create admin
   - docker compose exec web python manage.py migrate
   - docker compose exec web python manage.py createsuperuser

4) Open
   - Admin: http://localhost:8000/admin/
   - Create Items
   - Open Item page: http://localhost:8000/item/1/
   - Create Order and OrderItems in admin: http://localhost:8000/order/1/

### Payment modes
- STRIPE_PAYMENT_MODE=checkout_session
- STRIPE_PAYMENT_MODE=payment_intent

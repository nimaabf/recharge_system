# Recharge System

B2B recharge sales system with credit management and transaction tracking.

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
```

## Run Server

```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

## API Endpoints

Base URL: `http://localhost:8000/api/`

- `POST /api/sellers/<seller_id>/credit-request/` - Create credit request
  - Body: `{"amount": "100000.00"}`
- `POST /api/admin/credit-requests/<request_id>/approve/` - Approve credit request
  - Body: `{}`
- `POST /api/sellers/<seller_id>/charge/` - Recharge phone number
  - Body: `{"phone_number_id": 1, "amount": "5000.00"}`
- `GET /api/sellers/<seller_id>/balance/` - Get seller balance
- `GET /api/sellers/<seller_id>/transactions/` - Get transaction history
- `GET /api/sellers/<seller_id>/verify-accounting/` - Verify accounting integrity

## Setup Test Data

Before testing API, create test data using Django admin at `http://localhost:8000/admin/` or Django shell:

```bash
python manage.py shell
>>> from app.models import Seller, PhoneNumber
>>> Seller.objects.create(name="Test Seller", balance=100000)
>>> PhoneNumber.objects.create(phone_number="09123456789", is_active=True)
```

## Run Tests

```bash
python manage.py test tests
```

Test files:

- `tests/test_recharge_system.py` - Main test suite (2 sellers, 10 credit increases, 1000 recharge sales)
- `tests/test_parallel_load.py` - Parallel load tests

Test suite includes 2 sellers, 10 credit increases, 1000 recharge sales, and parallel load tests.

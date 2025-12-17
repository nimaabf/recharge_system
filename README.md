# Recharge System - B2B Credit Management

A Django-based B2B recharge sales system with credit management, transaction tracking, and accounting integrity verification.

## Features

- **Credit Management**: Sellers can request credit increases, admin approves them
- **Recharge Sales**: Sellers can recharge phone numbers, deducting from their balance
- **Transaction Logging**: All credit changes are recorded for accounting
- **Accounting Integrity**: System verifies that sum of all transactions matches current balance
- **Race Condition Protection**: Uses `select_for_update()` and `transaction.atomic()` for thread safety
- **Parallel Load Support**: Tested under heavy concurrent load

## Project Structure

```
recharge_system/
├── app/
│   ├── models.py          # Database models (Seller, CreditRequest, CreditTransaction, etc.)
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   └── services/
│       ├── credit_service.py   # Credit request management
│       └── charge_service.py   # Recharge operations
├── tests/
│   ├── test_recharge_system.py  # Main test suite
│   └── test_parallel_load.py    # Parallel load tests
└── recharge_system/
    └── settings.py        # Django settings
```

## API Endpoints

- `POST /api/sellers/<seller_id>/credit-request/` - Create credit request
- `POST /api/admin/credit-requests/<request_id>/approve/` - Approve credit request
- `POST /api/sellers/<seller_id>/charge/` - Recharge phone number
- `GET /api/sellers/<seller_id>/balance/` - Get seller balance
- `GET /api/sellers/<seller_id>/transactions/` - Get transaction history
- `GET /api/sellers/<seller_id>/verify-accounting/` - Verify accounting integrity

## Key Requirements Implementation

### ✅ Credit Increase Only Charges Once

- Uses `select_for_update()` to lock credit request
- Checks status before approval
- Prevents double approval

### ✅ Transaction Logging

- All credit increases recorded in `CreditTransaction` with positive amount
- All recharge sales recorded with negative amount
- Each transaction includes `balance_after` for verification

### ✅ Balance Never Goes Negative

- Database constraint: `CheckConstraint(balance__gte=0)`
- Service-level check before deduction
- Raises `InsufficientBalanceError` if insufficient funds

### ✅ Race Condition Protection

- `select_for_update()` locks rows during updates
- `transaction.atomic()` ensures atomic operations
- Prevents concurrent balance updates

### ✅ Accounting Integrity

- `verify_accounting_integrity()` sums all transactions
- Compares with current balance
- Tolerance of 0.01 for rounding

## Running Tests

```bash
# Run all tests
python manage.py test tests

# Run specific test
python manage.py test tests.test_recharge_system.RechargeSystemTestCase

# Run parallel load tests
python manage.py test tests.test_parallel_load
```

## API Endpoints and Requests

### Base URL

```
http://localhost:8000/api/
```

### 1. Create Credit Request

**POST** `/api/sellers/<seller_id>/credit-request/`

**Request Body:**

```json
{
    "amount": "100000.00"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/sellers/1/credit-request/ \
  -H "Content-Type: application/json" \
  -d '{"amount": "100000.00"}'
```

**Response (201 Created):**

```json
{
    "id": 1,
    "seller_id": 1,
    "amount": "100000.00",
    "status": "pending",
    "created_at": "2025-12-17T10:00:00Z",
    "approved_at": null
}
```

### 2. Approve Credit Request

**POST** `/api/admin/credit-requests/<request_id>/approve/`

**Request Body:** (empty)

**Example:**

```bash
curl -X POST http://localhost:8000/api/admin/credit-requests/1/approve/ \
  -H "Content-Type: application/json"
```

**Response (200 OK):**

```json
{
    "id": 1,
    "seller_id": 1,
    "amount": "100000.00",
    "status": "approved",
    "created_at": "2025-12-17T10:00:00Z",
    "approved_at": "2025-12-17T10:05:00Z"
}
```

### 3. Charge Phone (Recharge)

**POST** `/api/sellers/<seller_id>/charge/`

**Request Body:**

```json
{
    "phone_number_id": 1,
    "amount": "5000.00"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/sellers/1/charge/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number_id": 1, "amount": "5000.00"}'
```

**Response (201 Created):**

```json
{
    "id": 1,
    "seller_id": 1,
    "phone_number_id": 1,
    "amount": "5000.00",
    "status": "completed",
    "created_at": "2025-12-17T10:10:00Z"
}
```

### 4. Get Seller Balance

**GET** `/api/sellers/<seller_id>/balance/`

**Example:**

```bash
curl -X GET http://localhost:8000/api/sellers/1/balance/
```

**Response (200 OK):**

```json
{
    "seller_id": 1,
    "current_balance": "95000.00",
    "seller_name": "Seller 1"
}
```

### 5. Get Transaction History

**GET** `/api/sellers/<seller_id>/transactions/`

**Example:**

```bash
curl -X GET http://localhost:8000/api/sellers/1/transactions/
```

**Response (200 OK):**

```json
{
    "seller_id": 1,
    "current_balance": "95000.00",
    "transactions": [
        {
            "id": 1,
            "seller_id": 1,
            "amount": "100000.00",
            "transaction_type": "credit_increase",
            "reference_id": 1,
            "balance_after": "100000.00",
            "created_at": "2025-12-17T10:05:00Z"
        },
        {
            "id": 2,
            "seller_id": 1,
            "amount": "-5000.00",
            "transaction_type": "recharge_sale",
            "reference_id": 1,
            "balance_after": "95000.00",
            "created_at": "2025-12-17T10:10:00Z"
        }
    ],
    "total_count": 2
}
```

### 6. Verify Accounting Integrity

**GET** `/api/sellers/<seller_id>/verify-accounting/`

**Example:**

```bash
curl -X GET http://localhost:8000/api/sellers/1/verify-accounting/
```

**Response (200 OK):**

```json
{
    "seller_id": 1,
    "current_balance": "95000.00",
    "calculated_balance": "95000.00",
    "is_match": true,
    "transaction_count": 2
}
```

### Error Responses

**404 Not Found:**

```json
{
    "detail": "Seller with ID 999 not found"
}
```

**400 Bad Request:**

```json
{
    "amount": ["Ensure this value is greater than or equal to 0.01."]
}
```

**400 Validation Error:**

```json
{
    "detail": "Insufficient balance. Current: 1000.00, Required: 5000.00"
}
```

## Test Coverage

The test suite includes:

- **2 sellers** with different credit scenarios
- **10 credit increases** per seller
- **1000 recharge sales** (500 per seller)
- **Accounting integrity verification** after all operations
- **Parallel load testing** with threads
- **Race condition testing** for concurrent approvals

## Multi-Thread vs Multi-Process

### Why Threads for This Project?

1. **I/O-Bound Operations**: Database operations are I/O-bound, not CPU-bound
2. **Shared Memory**: Threads share memory, making data access faster
3. **Django Support**: Django's ORM and transactions work well with threads
4. **Lower Overhead**: Threads have less overhead than processes

### When to Use Processes?

- CPU-intensive calculations
- When you need true parallelism (bypassing GIL)
- When isolation is critical

For this project, **threads are the right choice** because:

- All operations are database I/O
- Django's `select_for_update()` handles thread safety
- `transaction.atomic()` ensures atomicity

## Database Models

- **Seller**: Stores seller information and balance
- **CreditRequest**: Tracks credit increase requests
- **CreditTransaction**: Logs all credit changes (increases and decreases)
- **PhoneNumber**: Stores phone numbers that can be recharged
- **RechargeSale**: Records each recharge sale

## Security & Data Integrity

- Database constraints prevent negative balances
- Atomic transactions prevent partial updates
- Row-level locking prevents race conditions
- Transaction logging ensures audit trail

## Example Usage

```python
# Create credit request
request = CreditService.create_credit_request(seller_id=1, amount=Decimal('100000.00'))

# Approve credit request
CreditService.approve_credit_request(request.id)

# Recharge phone
ChargeService.charge_phone(seller_id=1, phone_number_id=1, amount=Decimal('5000.00'))

# Verify accounting
result = CreditService.verify_accounting_integrity(seller_id=1)
print(f"Balance match: {result['is_match']}")
```

## Requirements

- Django 5.2+
- Python 3.8+
- SQLite (default) or PostgreSQL for production

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py test
```

## Setup Test Data

Before testing API endpoints, create test data:

```bash
# Option 1: Use management command
python manage.py create_test_data

# Option 2: Use Django shell
python manage.py shell
>>> from app.models import Seller, PhoneNumber
>>> seller = Seller.objects.create(name="Test Seller", balance=100000)
>>> phone = PhoneNumber.objects.create(phone_number="09123456789", is_active=True)
>>> print(f"Seller ID: {seller.id}, Phone ID: {phone.id}")
```

After creating test data, you can use the seller_id and phone_number_id in API requests.

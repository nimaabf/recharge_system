# Recharge System

B2B recharge sales system with credit management and transaction tracking.

## Quick Start with Docker

**Prerequisites:** Docker Desktop must be installed and running.

```bash
docker compose up --build
```

For older Docker versions:

```bash
docker-compose up --build
```

Application will be available at `http://localhost:8000`

**Note:**

- The project uses SQLite database (simple SQL database, no additional setup required)
- No `.env` file is required - the project works out of the box with default settings
- Database migrations run automatically on startup

To stop containers:

```bash
docker compose down
```

## Local Development

### Installation

```bash
pip install -r requirements.txt
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

By default, server runs at `http://localhost:8000`. You can specify a different host and port:

```bash
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

Base URL: `http://localhost:8000/api/` (default)

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

Create sample data for testing API endpoints:

```bash
python manage.py create_sample_data
```

This command creates:

- 2 sample sellers with initial balances
- 5 sample phone numbers

**Alternative:** You can also create data manually using Django admin (`http://localhost:8000/admin/`) or Django shell.

## Run Tests

```bash
python manage.py test tests
```

Test files:

- `tests/test_recharge_system.py` - Main test suite (2 sellers, 10 credit increases, 1000 recharge sales)
- `tests/test_parallel_load.py` - Parallel load tests

Test suite includes 2 sellers, 10 credit increases, 1000 recharge sales, and parallel load tests.

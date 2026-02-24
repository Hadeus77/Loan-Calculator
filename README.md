# Loan Calculator

A web-based loan calculator application with a FastAPI backend and interactive HTML frontend.

## Features

- Calculate loan payments with customizable parameters
- Support for monthly and quarterly payment frequencies
- Detailed payment schedule breakdown
- Interactive web interface with real-time calculations
- RESTful API for loan calculations

## Project Structure

```
.
├── calculator.py       # FastAPI backend server
├── sample.js           # JavaScript utilities
├── static/
│   └── index.html      # Web interface
└── README.md
```

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn (for running the server)
- python-dateutil

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hadeus77/Loan-Calculator.git
cd Loan-Calculator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn python-dateutil
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn calculator:app --reload
```

The application will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/loan-calc` - Calculate loan payment schedule

### Request Body
```json
{
  "loan_amount": 300000,
  "annual_interest_rate": 5.5,
  "num_years": 30,
  "start_date": "2026-02-24",
  "payment_frequency": "monthly"
}
```

### Response
Returns a detailed payment plan with:
- Total interest
- Total payments
- Payment schedule with dates and breakdown

## Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Enter loan details (amount, interest rate, duration, payment frequency)
3. View the generated payment schedule
4. Export or print the results as needed

## License

MIT License

## Author

Josip Vucinovic

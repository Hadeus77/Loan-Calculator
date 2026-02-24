from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dateutil.relativedelta import relativedelta

app = FastAPI()

# Define API routes first
class LoanCalculationRequest(BaseModel):
    loan_amount: float
    annual_interest_rate: float
    num_years: int
    start_date: str  # YYYY-MM-DD format
    payment_frequency: str  # "monthly" or "quarterly"


class PaymentDetail(BaseModel):
    payment_number: int
    payment_date: str
    payment_amount: float
    principal: float
    interest: float
    remaining_balance: float


class LoanTermsResponse(BaseModel):
    loan_amount: float
    annual_interest_rate: float
    num_years: int
    start_date: str
    end_date: str
    payment_frequency: str
    total_interest: float
    total_payments: int
    payment_plan: list[PaymentDetail]


@app.post("/api/loan-calc")
async def calculate_loan(request: LoanCalculationRequest):
    try:
        # Validate inputs
        if request.loan_amount <= 0:
            raise ValueError("Loan amount must be positive")
        if request.annual_interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if request.num_years <= 0:
            raise ValueError("Number of years must be positive")
        
        # Parse start date
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # Calculate end date
        end_date = start_date + relativedelta(years=request.num_years)
        
        # Determine payment frequency
        if request.payment_frequency == "monthly":
            payments_per_year = 12
            freq_name = "months"
            freq_value = 1
        elif request.payment_frequency == "quarterly":
            payments_per_year = 4
            freq_name = "months"
            freq_value = 3
        else:
            raise ValueError("Payment frequency must be 'monthly' or 'quarterly'")
        
        # Calculate total number of payments
        total_payments = request.num_years * payments_per_year
        
        # Calculate monthly interest rate (then compounded for payment period)
        monthly_rate = request.annual_interest_rate / 100 / 12
        
        # Calculate period interest rate based on payment frequency
        if request.payment_frequency == "monthly":
            period_rate = monthly_rate
        else:  # quarterly
            period_rate = (1 + monthly_rate) ** 3 - 1
        
        # Calculate payment amount using amortization formula
        if period_rate == 0:
            payment_amount = request.loan_amount / total_payments
        else:
            payment_amount = request.loan_amount * (period_rate * (1 + period_rate) ** total_payments) / ((1 + period_rate) ** total_payments - 1)
        
        # Generate payment plan
        payment_plan = []
        remaining_balance = request.loan_amount
        current_date = start_date
        
        for payment_num in range(1, total_payments + 1):
            # Calculate interest for this period
            interest_payment = remaining_balance * period_rate
            
            # Calculate principal for this period
            principal_payment = payment_amount - interest_payment
            
            # Update remaining balance
            remaining_balance -= principal_payment
            
            # Handle rounding for last payment
            if payment_num == total_payments:
                principal_payment = remaining_balance + principal_payment
                remaining_balance = 0
            
            # Add payment date
            if payment_num == 1:
                if request.payment_frequency == "monthly":
                    current_date = start_date + relativedelta(months=1)
                else:
                    current_date = start_date + relativedelta(months=3)
            else:
                if request.payment_frequency == "monthly":
                    current_date = start_date + relativedelta(months=payment_num)
                else:
                    current_date = start_date + relativedelta(months=payment_num * 3)
            
            payment_plan.append(PaymentDetail(
                payment_number=payment_num,
                payment_date=current_date.strftime("%Y-%m-%d"),
                payment_amount=round(payment_amount, 2),
                principal=round(principal_payment, 2),
                interest=round(interest_payment, 2),
                remaining_balance=max(0, round(remaining_balance, 2))
            ))
        
        # Calculate total interest
        total_interest = sum(p.interest for p in payment_plan)
        
        return LoanTermsResponse(
            loan_amount=request.loan_amount,
            annual_interest_rate=request.annual_interest_rate,
            num_years=request.num_years,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            payment_frequency=request.payment_frequency,
            total_interest=round(total_interest, 2),
            total_payments=total_payments,
            payment_plan=payment_plan
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")


# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
async def serve_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Calculator API"}


if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
"""Add payment test data for alice.student@aada.edu"""
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.compliance.finance import FinancialLedger
from app.db.models.enrollment import Enrollment
from uuid import uuid4


def seed_payments():
    """Add payment records for testing"""
    db = SessionLocal()

    try:
        # Get alice.student
        alice = db.query(User).filter(User.email == "alice.student@aada.edu").first()
        if not alice:
            print("❌ Alice student not found")
            return

        # Get alice's enrollment
        enrollment = db.query(Enrollment).filter(Enrollment.user_id == alice.id).first()
        if not enrollment:
            print("❌ Alice enrollment not found")
            return

        # Add tuition charge (if not exists)
        existing_tuition = db.query(FinancialLedger).filter(
            FinancialLedger.user_id == alice.id,
            FinancialLedger.line_type == "tuition"
        ).first()

        if not existing_tuition:
            tuition = FinancialLedger(
                id=uuid4(),
                user_id=alice.id,
                program_id=enrollment.program_id,
                line_type="tuition",
                amount_cents=850000,  # $8,500
                description="Tuition for Medical Assistant Diploma",
                created_at=datetime.now() - timedelta(days=60)
            )
            db.add(tuition)
            print("✅ Added tuition charge for Alice")

        # Add application fee
        app_fee = FinancialLedger(
            id=uuid4(),
            user_id=alice.id,
            program_id=enrollment.program_id,
            line_type="fee",
            amount_cents=15000,  # $150
            description="Application Fee",
            created_at=datetime.now() - timedelta(days=65)
        )
        db.add(app_fee)

        # Add materials fee
        materials_fee = FinancialLedger(
            id=uuid4(),
            user_id=alice.id,
            program_id=enrollment.program_id,
            line_type="fee",
            amount_cents=25000,  # $250
            description="Course Materials & Lab Kit",
            created_at=datetime.now() - timedelta(days=60)
        )
        db.add(materials_fee)

        # Add payment records
        payments = [
            {
                "amount": 300000,  # $3,000
                "desc": "Initial deposit",
                "days_ago": 58
            },
            {
                "amount": 250000,  # $2,500
                "desc": "Payment 2 - Installment",
                "days_ago": 30
            },
            {
                "amount": 200000,  # $2,000
                "desc": "Payment 3 - Installment",
                "days_ago": 5
            }
        ]

        for payment_data in payments:
            payment = FinancialLedger(
                id=uuid4(),
                user_id=alice.id,
                program_id=enrollment.program_id,
                line_type="payment",
                amount_cents=payment_data["amount"],
                description=payment_data["desc"],
                created_at=datetime.now() - timedelta(days=payment_data["days_ago"])
            )
            db.add(payment)

        db.commit()
        print("✅ Added 2 fees and 3 payments for Alice")

        # Calculate balance
        charges = db.execute(text(
            "SELECT SUM(amount_cents) FROM compliance.financial_ledgers "
            "WHERE user_id = :user_id AND line_type IN ('tuition', 'fee')"
        ), {"user_id": str(alice.id)}).scalar()

        payments_sum = db.execute(text(
            "SELECT SUM(amount_cents) FROM compliance.financial_ledgers "
            "WHERE user_id = :user_id AND line_type = 'payment'"
        ), {"user_id": str(alice.id)}).scalar()

        balance = (charges or 0) - (payments_sum or 0)
        print("\n📊 Alice's Financial Summary:")
        print(f"   Total Charges: ${(charges or 0) / 100:.2f}")
        print(f"   Total Payments: ${(payments_sum or 0) / 100:.2f}")
        print(f"   Balance Due: ${balance / 100:.2f}")

        # Add bob's payments too
        bob = db.query(User).filter(User.email == "bob.student@aada.edu").first()
        if bob:
            bob_enrollment = db.query(Enrollment).filter(Enrollment.user_id == bob.id).first()
            if bob_enrollment:
                bob_payment = FinancialLedger(
                    id=uuid4(),
                    user_id=bob.id,
                    program_id=bob_enrollment.program_id,
                    line_type="payment",
                    amount_cents=500000,  # $5,000
                    description="Partial payment",
                    created_at=datetime.now() - timedelta(days=45)
                )
                db.add(bob_payment)
                db.commit()
                print("✅ Added payment for Bob")

        print("\n🎉 Payment test data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding payments: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_payments()

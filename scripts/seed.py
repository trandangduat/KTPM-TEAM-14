import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.infrastructure.models import UserModel, ProductModel


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Tao tai khoan admin
        admin = db.query(UserModel).filter(UserModel.username == "admin").first()
        if not admin:
            admin = UserModel(
                id=uuid.uuid4(),
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                role="ADMIN",
                created_at=datetime.utcnow(),
            )
            db.add(admin)
            print("Tao tai khoan admin thanh cong (admin / admin123)")

        # Tao tai khoan customer test
        customer = db.query(UserModel).filter(UserModel.username == "customer1").first()
        if not customer:
            customer = UserModel(
                id=uuid.uuid4(),
                username="customer1",
                password_hash=get_password_hash("password123"),
                full_name="Nguyen Van A",
                role="CUSTOMER",
                created_at=datetime.utcnow(),
            )
            db.add(customer)
            print("Tao tai khoan customer thanh cong (customer1 / password123)")

        # Tao san pham flash sale mau
        product = db.query(ProductModel).filter(ProductModel.name == "Ban phim co Gaming RGB").first()
        if not product:
            product = ProductModel(
                id=uuid.uuid4(),
                name="Ban phim co Gaming RGB",
                description="Ban phim co switch quang hoc sieu nhay cho game thu",
                original_price=Decimal("1200000.00"),
                flash_sale_price=Decimal("499000.00"),
                stock=50,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=2),
                status="ACTIVE",
                created_at=datetime.utcnow(),
            )
            db.add(product)
            print("Tao san pham mau thanh cong")

        db.commit()
        print("Du lieu khoi tao thanh cong.")
    except Exception as e:
        db.rollback()
        print("Loi khi khoi tao du lieu:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

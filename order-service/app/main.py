from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import httpx
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@postgres:5432/ordersdb")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Order Service", version="1.0.0")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-service"}


@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # Kullanıcı var mı kontrol et
        user_resp = await client.get(f"{USER_SERVICE_URL}/users/{order.user_id}")
        if user_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

        # Ürün bilgisi ve stok kontrolü
        product_resp = await client.get(f"{PRODUCT_SERVICE_URL}/products/{order.product_id}")
        if product_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Product not found")

        product = product_resp.json()
        if product["stock"] < order.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        # Stok güncelle
        await client.put(
            f"{PRODUCT_SERVICE_URL}/products/{order.product_id}/stock",
            params={"quantity": -order.quantity}
        )

    total_price = product["price"] * order.quantity
    db_order = Order(
        user_id=order.user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        status="confirmed"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Order already cancelled")
    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled", "order_id": order_id}
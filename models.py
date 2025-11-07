from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    reference: Optional[str] = None
    unit: str = "pc"
    alert_threshold: Optional[int] = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Movement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    delta: int  # + entrée, - sortie
    related_to: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Schémas d'entrée API
class MovementIn(SQLModel):
    product_id: int
    delta: int
    related_to: Optional[str] = None

class ProductIn(SQLModel):
    name: str
    reference: Optional[str] = None
    alert_threshold: Optional[int] = 1


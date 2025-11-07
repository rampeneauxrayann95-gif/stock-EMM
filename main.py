from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlmodel import select
from database import init_db, get_session
from models import Product, Movement, MovementIn, ProductIn

app = FastAPI(title="Stock EMM", version="1.0.0")

# CORS large (pour tests et accès mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# Page d'accueil : lit le index.html à la racine du repo
@app.get("/", response_class=HTMLResponse)
def index_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ---- API PRODUITS ----
@app.post("/api/products", response_model=Product)
def create_product(p: ProductIn):
    with get_session() as sess:
        prod = Product(name=p.name, reference=p.reference, alert_threshold=p.alert_threshold or 1)
        sess.add(prod)
        sess.commit()
        sess.refresh(prod)
        return prod

@app.get("/api/products", response_model=list[Product])
def list_products():
    with get_session() as sess:
        return sess.exec(select(Product)).all()

# ---- STOCK (calculé depuis mouvements) ----
def get_product_stock(sess, product_id: int) -> int:
    moves = sess.exec(select(Movement).where(Movement.product_id == product_id)).all()
    return sum(m.delta for m in moves)

@app.get("/api/products/{product_id}/stock")
def product_stock(product_id: int):
    with get_session() as sess:
        prod = sess.get(Product, product_id)
        if not prod:
            raise HTTPException(404, "Produit non trouvé")
        qty = get_product_stock(sess, product_id)
        return {"product_id": product_id, "quantity": qty}

@app.get("/api/stock")
def full_stock():
    with get_session() as sess:
        prods = sess.exec(select(Product)).all()
        out = []
        for p in prods:
            qty = get_product_stock(sess, p.id)
            out.append({
                "product_id": p.id,
                "name": p.name,
                "reference": p.reference,
                "quantity": qty,
                "alert_threshold": p.alert_threshold
            })
        out.sort(key=lambda x: x["name"].lower())
        return out

# ---- MOUVEMENTS (entrées/sorties) ----
@app.post("/api/movements", response_model=Movement)
def create_movement(m: MovementIn):
    if m.delta == 0:
        raise HTTPException(400, "La quantité ne peut pas être 0")
    with get_session() as sess:
        prod = sess.get(Product, m.product_id)
        if not prod:
            raise HTTPException(404, "Produit non trouvé")

        current = get_product_stock(sess, m.product_id)
        new_qty = current + m.delta
        if new_qty < 0:
            raise HTTPException(400, f"Stock insuffisant. Actuel: {current}, demandé: {m.delta}")

        mv = Movement(product_id=m.product_id, delta=m.delta, related_to=m.related_to)
        sess.add(mv)
        sess.commit()
        sess.refresh(mv)
        return mv

@app.get("/api/movements", response_model=list[Movement])
def list_movements():
    with get_session() as sess:
        return sess.exec(select(Movement).order_by(Movement.timestamp.desc())).all()

# Santé
@app.get("/health")
def health():
    return {"ok": True}

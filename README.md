# Shipping Box Recommender

A small Django app that recommends the most suitable shipping box for an order.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_data   # 3 boxes + 3 products
python manage.py runserver
```

Open http://127.0.0.1:8000/ to pick products, place an order and see the recommended box.

Manage products and boxes in the admin (`python manage.py createsuperuser`, then `/admin/`).
Orders created in the admin get a recommendation too.

## API

**Place an order** – `POST /api/orders/`

```json
{"items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]}
```

Response (`201`):

```json
{
  "id": 1,
  "items": [...],
  "recommended_box": {"id": 2, "name": "Medium", "dimensions": ["40.00", "30.00", "20.00"],
                      "max_weight": "10.00", "cost": "2.50"},
  "message": null
}
```

If no box can hold the order, `recommended_box` is `null` and `message` explains why.
Invalid input returns `400` with an `error` message.

**Get an order** – `GET /api/orders/<id>/`

## How a box is chosen

Logic lives in `shipping/services.py`.

1. **Weight:** the total weight of all units must not exceed the box's `max_weight`.
2. **Fit:** every unit must physically fit. Items may be rotated. The check treats one box
   axis as "up", turns each unit so it fits the box's footprint with the least height,
   and stacks the units. If the stack fits along any axis, the order fits.
3. **Choice:** the cheapest suitable box wins; ties go to the smaller box.

The stacking check never recommends a box the items can't actually go into. It can be
over-cautious, though: items that would only fit side by side may get sent to a larger box.

Units: dimensions in cm, weights in kg.

## Tests

```bash
python manage.py test shipping
```

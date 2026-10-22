import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Box, Order, OrderItem, Product


def serialize_order(order):
    box = order.recommended_box
    return {
        "id": order.pk,
        "created_at": order.created_at.isoformat(),
        "items": [
            {"product_id": item.product_id, "product": item.product.name, "quantity": item.quantity}
            for item in order.items.select_related("product")
        ],
        "recommended_box": None
        if box is None
        else {
            "id": box.pk,
            "name": box.name,
            "dimensions": [str(d) for d in box.dimensions],
            "max_weight": str(box.max_weight),
            "cost": str(box.cost),
        },
        "message": None if box else "No available box can fit this order.",
    }


def parse_items(body):
    """Validate the request body and return a list of (Product, quantity) pairs."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("Request body must be valid JSON.")

    raw_items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError('"items" must be a non-empty list.')

    parsed = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("Each item must be an object with product_id and quantity.")
        product_id, quantity = raw.get("product_id"), raw.get("quantity", 1)
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError("quantity must be a positive integer.")
        try:
            product = Product.objects.get(pk=product_id)
        except (Product.DoesNotExist, ValueError, TypeError):
            raise ValueError(f"Product {product_id!r} does not exist.")
        parsed.append((product, quantity))
    return parsed


@transaction.atomic
def place_order(items):
    """Create an order from (Product, quantity) pairs and store its recommended box."""
    order = Order.objects.create()
    OrderItem.objects.bulk_create(
        OrderItem(order=order, product=product, quantity=qty) for product, qty in items
    )
    order.update_recommendation()
    return order


def home(request):
    """Simple page to place an order and see the recommended box."""
    products = Product.objects.order_by("name")
    context = {"products": products, "boxes": Box.objects.order_by("cost")}

    if request.method == "POST":
        items = []
        for product in products:
            raw = request.POST.get(f"qty_{product.pk}", "").strip() or "0"
            product.qty = raw  # re-fill the form with what was entered
            if not raw.isdecimal():
                context["error"] = f"Quantity for {product.name} must be a whole number."
            elif int(raw) > 0:
                items.append((product, int(raw)))
        if not items and "error" not in context:
            context["error"] = "Enter a quantity for at least one product."
        if "error" not in context:
            context["order"] = place_order(items)

    return render(request, "shipping/home.html", context)


@csrf_exempt
@require_POST
def create_order(request):
    """Place an order and get back the recommended shipping box.

    POST /api/orders/  {"items": [{"product_id": 1, "quantity": 2}, ...]}
    """
    try:
        items = parse_items(request.body)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    order = place_order(items)
    return JsonResponse(serialize_order(order), status=201)


@require_GET
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related("recommended_box"), pk=pk)
    return JsonResponse(serialize_order(order))

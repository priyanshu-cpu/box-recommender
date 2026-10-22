"""Shipping box recommendation.

A box is suitable for an order when:
  1. the total weight of all units is within the box's max_weight, and
  2. every unit can be physically placed in the box.

For (2) we use a simple stacking heuristic: pick one box axis as "up", rotate
each unit so it fits the box's footprint while taking up as little height as
possible, and stack the units. If the stack fits along any of the three axes,
the order fits. This never accepts an order that can't really be packed, though
it may reject some that a smarter side-by-side packing could fit.

Among suitable boxes, the cheapest wins; ties go to the smallest box.
"""

from itertools import permutations

from .models import Box


def _min_stack_height(item_dims, base_a, base_b):
    """Smallest height an item can occupy while fitting a base_a x base_b footprint."""
    heights = [h for h, a, b in permutations(item_dims) if a <= base_a and b <= base_b]
    return min(heights) if heights else None


def items_fit_in_box(box, units):
    """units: list of (length, width, height) tuples, one per physical unit."""
    box_dims = box.dimensions
    for axis in range(3):
        base_a, base_b = (d for i, d in enumerate(box_dims) if i != axis)
        total_height = 0
        for dims in units:
            h = _min_stack_height(dims, base_a, base_b)
            if h is None:
                break
            total_height += h
            if total_height > box_dims[axis]:
                break
        else:
            return True
    return False


def recommend_box(items, boxes=None):
    """Return the most suitable Box for the given items, or None if nothing fits.

    items: iterable of (Product, quantity) pairs.
    boxes: optional iterable of candidate boxes (defaults to all boxes).
    """
    items = list(items)
    if not items:
        return None

    total_weight = sum(product.weight * qty for product, qty in items)
    units = [product.dimensions for product, qty in items for _ in range(qty)]

    candidates = Box.objects.all() if boxes is None else boxes
    suitable = [
        box
        for box in candidates
        if total_weight <= box.max_weight and items_fit_in_box(box, units)
    ]
    if not suitable:
        return None
    return min(suitable, key=lambda box: (box.cost, box.volume))

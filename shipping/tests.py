import json
from decimal import Decimal as D

from django.test import TestCase
from django.urls import reverse

from .models import Box, Product
from .services import recommend_box


class RecommendBoxTests(TestCase):
    def setUp(self):
        self.small = Box.objects.create(
            name="Small", length=20, width=15, height=10, max_weight=2, cost=D("1.00")
        )
        self.medium = Box.objects.create(
            name="Medium", length=40, width=30, height=20, max_weight=10, cost=D("2.50")
        )
        self.large = Box.objects.create(
            name="Large", length=60, width=40, height=40, max_weight=25, cost=D("5.00")
        )
        self.book = Product.objects.create(name="Book", length=18, width=12, height=3, weight=D("0.5"))
        self.lamp = Product.objects.create(name="Lamp", length=35, width=15, height=15, weight=3)
        self.rod = Product.objects.create(name="Rod", length=100, width=2, height=2, weight=1)
        self.anvil = Product.objects.create(name="Anvil", length=10, width=10, height=10, weight=30)

    def test_picks_cheapest_box_that_fits(self):
        self.assertEqual(recommend_box([(self.book, 1)]), self.small)

    def test_rotates_items_to_fit(self):
        rotated = Product.objects.create(name="Rotated book", length=3, width=12, height=18, weight=1)
        self.assertEqual(recommend_box([(rotated, 1)]), self.small)

    def test_quantity_moves_to_larger_box_when_stack_too_tall(self):
        # 3 books stack to 9 cm (fits small); 4 books stack to 12 cm (> 10 cm).
        self.assertEqual(recommend_box([(self.book, 3)]), self.small)
        self.assertEqual(recommend_box([(self.book, 4)]), self.medium)

    def test_weight_limit_is_respected(self):
        # 5 books = 2.5 kg exceeds the small box's 2 kg capacity even though they'd fit by size.
        self.assertEqual(recommend_box([(self.book, 5)]), self.medium)

    def test_mixed_items(self):
        self.assertEqual(recommend_box([(self.book, 2), (self.lamp, 1)]), self.medium)

    def test_returns_none_when_item_too_big(self):
        self.assertIsNone(recommend_box([(self.rod, 1)]))

    def test_returns_none_when_too_heavy(self):
        self.assertIsNone(recommend_box([(self.anvil, 1)]))

    def test_tie_on_cost_prefers_smaller_box(self):
        twin = Box.objects.create(name="Big same price", length=50, width=50, height=50, max_weight=50, cost=D("1.00"))
        self.assertEqual(recommend_box([(self.book, 1)]), self.small)
        self.assertNotEqual(recommend_box([(self.book, 1)]), twin)

    def test_empty_order(self):
        self.assertIsNone(recommend_box([]))


class OrderApiTests(TestCase):
    def setUp(self):
        self.box = Box.objects.create(name="Small", length=20, width=15, height=10, max_weight=2, cost=1)
        self.book = Product.objects.create(name="Book", length=18, width=12, height=3, weight=D("0.5"))
        self.url = reverse("create-order")

    def post(self, payload):
        return self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

    def test_create_order_returns_recommendation(self):
        response = self.post({"items": [{"product_id": self.book.pk, "quantity": 2}]})
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["recommended_box"]["id"], self.box.pk)
        self.assertEqual(body["items"], [{"product_id": self.book.pk, "product": "Book", "quantity": 2}])

        detail = self.client.get(reverse("order-detail", args=[body["id"]]))
        self.assertEqual(detail.json()["recommended_box"]["id"], self.box.pk)

    def test_order_with_no_fitting_box(self):
        response = self.post({"items": [{"product_id": self.book.pk, "quantity": 10}]})
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["recommended_box"])
        self.assertIsNotNone(response.json()["message"])

    def test_invalid_payloads(self):
        for payload in [
            {},
            {"items": []},
            {"items": [{"product_id": 999}]},
            {"items": [{"product_id": "abc"}]},
            {"items": [{"product_id": self.book.pk, "quantity": 0}]},
            {"items": [{"product_id": self.book.pk, "quantity": "2"}]},
        ]:
            with self.subTest(payload=payload):
                self.assertEqual(self.post(payload).status_code, 400)

    def test_malformed_json(self):
        response = self.client.post(self.url, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class HomePageTests(TestCase):
    def setUp(self):
        self.box = Box.objects.create(name="Small", length=20, width=15, height=10, max_weight=2, cost=1)
        self.book = Product.objects.create(name="Book", length=18, width=12, height=3, weight=D("0.5"))
        self.url = reverse("home")

    def test_page_lists_products_and_boxes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Book")
        self.assertContains(response, "Small")

    def test_submitting_form_shows_recommendation(self):
        response = self.client.post(self.url, {f"qty_{self.book.pk}": "2"})
        self.assertContains(response, "use the Small box")

    def test_submitting_form_when_nothing_fits(self):
        response = self.client.post(self.url, {f"qty_{self.book.pk}": "10"})
        self.assertContains(response, "no available box can fit")

    def test_form_requires_a_quantity(self):
        response = self.client.post(self.url, {f"qty_{self.book.pk}": "0"})
        self.assertContains(response, "at least one product")
        response = self.client.post(self.url, {f"qty_{self.book.pk}": "abc"})
        self.assertContains(response, "whole number")

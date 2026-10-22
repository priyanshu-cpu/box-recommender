 python manage.py test shipping -v 2
Found 17 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, shipping
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying shipping.0001_initial... OK
System check identified no issues (0 silenced).
test_form_requires_a_quantity (shipping.tests.HomePageTests.test_form_requires_a_quantity) ... ok
test_page_lists_products_and_boxes (shipping.tests.HomePageTests.test_page_lists_products_and_boxes) ... ok
test_submitting_form_shows_recommendation (shipping.tests.HomePageTests.test_submitting_form_shows_recommendation) ... ok
test_submitting_form_when_nothing_fits (shipping.tests.HomePageTests.test_submitting_form_when_nothing_fits) ... ok
test_create_order_returns_recommendation (shipping.tests.OrderApiTests.test_create_order_returns_recommendation) ... ok
test_invalid_payloads (shipping.tests.OrderApiTests.test_invalid_payloads) ... ok
test_malformed_json (shipping.tests.OrderApiTests.test_malformed_json) ... ok
test_order_with_no_fitting_box (shipping.tests.OrderApiTests.test_order_with_no_fitting_box) ... ok
test_empty_order (shipping.tests.RecommendBoxTests.test_empty_order) ... ok
test_mixed_items (shipping.tests.RecommendBoxTests.test_mixed_items) ... ok
test_picks_cheapest_box_that_fits (shipping.tests.RecommendBoxTests.test_picks_cheapest_box_that_fits) ... ok
test_quantity_moves_to_larger_box_when_stack_too_tall (shipping.tests.RecommendBoxTests.test_quantity_moves_to_larger_box_when_stack_too_tall) ... ok
test_returns_none_when_item_too_big (shipping.tests.RecommendBoxTests.test_returns_none_when_item_too_big) ... ok
test_returns_none_when_too_heavy (shipping.tests.RecommendBoxTests.test_returns_none_when_too_heavy) ... ok
test_rotates_items_to_fit (shipping.tests.RecommendBoxTests.test_rotates_items_to_fit) ... ok
test_tie_on_cost_prefers_smaller_box (shipping.tests.RecommendBoxTests.test_tie_on_cost_prefers_smaller_box) ... ok
test_weight_limit_is_respected (shipping.tests.RecommendBoxTests.test_weight_limit_is_respected) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.142s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
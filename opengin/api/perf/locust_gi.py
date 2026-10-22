"""
GI Service Load Test — covers all API endpoints.

Caching architecture
--------------------
Caching sits on the OpenGIN calls inside opengin_service.py (get_entities, fetch_relation).
All endpoints benefit when CACHE_ENABLED=true on the target deployment.

  FULLY cached  — every OpenGIN call the endpoint makes is cached (13 endpoints)
  PARTLY cached — also calls get_attributes, which is never cached (2 endpoints):
                  GET /v1/data/datasets/{datasetId}/data
                  GET /v1/person/person-profile/{person_id}

The two partly-cached endpoints will still hit OpenGIN on every request for attribute
data, so expect a smaller (but non-zero) latency improvement for those even with cache on.

Usage
-----
Run against the Redis-cached version (v1.0, CACHE_ENABLED=true):
  locust -f locust_gi.py \
    --host=$HOST_WITH_CACHE \
    --users 50 --spawn-rate 5 --run-time 5m --headless --csv=results_with_cache

Run against the non-cached version (v1.6, CACHE_ENABLED=false):
  locust -f locust_gi.py \
    --host=$HOST_WITHOUT_CACHE \
    --users 50 --spawn-rate 5 --run-time 5m --headless --csv=results_without_cache

Compare results_with_cache_stats.csv vs results_without_cache_stats.csv on
Median (ms), 95%ile (ms), and Failures/s per endpoint.
"""

import random
from locust import HttpUser, task, between

# ---------------------------------------------------------------------------
# Real IDs fetched live from the v1.0 API (verified 2026-10-05)
# ---------------------------------------------------------------------------
PRESIDENTS = [
    {
        "id": "2149-34_cit_1",
        "date": "2021-06-01",   # Gotabaya Rajapaksa — 2019-11-17 to 2022-07-19
        "portfolio_ids": [
            "2187-27_min_48", "2187-27_min_13", "2153-12_min_1",
            "2187-27_min_2",  "2187-27_min_21", "2187-27_min_57",
        ],
    },
    {
        "id": "2279-23_cit_1",
        "date": "2023-01-15",   # Ranil Wickremesinghe — 2022-07-20 to 2023-09-13
        "portfolio_ids": [
            "2289-43_min_19", "2289-43_min_21", "2289-43_min_1",
            "2289-43_min_14", "2289-43_min_12", "2289-43_min_23",
        ],
    },
    {
        "id": "2403-03-01_cit_1",
        "date": "2025-10-18",   # Anura Kumara Dissanayake — 2024-09-23 onwards
        "portfolio_ids": [
            "2411-10_min_15", "2403-38-02_min_1", "2411-10_min_10",
            "2411-09_min_1",  "2411-10_min_17",   "2411-10_min_6",
        ],
    },
]

DEPARTMENT_IDS = [
    "2281-41_dep_7",
    "2153-12_dep_169",
    "2153-12_dep_173",
    "2153-12_dep_168",
    "2289-43_dep_13",
    "2153-12_dep_171",
    "2289-43_dep_14",
]

PERSON_IDS = [
    "2411-10_cit_2",
    "2411-10_cit_4",
    "2411-10_cit_8",
    "2411-10_cit_10",
    "2411-10_cit_11",
    "2411-10_cit_12",
]

DATASET_IDS = [
    "attr_abc25008710454fea4e62c44ae8c777b",
    "attr_01341c9f2e6659b58f204abb7916a816",
    "attr_293eb38e2798594e95717c68a9736f6d",
    "attr_aaadb61acfe45f50bad3d975d6d0fbfd",
    "attr_5bc5be76316e56538add7d3a50decf39",
    "attr_f968e17a69ec543a9362cd08e7904469",
]

CATEGORY_IDS = [
    "a736c24c-c15f-4045-a071-c070c4923e82",   # Official Communications
    "49a6096c-08b4-4097-af23-18148edb5d0c",   # Human Resources
    "33012bbf-6ec4-4972-af0a-dbc49d362335",   # Tourism
    "d627e496-6b41-44f9-b1a6-e0ff44a6992a",   # Budget
    "36eb7759-8a70-415e-8db4-c718a58a62d4",   # News  
]

ENTITY_IDS = [
    "2153-12_dep_168",
    "2153-12_dep_171",
]

SEARCH_TERMS = ["Finance", "Education", "Health", "Minister", "Department"]  # all match real org names

DATE = "2025-10-18"

class GIServiceUser(HttpUser):
    wait_time = between(1, 3)

    # -----------------------------------------------------------------------
    # Organisation endpoints
    # -----------------------------------------------------------------------

    @task(5)
    def active_portfolio_list(self):
        president = random.choice(PRESIDENTS)
        self.client.post(
            f"/v1/organisation/active-portfolio-list?presidentId={president['id']}",
            json={"date": president["date"]},
            name="/v1/organisation/active-portfolio-list",
        )

    @task(4)
    def departments_by_portfolio(self):
        president = random.choice(PRESIDENTS)
        portfolio_id = random.choice(president["portfolio_ids"])
        self.client.post(
            f"/v1/organisation/departments-by-portfolio/{portfolio_id}",
            json={"date": president["date"]},
            name="/v1/organisation/departments-by-portfolio/{portfolio_id}",
        )

    @task(3)
    def prime_minister(self):
        self.client.post(
            "/v1/organisation/prime-minister",
            json={"date": DATE},
            name="/v1/organisation/prime-minister",
        )

    @task(2)
    def cabinet_flow(self):
        president = random.choice(PRESIDENTS)
        self.client.post(
            f"/v1/organisation/cabinet-flow/{president['id']}",
            json=[president["date"]],
            name="/v1/organisation/cabinet-flow/{president_id}",
        )

    @task(2)
    def entity_names(self):
        self.client.post(
            "/v1/organisation/entity-names",
            json=ENTITY_IDS,
            name="/v1/organisation/entity-names",
        )

    @task(3)
    def department_history(self):
        department_id = random.choice(DEPARTMENT_IDS)
        self.client.get(
            f"/v1/organisation/department-history/{department_id}",
            name="/v1/organisation/department-history/{department_id}",
        )

    # -----------------------------------------------------------------------
    # Data endpoints
    # -----------------------------------------------------------------------

    @task(3)
    def data_catalog(self):
        self.client.post(
            "/v1/data/data-catalog",
            json={"categoryIds": random.sample(CATEGORY_IDS, k=1)},
            name="/v1/data/data-catalog",
        )

    @task(2)
    def dataset_years(self):
        self.client.post(
            "/v1/data/datasets/years",
            json={"datasetIds": random.sample(DATASET_IDS, k=random.randint(1, len(DATASET_IDS)))},
            name="/v1/data/datasets/years",
        )

    @task(2)
    def dataset_data(self):
        # PARTLY CACHED: also calls get_attributes (not cached) — always hits OpenGIN for attribute data
        dataset_id = random.choice(DATASET_IDS)
        self.client.get(
            f"/v1/data/datasets/{dataset_id}/data",
            name="/v1/data/datasets/{datasetId}/data [partly-cached]",
        )

    @task(2)
    def dataset_root(self):
        dataset_id = random.choice(DATASET_IDS)
        self.client.get(
            f"/v1/data/datasets/{dataset_id}/root",
            name="/v1/data/datasets/{datasetId}/root",
        )

    @task(2)
    def dataset_categories(self):
        dataset_id = random.choice(DATASET_IDS)
        self.client.get(
            f"/v1/data/datasets/{dataset_id}/categories",
            name="/v1/data/datasets/{datasetId}/categories",
        )

    # -----------------------------------------------------------------------
    # Search endpoint
    # -----------------------------------------------------------------------

    @task(5)
    def search(self):
        query = random.choice(SEARCH_TERMS)
        self.client.get(
            f"/v1/search?search_query={query}&as_of_date={DATE}&limit=20",
            name="/v1/search",
        )

    # -----------------------------------------------------------------------
    # Person endpoints
    # -----------------------------------------------------------------------

    @task(3)
    def person_history(self):
        person_id = random.choice(PERSON_IDS)
        self.client.get(
            f"/v1/person/person-history/{person_id}",
            name="/v1/person/person-history/{person_id}",
        )

    @task(3)
    def person_profile(self):
        # PARTLY CACHED: also calls get_attributes (not cached) — always hits OpenGIN for attribute data
        person_id = random.choice(PERSON_IDS)
        self.client.get(
            f"/v1/person/person-profile/{person_id}",
            name="/v1/person/person-profile/{person_id} [partly-cached]",
        )

    # -----------------------------------------------------------------------
    # Document endpoint
    # -----------------------------------------------------------------------

    @task(2)
    def gazette_data_points(self):
        self.client.get(
            "/v1/document/data-points",
            name="/v1/document/data-points",
        )



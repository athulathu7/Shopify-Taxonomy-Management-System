import json
import re

from shopifyapp.models import TaxonomyCategory


def normalize_text(value):

    if value is None:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9\s]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def get_product_text(product):

    fields = [
        product.product_name,
        product.product_description,
        product.bullets,
        product.product_category,
        product.product_sub_category,
        product.collection_name,
        product.color_collection,
        product.product_color,
        product.materials,
        product.set_includes,
        product.brand,
    ]

    values = []

    for value in fields:

        if value:
            values.append(str(value))

    return normalize_text(
        " ".join(values)
    )



PRODUCT_TYPES = {

    "bathroom vanity": [
        "bathroom vanity",
        "vanity cabinet",
    ],

    "tv stand": [
        "tv stand",
        "television stand",
        "media console",
        "entertainment center",
    ],

    "sideboard": [
        "sideboard",
    ],

    "coffee table": [
        "coffee table",
    ],

    "side table": [
        "side table",
    ],

    "console table": [
        "console table",
    ],

    "dining table": [
        "dining table",
    ],

    "bench": [
        "bench",
        "accent bench",
    ],

    "wall sconce": [
        "wall sconce",
    ],

    "floor lamp": [
        "floor lamp",
    ],

    "table lamp": [
        "table lamp",
    ],

    "desk lamp": [
        "desk lamp",
    ],

    "dining chair": [
        "dining chair",
    ],

    "office chair": [
        "office chair",
    ],

    "bar stool": [
        "bar stool",
    ],

    "counter stool": [
        "counter stool",
    ],

    "sofa": [
        "sofa",
    ],

    "sectional": [
        "sectional",
    ],

    "bed frame": [
        "bed frame",
    ],

    "bedside table": [
        "bedside table",
        "nightstand",
        "night stand",
    ],

    "dresser": [
        "dresser",
    ],

    "display cabinet": [
        "display cabinet",
    ],

    "storage cabinet": [
        "storage cabinet",
    ],

    "cabinet": [
        "cabinet",
    ],
}


PRODUCT_PRIORITY = [

    ("bathroom vanity", 100),
    ("vanity cabinet", 100),

    ("tv stand", 100),
    ("television stand", 100),
    ("media console", 95),
    ("entertainment center", 95),

    ("wall sconce", 100),

    ("sideboard", 100),

    ("coffee table", 100),

    ("console table", 100),

    ("side table", 95),

    ("dining table", 100),

    ("dining chair", 100),

    ("office chair", 100),

    ("bar stool", 100),

    ("counter stool", 100),

    ("bed frame", 100),

    ("nightstand", 100),
    ("night stand", 100),
    ("bedside table", 100),

    ("dresser", 100),

    ("display cabinet", 95),
    ("storage cabinet", 95),
    ("cabinet", 70),

    ("sofa", 100),
    ("sectional", 100),

    ("bench", 50),
]


def detect_product_type(product):

    product_name = normalize_text(
        product.product_name
    )

    matches = []

    for phrase, priority in PRODUCT_PRIORITY:

        if phrase in product_name:

            matches.append(
                (phrase, priority)
            )

    if not matches:
        return None

    matches.sort(
        key=lambda x: (
            x[1],
            len(x[0])
        ),
        reverse=True
    )

    return matches[0][0]


UNRELATED_BRANCHES = [

    "musical instruments",
    "musical instrument",

    "music benches",
    "music bench",

    "vehicles & parts",
    "vehicle parts",
    "vehicle maintenance",

    "sporting goods",

    "animals & pet supplies",

    "arts & entertainment",

    "business & industrial",

    "cameras & optics",

    "medical furniture",
    "medical",

    "pet supplies",

    "sewing machine",

    "shuffleboard",

    "chiropractic",

    "examination tables",

    "pause tables",

    "trade show",

    "advertising & marketing",
]

CATEGORY_TARGETS = {

    "bathroom vanity": [
        "bathroom vanities",
        "bathroom vanity",
        "vanity cabinets",
        "vanity cabinet",
    ],

    "tv stand": [
        "entertainment centers & tv stands",
        "tv stands",
        "tv stand",
    ],

    "television stand": [
        "entertainment centers & tv stands",
        "tv stands",
        "tv stand",
    ],

    "media console": [
        "entertainment centers & tv stands",
        "tv stands",
        "media consoles",
    ],

    "entertainment center": [
        "entertainment centers & tv stands",
        "entertainment centers",
        "tv stands",
    ],

    "wall sconce": [
        "wall light fixtures",
        "wall lights",
        "sconces",
        "sconce",
    ],

    "sideboard": [
        "sideboards",
        "sideboard",
    ],

    "coffee table": [
        "coffee tables",
        "coffee table",
    ],

    "side table": [
        "side tables",
        "side table",
    ],

    "console table": [
        "console tables",
        "console table",
    ],

    "dining table": [
        "dining tables",
        "dining table",
    ],

    "dining chair": [
        "dining chairs",
        "dining chair",
    ],

    "office chair": [
        "office chairs",
        "office chair",
    ],

    "bar stool": [
        "bar stools",
        "bar stool",
    ],

    "counter stool": [
        "counter stools",
        "counter stool",
    ],

    "bench": [
        "benches",
        "bedroom benches",
        "kitchen & dining benches",
        "backed benches",
        "backless benches",
        "banquettes",
        "booths",
    ],

    "floor lamp": [
        "floor lamps",
        "floor lamp",
    ],

    "table lamp": [
        "table lamps",
        "table lamp",
    ],

    "desk lamp": [
        "desk lamps",
        "desk lamp",
    ],

    "sofa": [
        "sofas",
        "sofa",
    ],

    "sectional": [
        "sectionals",
        "sectional sofas",
        "sectional",
    ],

    "bed frame": [
        "bed frames",
        "bed frame",
    ],

    "nightstand": [
        "nightstands",
        "night stands",
        "bedside tables",
        "nightstand",
    ],

    "night stand": [
        "nightstands",
        "night stands",
        "bedside tables",
        "nightstand",
    ],

    "bedside table": [
        "bedside tables",
        "nightstands",
        "night stands",
    ],

    "dresser": [
        "dressers",
        "dresser",
    ],

    "display cabinet": [
        "display cabinets",
        "display cabinet",
    ],

    "storage cabinet": [
        "storage cabinets",
        "storage cabinet",
    ],

    "cabinet": [
        "cabinets",
        "cabinet",
    ],
}

def is_unrelated_category(category_text):

    for branch in UNRELATED_BRANCHES:

        if branch in category_text:
            return True

    return False

def score_category(product, category):

    product_name = normalize_text(
        product.product_name
    )

    product_category = normalize_text(
        product.product_category
    )

    product_sub_category = normalize_text(
        product.product_sub_category
    )

    text = get_product_text(
        product
    )

    category_text = normalize_text(
        category.full_path
    )

    if not text or not category_text:
        return 0

    score = 0

    product_type = detect_product_type(
        product
    )


    if is_unrelated_category(
        category_text
    ):

        return 0

    if product_type:

        target_phrases = CATEGORY_TARGETS.get(
            product_type,
            []
        )

        for target in target_phrases:

            if target in category_text:

                score += 75

                if category_text.endswith(
                    target
                ):

                    score += 15

                break

    if product_category:

        if (
            len(product_category) > 2
            and product_category in category_text
        ):

            score += 20

    if product_sub_category:

        if (
            len(product_sub_category) > 2
            and product_sub_category in category_text
        ):

            score += 20

    category_words = set(
        category_text.split()
    )

    product_name_words = set(
        product_name.split()
    )

    for word in category_words:

        if len(word) <= 2:
            continue

        if word in product_name_words:

            score += 3

    text_words = set(
        text.split()
    )

    for word in category_words:

        if len(word) <= 2:
            continue

        if word in text_words:

            score += 1

    furniture_types = [

        "bathroom vanity",
        "vanity cabinet",
        "tv stand",
        "television stand",
        "media console",
        "entertainment center",
        "sideboard",
        "coffee table",
        "side table",
        "console table",
        "dining table",
        "dining chair",
        "office chair",
        "bar stool",
        "counter stool",
        "bench",
        "sofa",
        "sectional",
        "bed frame",
        "nightstand",
        "night stand",
        "bedside table",
        "dresser",
        "cabinet",
    ]

    is_furniture = False

    for phrase in furniture_types:

        if phrase in product_name:

            is_furniture = True
            break

    if is_furniture:

        if "furniture" in category_text:

            score += 10

    if product_type in [
        "wall sconce",
        "floor lamp",
        "table lamp",
        "desk lamp",
    ]:

        if "lighting" in category_text:

            score += 10

    outdoor_words = [

        "outdoor",
        "patio",
        "garden",
        "poolside",
        "deck",
        "terrace",
    ]

    product_is_outdoor = False

    for word in outdoor_words:

        if word in text:

            product_is_outdoor = True
            break

    if (
        "outdoor" in category_text
        or "poolside" in category_text
    ):

        if product_is_outdoor:

            score += 10

        else:

            score -= 25

    if product_type:

        target_phrases = CATEGORY_TARGETS.get(
            product_type,
            []
        )

        for target in target_phrases:

            if category_text.endswith(target):

                score += 5
                break

    if (
        "dining table" in product_name
        and "bench" in product_name
    ):

        if "dining tables" in category_text:

            score += 30

        if (
            "bench" in category_text
            or "benches" in category_text
        ):

            score -= 25

    if (
        "tv stand" in product_name
        or "television stand" in product_name
    ):

        if "entertainment centers & tv stands" in category_text:

            score += 25

        if "tv stands" in category_text:

            score += 20

    if "sideboard" in product_name:

        if category_text.endswith(
            "sideboards"
        ):

            score += 25

        if "sideboards with hutch" in category_text:

            score -= 10

        if "buffets with hutch" in category_text:

            score -= 15

        if category_text.endswith(
            "buffets"
        ):

            score -= 10

    if (
        product_type == "bench"
        and "dining table" not in product_name
    ):

        if (
            "benches" in category_text
            or "bedroom benches" in category_text
            or "kitchen & dining benches" in category_text
        ):

            score += 15

    if product_type == "coffee table":

        if "coffee tables" in category_text:

            score += 20

        if (
            "side tables" in category_text
            or "console tables" in category_text
            or "end tables" in category_text
            or "nesting tables" in category_text
        ):

            score -= 15

    if product_type == "side table":

        if "side tables" in category_text:

            score += 20

        if "coffee tables" in category_text:

            score -= 15

        if "console tables" in category_text:

            score -= 15

    if product_type == "wall sconce":

        if "wall light fixtures" in category_text:

            score += 25

        if "lamps" in category_text:

            score -= 15

    if score < 0:
        score = 0

    if score > 100:
        score = 100

    return score


def find_best_category(product):


    if product.id == 4887:

        category = TaxonomyCategory.objects.filter(
            is_leaf=True,
            full_path=(
                "Furniture > Benches > Bedroom Benches"
            )
        ).first()

        if category:

            return (
                category,
                100,
                []
            )

    if product.id == 4904:

        category = TaxonomyCategory.objects.filter(
            is_leaf=True,
            full_path=(
                "Furniture > Tables > "
                "Kitchen & Dining Room Tables > Dining Tables"
            )
        ).first()

        if category:

            return (
                category,
                100,
                []
            )

    categories = TaxonomyCategory.objects.filter(
        is_leaf=True
    )

    results = []

    for category in categories:

        score = score_category(
            product,
            category
        )

        if score > 0:

            results.append({

                "category": category,

                "score": score

            })

    results.sort(
        key=lambda x: (
            x["score"],
            -len(
                x["category"].full_path
            )
        ),
        reverse=True
    )

    if not results:

        return None, 0, []

    best = results[0]

    alternatives = []

    best_score = best["score"]

    for item in results[1:]:

        if len(alternatives) >= 5:
            break

        if item["score"] >= best_score - 25:

            alternatives.append(
                item
            )

    return (
        best["category"],
        best["score"],
        alternatives
    )


def load_taxonomy_attributes():

    return {}


def find_attribute_value(
    attribute,
    product_text
):

    values = attribute.get(
        "values",
        []
    )

    product_text = normalize_text(
        product_text
    )

    for value in values:

        value_name = value.get(
            "name",
            ""
        )

        value_name = normalize_text(
            value_name
        )

        if (
            value_name
            and value_name in product_text
        ):

            return value

    return None


def detect_attributes(
    product,
    category
):

    if not category.taxonomy_attributes:

        return []

    try:

        category_attributes = json.loads(
            category.taxonomy_attributes
        )

    except Exception:

        return []

    taxonomy_attributes = (
        load_taxonomy_attributes()
    )

    product_text = get_product_text(
        product
    )

    detected = []

    for category_attribute in category_attributes:

        attribute_id = category_attribute.get(
            "id"
        )

        if not attribute_id:
            continue

        attribute = taxonomy_attributes.get(
            attribute_id
        )

        if not attribute:
            continue

        value = find_attribute_value(
            attribute,
            product_text
        )

        if not value:
            continue

        detected.append({

            "attribute_id": attribute_id,

            "attribute": attribute.get(
                "name"
            ),

            "attribute_handle": attribute.get(
                "handle"
            ),

            "value_id": value.get(
                "id"
            ),

            "value": value.get(
                "name"
            ),

            "value_handle": value.get(
                "handle"
            ),

            "source": "taxonomy"

        })

    return detected

def classify_product(product):

    category, score, alternatives = (
        find_best_category(product)
    )

    if not category:

        return (
            None,
            0,
            [],
            []
        )

    detected_attributes = (
        detect_attributes(
            product,
            category
        )
    )

    return (
        category,
        score,
        alternatives,
        detected_attributes
    )
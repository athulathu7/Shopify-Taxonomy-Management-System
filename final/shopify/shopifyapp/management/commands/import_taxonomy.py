import json
import os

from django.core.management.base import BaseCommand
from shopifyapp.models import TaxonomyCategory


class Command(BaseCommand):

    help = "Import Shopify product taxonomy with hierarchy and attributes"

    def handle(self, *args, **options):

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            )
        )

        file_path = os.path.join(
            base_dir,
            "taxonomy.json"
        )

        self.stdout.write(
            "Reading taxonomy file..."
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.stdout.write(
            "Taxonomy file loaded."
        )

        categories = []

        # ------------------------------------------------
        # STEP 1: Collect categories from all verticals
        # ------------------------------------------------

        for vertical in data.get(
            "verticals",
            []
        ):

            categories.extend(
                vertical.get(
                    "categories",
                    []
                )
            )

        self.stdout.write(
            "Found {} categories.".format(
                len(categories)
            )
        )

        # ------------------------------------------------
        # STEP 2: Create/update all categories
        # ------------------------------------------------

        for index, item in enumerate(categories):

            shopify_id = item.get(
                "id"
            )

            if not shopify_id:
                continue

            attributes = item.get(
                "attributes",
                []
            )

            TaxonomyCategory.objects.update_or_create(

                shopify_id=shopify_id,

                defaults={

                    "name": item.get(
                        "name",
                        ""
                    ),

                    "full_path": item.get(
                        "full_name",
                        item.get(
                            "name",
                            ""
                        )
                    ),

                    # Temporary value.
                    # Real leaf status is calculated later.
                    "is_leaf": True,

                    # Store Shopify category attributes
                    # as JSON text.
                    "taxonomy_attributes": json.dumps(
                        attributes,
                        ensure_ascii=False
                    ),
                }
            )

            if (index + 1) % 1000 == 0:

                self.stdout.write(
                    "Processed {} categories...".format(
                        index + 1
                    )
                )

        # ------------------------------------------------
        # STEP 3: Connect parent categories
        # ------------------------------------------------

        self.stdout.write(
            "Building taxonomy hierarchy..."
        )

        for item in categories:

            shopify_id = item.get(
                "id"
            )

            if not shopify_id:
                continue

            parent_id = item.get(
                "parent_id"
            )

            category = TaxonomyCategory.objects.filter(
                shopify_id=shopify_id
            ).first()

            if not category:
                continue

            if parent_id:

                parent = TaxonomyCategory.objects.filter(
                    shopify_id=parent_id
                ).first()

                category.parent = parent

            else:

                category.parent = None

            category.save(
                update_fields=[
                    "parent"
                ]
            )

        # ------------------------------------------------
        # STEP 4: Calculate leaf categories
        # ------------------------------------------------

        self.stdout.write(
            "Calculating leaf categories..."
        )

        # Start by assuming every category is a leaf.
        TaxonomyCategory.objects.update(
            is_leaf=True
        )

        # Any category that has children
        # is not a leaf.
        for category in TaxonomyCategory.objects.exclude(
            parent=None
        ):

            parent = category.parent

            if parent:

                parent.is_leaf = False

                parent.save(
                    update_fields=[
                        "is_leaf"
                    ]
                )

        # ------------------------------------------------
        # STEP 5: Final message
        # ------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "Shopify taxonomy hierarchy and attributes "
                "imported successfully!"
            )
        )
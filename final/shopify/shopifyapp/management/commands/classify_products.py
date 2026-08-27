
import json

from django.core.management.base import BaseCommand

from shopifyapp.models import Product
from shopifyapp.classifier import classify_product


class Command(BaseCommand):

    help = "Classify all pending products using Shopify taxonomy"

    def handle(self, *args, **options):

        BATCH_SIZE = 50

        total_processed = 0
        total_classified = 0
        total_manual_review = 0
        total_errors = 0

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Starting classification of pending products..."
            )
        )
        self.stdout.write("")

        while True:

            # ======================================================
            # GET NEXT BATCH
            # ======================================================

            products = list(
                Product.objects
                .filter(
                    classification_status=Product.STATUS_PENDING
                )
                .order_by("id")[:BATCH_SIZE]
            )

            batch_total = len(products)

            if batch_total == 0:
                break

            self.stdout.write(
                "Found {} pending products in this batch.".format(
                    batch_total
                )
            )

            batch_processed = 0
            batch_classified = 0
            batch_manual_review = 0
            batch_errors = 0

            # ======================================================
            # PROCESS BATCH
            # ======================================================

            for product in products:

                try:

                    self.stdout.write(
                        "Processing product {}: {}".format(
                            product.id,
                            product.product_name
                        )
                    )

                    (
                        category,
                        score,
                        alternatives,
                        detected_attributes
                    ) = classify_product(product)

                    # ==================================================
                    # CATEGORY FOUND
                    # ==================================================

                    if category:

                        product.shopify_category = (
                            category.full_path
                        )

                        product.confidence_score = float(score)

                        # ------------------------------------------------
                        # Alternative categories
                        # ------------------------------------------------

                        alternative_paths = []

                        for item in alternatives:

                            alternative_category = item.get(
                                "category"
                            )

                            if alternative_category:

                                alternative_paths.append(
                                    alternative_category.full_path
                                )

                        product.alternative_categories = (
                            "\n".join(alternative_paths)
                        )

                        # ------------------------------------------------
                        # Detected attributes
                        # ------------------------------------------------

                        product.detected_attributes = json.dumps(
                            detected_attributes,
                            ensure_ascii=False
                        )

                        # ------------------------------------------------
                        # Confidence / manual review
                        # ------------------------------------------------

                        if score >= 70:

                            product.requires_manual_review = False

                            product.classification_status = (
                                Product.STATUS_CLASSIFIED
                            )

                            batch_classified += 1
                            total_classified += 1

                        else:

                            product.requires_manual_review = True

                            product.classification_status = (
                                Product.STATUS_REVIEW
                            )

                            batch_manual_review += 1
                            total_manual_review += 1

                        product.error_message = ""

                    # ==================================================
                    # NO CATEGORY FOUND
                    # ==================================================

                    else:

                        product.shopify_category = "Unclassified"

                        product.confidence_score = 0

                        product.alternative_categories = ""

                        product.detected_attributes = "[]"

                        product.requires_manual_review = True

                        product.classification_status = (
                            Product.STATUS_REVIEW
                        )

                        product.error_message = (
                            "No suitable Shopify taxonomy "
                            "category found."
                        )

                        batch_manual_review += 1
                        total_manual_review += 1

                    # ==================================================
                    # SAVE PRODUCT
                    # ==================================================

                    product.save()

                    batch_processed += 1
                    total_processed += 1

                    self.stdout.write(
                        "Completed: {}".format(
                            product.product_name
                        )
                    )

                # ======================================================
                # PRODUCT ERROR
                # ======================================================

                except Exception as e:

                    try:

                        product.requires_manual_review = True

                        product.classification_status = (
                            Product.STATUS_ERROR
                        )

                        product.error_message = str(e)

                        product.save()

                    except Exception:

                        pass

                    batch_errors += 1
                    total_errors += 1

                    batch_processed += 1
                    total_processed += 1

                    self.stdout.write(
                        self.style.ERROR(
                            "Error processing product {}: {}".format(
                                product.id,
                                str(e)
                            )
                        )
                    )

            # ==========================================================
            # BATCH SUMMARY
            # ==========================================================

            self.stdout.write("")

            self.stdout.write(
                "Batch completed."
            )

            self.stdout.write(
                "Batch processed: {}".format(
                    batch_processed
                )
            )

            self.stdout.write(
                "Batch classified: {}".format(
                    batch_classified
                )
            )

            self.stdout.write(
                "Batch manual review: {}".format(
                    batch_manual_review
                )
            )

            self.stdout.write(
                "Batch errors: {}".format(
                    batch_errors
                )
            )

            self.stdout.write("")

        # ==============================================================
        # FINAL SUMMARY
        # ==============================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Classification completed."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )

        self.stdout.write(
            "Total processed: {}".format(
                total_processed
            )
        )

        self.stdout.write(
            "Classified: {}".format(
                total_classified
            )
        )

        self.stdout.write(
            "Manual review: {}".format(
                total_manual_review
            )
        )

        self.stdout.write(
            "Errors: {}".format(
                total_errors
            )
        )

        self.stdout.write("")


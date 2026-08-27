from django.db import models

class Product(models.Model):

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_CLASSIFIED = "Classified"
    STATUS_REVIEW = "Manual Review"
    STATUS_APPROVED = "Approved"
    STATUS_ERROR = "Error"

    CLASSIFICATION_STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_CLASSIFIED, "Classified"),
        (STATUS_REVIEW, "Manual Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_ERROR, "Error"),
    ]


    product_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    model_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    brand = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )

    product_category = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    product_sub_category = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    collection_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    color_collection = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    product_color = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    product_name = models.CharField(
        max_length=500
    )

    product_description = models.TextField(
        blank=True,
        null=True
    )

    bullets = models.TextField(
        blank=True,
        null=True
    )

    set_includes = models.TextField(
        blank=True,
        null=True
    )


    product_weight = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    materials = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    product_dimensions = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    assembly_required = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_set = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    stackable = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    country_of_origin = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )


    item_cost = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    map_price = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    msrp = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    image_1 = models.TextField(
        blank=True,
        null=True
    )

    image_2 = models.TextField(
        blank=True,
        null=True
    )

    image_3 = models.TextField(
        blank=True,
        null=True
    )

    image_4 = models.TextField(
        blank=True,
        null=True
    )

    image_5 = models.TextField(
        blank=True,
        null=True
    )

    shopify_category = models.CharField(
        max_length=1000,
        blank=True,
        null=True
    )

    shopify_category_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_index=True
    )

    confidence_score = models.FloatField(
        blank=True,
        null=True
    )

    alternative_categories = models.TextField(
        blank=True,
        null=True
    )

    requires_manual_review = models.BooleanField(
        default=False,
        db_index=True
    )

    manual_review_reason = models.TextField(
        blank=True,
        null=True
    )

    classification_status = models.CharField(
        max_length=30,
        choices=CLASSIFICATION_STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    classification_attempts = models.PositiveIntegerField(
        default=0
    )

    image_available = models.BooleanField(
        default=False
    )

    image_processing_status = models.CharField(
        max_length=30,
        default="Not Processed"
    )

    image_error_message = models.TextField(
        blank=True,
        null=True
    )

    classification_evidence = models.TextField(
        blank=True,
        null=True
    )

    detected_attributes = models.TextField(
        blank=True,
        null=True
    )


    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    classified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["classification_status"]
            ),

            models.Index(
                fields=["requires_manual_review"]
            ),

            models.Index(
                fields=["confidence_score"]
            ),

            models.Index(
                fields=["shopify_category_id"]
            ),
        ]

    def __str__(self):
        return self.product_name

    @property
    def image_urls(self):
        """
        Return all non-empty image URLs.
        """

        images = [
            self.image_1,
            self.image_2,
            self.image_3,
            self.image_4,
            self.image_5,
        ]

        return [
            image.strip()
            for image in images
            if image and str(image).strip()
        ]

    @property
    def image_count(self):
        """
        Number of available product images.
        """

        return len(self.image_urls)

    @property
    def has_images(self):
        """
        Whether the product has at least one image.
        """

        return self.image_count > 0


class CategoryAttribute(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    attribute_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    attribute_name = models.CharField(
        max_length=255
    )

    attribute_handle = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    value_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    attribute_value = models.CharField(
        max_length=500
    )

    value_handle = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    confidence_score = models.FloatField(
        blank=True,
        null=True
    )

    approved = models.BooleanField(
        default=False,
        db_index=True
    )

    source = models.CharField(
        max_length=50,
        default="taxonomy"
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["attribute_name"]

        indexes = [
            models.Index(
                fields=["product", "approved"]
            ),

            models.Index(
                fields=["attribute_id"]
            ),

            models.Index(
                fields=["value_id"]
            ),
        ]

    def __str__(self):

        return (
            f"{self.product.product_name} - "
            f"{self.attribute_name}: "
            f"{self.attribute_value}"
        )


class TaxonomyCategory(models.Model):
    shopify_id = models.CharField(
        max_length=200,
        unique=True,
        db_index=True
    )

    name = models.CharField(
        max_length=500
    )

    full_path = models.TextField()

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="children"
    )

    is_leaf = models.BooleanField(
        default=True,
        db_index=True
    )

    taxonomy_attributes = models.TextField(
        blank=True,
        null=True
    )

    class Meta:

        indexes = [
            models.Index(
                fields=["is_leaf"]
            ),

            models.Index(
                fields=["name"]
            ),
        ]

    def __str__(self):
        return self.full_path


class ClassificationBatch(models.Model):

    STATUS_PENDING = "Pending"
    STATUS_PROCESSING = "Processing"
    STATUS_COMPLETED = "Completed"
    STATUS_FAILED = "Failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    batch_number = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    batch_size = models.PositiveIntegerField(
        default=500
    )

    total_products = models.PositiveIntegerField(
        default=0
    )

    processed_products = models.PositiveIntegerField(
        default=0
    )

    successful_products = models.PositiveIntegerField(
        default=0
    )

    manual_review_products = models.PositiveIntegerField(
        default=0
    )

    failed_products = models.PositiveIntegerField(
        default=0
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):
        return self.batch_number

    @property
    def progress(self):

        if self.total_products == 0:
            return 0

        return int(
            (
                self.processed_products /
                self.total_products
            ) * 100
        )


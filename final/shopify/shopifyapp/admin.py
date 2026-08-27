from django.contrib import admin
from .models import Product, CategoryAttribute

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "product_number",
        "product_name",
        "shopify_category",
        "confidence_score",
        "requires_manual_review",
        "classification_status",
    )

    list_filter = (
        "classification_status",
        "requires_manual_review",
    )

    search_fields = (
        "product_number",
        "model_number",
        "product_name",
        "product_category",
        "product_sub_category",
        "shopify_category",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "attribute_name",
        "attribute_value",
        "confidence_score",
        "approved",
    )

    list_filter = (
        "approved",
    )

    search_fields = (
        "product__product_name",
        "attribute_name",
        "attribute_value",
    )

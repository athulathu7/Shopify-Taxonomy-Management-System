from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import pandas as pd
from .models import (Product,CategoryAttribute,ClassificationBatch,)
from .classifier import classify_product as run_classifier



def clean_value(value):
  
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    value = str(value).strip()

    return value if value else None


def get_product_image_count(product):
  
    try:
        return product.image_count
    except Exception:
        images = [
            product.image_1,
            product.image_2,
            product.image_3,
            product.image_4,
            product.image_5,
        ]

        return len([
            image
            for image in images
            if image and str(image).strip()
        ])


def get_available_information_count(product):
    

    fields_to_check = [
        product.product_name,
        product.product_description,
        product.product_category,
        product.product_sub_category,
        product.brand,
        product.materials,
        product.product_color,
        product.bullets,
        product.set_includes,
    ]

    count = 0

    for value in fields_to_check:
        if value and str(value).strip():
            count += 1

    if get_product_image_count(product) > 0:
        count += 1

    return count


def normalize_confidence(score):

    if score is None:
        return None

    try:
        confidence = float(score)
    except (TypeError, ValueError):
        return None

    if 0 <= confidence <= 1:
        confidence *= 100

    confidence = min(
        max(confidence, 0.0),
        100.0
    )

    return round(confidence, 2)


def get_alternative_category_names(alternatives):
  

    names = []

    for alternative in alternatives or []:

        if not isinstance(alternative, dict):
            continue

        category = alternative.get("category")

        if category:
            full_path = getattr(
                category,
                "full_path",
                None
            )

            if full_path:
                names.append(str(full_path))

    return names


def set_classification_result(product,category,confidence,alternatives,detected_attributes,):
    """
    Save the classification result.

    Confidence is always stored as a percentage from 0 to 100.
    """


    if category:

        product.shopify_category = category.full_path

        product.shopify_category_id = category.shopify_id

    else:

        product.shopify_category = "Unclassified"
        product.shopify_category_id = None


    confidence = normalize_confidence(confidence)

    if confidence is None:

        product.confidence_score = None

        product.classification_status = (
            Product.STATUS_REVIEW
        )

        product.requires_manual_review = True

        product.manual_review_reason = (
            "Classifier did not return a confidence score."
        )

        product.classified_at = None

    else:

        available_information = (
            get_available_information_count(product)
        )

        if available_information <= 1:

            confidence = min(
                confidence,
                40.0
            )

        product.confidence_score = confidence

        if confidence < 60:

            product.classification_status = (
                Product.STATUS_REVIEW
            )

            product.requires_manual_review = True

            product.manual_review_reason = (
                "Classification confidence is below 60%."
            )

            product.classified_at = None

        else:

            product.classification_status = (
                Product.STATUS_CLASSIFIED
            )

            product.requires_manual_review = False

            product.manual_review_reason = None

            product.classified_at = timezone.now()


    alternative_names = (
        get_alternative_category_names(
            alternatives
        )
    )

    product.alternative_categories = (
        ", ".join(alternative_names)
        if alternative_names
        else None
    )


    try:

        import json

        product.detected_attributes = json.dumps(
            detected_attributes or [],
            ensure_ascii=False
        )

    except Exception:

        product.detected_attributes = None


    if confidence is not None:

        product.classification_evidence = (
            "Classification confidence: {:.2f}%".format(
                confidence
            )
        )

    else:

        product.classification_evidence = (
            "Classifier did not return a confidence score."
        )


    product.error_message = None

    product.save()

    return confidence

def save_taxonomy_attributes(product,detected_attributes):
   

    CategoryAttribute.objects.filter(product=product).delete()

    for attribute in detected_attributes or []:

        attribute_name = attribute.get(
            "attribute"
        )

        attribute_value = attribute.get(
            "value"
        )

        if not attribute_name or not attribute_value:
            continue

        CategoryAttribute.objects.create(

            product=product,

            attribute_id=attribute.get(
                "attribute_id"
            ),

            attribute_name=attribute_name,

            attribute_handle=attribute.get(
                "attribute_handle"
            ),

            value_id=attribute.get(
                "value_id"
            ),

            attribute_value=attribute_value,

            value_handle=attribute.get(
                "value_handle"
            ),

            confidence_score=90,

            approved=False,

            source="taxonomy"
        )


def save_basic_product_attributes(product):
   

    basic_attributes = [

        (
            "Material",
            product.materials,
            90
        ),

        (
            "Color",
            product.product_color,
            90
        ),

        (
            "Product Category",
            product.product_category,
            85
        ),

        (
            "Product Sub Category",
            product.product_sub_category,
            85
        ),

        (
            "Collection",
            product.collection_name,
            80
        ),

        (
            "Set",
            product.is_set,
            80
        ),

        (
            "Assembly Required",
            product.assembly_required,
            80
        ),

        (
            "Stackable",
            product.stackable,
            80
        ),

        (
            "Country Of Origin",
            product.country_of_origin,
            80
        ),
    ]

    for (
        attribute_name,
        attribute_value,
        confidence
    ) in basic_attributes:

        if not attribute_value:
            continue

        CategoryAttribute.objects.create(

            product=product,

            attribute_name=attribute_name,

            attribute_value=str(
                attribute_value
            ),

            confidence_score=confidence,

            approved=False,

            source="product_data"
        )


    image_count = get_product_image_count(
        product
    )

    if image_count > 0:

        CategoryAttribute.objects.create(

            product=product,

            attribute_name="Images Available",

            attribute_value=str(
                image_count
            ),

            confidence_score=100,

            approved=False,

            source="product_data"
        )


def save_all_product_attributes(product,detected_attributes):
    

    save_taxonomy_attributes(product,detected_attributes)

    save_basic_product_attributes(product)


def register_view(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            
            form.save()

            messages.success(request,"Registration successful. Please login.")

            
            return redirect("login")

    else:

        form = UserCreationForm()

    return render(request,"register.html",{"form": form})


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username","").strip()

        password = request.POST.get("password","")

        user = authenticate(request,username=username,password=password)

        if user is not None:

            login(request,user)

            return redirect("dashboard")

        return render(request,"login.html",{"error": "Invalid username or password."})

    return render(request,"login.html")


@login_required
def logout_view(request):

    logout(request)

    return redirect("login")

@login_required
def dashboard(request):

    total_products = Product.objects.count()

    classified_products = Product.objects.filter(classification_status=Product.STATUS_CLASSIFIED).count()

    pending_products = Product.objects.filter(classification_status=Product.STATUS_PENDING).count()

    review_products = Product.objects.filter(classification_status=Product.STATUS_REVIEW).count()

    approved_products = Product.objects.filter(classification_status=Product.STATUS_APPROVED).count()

    error_products = Product.objects.filter(classification_status=Product.STATUS_ERROR).count()

    return render(request,"dashboard.html",{"total_products": total_products,"classified_products": classified_products,"pending_products": pending_products,"approved_products": approved_products,"review_products": review_products,"error_products": error_products,})

@login_required
def product_list(request):

    search = request.GET.get("search","").strip()

    products = Product.objects.all().order_by("-id")


    if search:

        products = products.filter(

            Q(
                product_name__icontains=search
            )
            |
            Q(
                product_number__icontains=search
            )
            |
            Q(
                model_number__icontains=search
            )
            |
            Q(
                brand__icontains=search
            )
            |
            Q(
                product_category__icontains=search
            )
            |
            Q(
                product_sub_category__icontains=search
            )
        )


    paginator = Paginator(products,20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)


    return render(request,"products.html",{"products": page_obj,"page_obj": page_obj,"search": search,})


@login_required
def product_detail(request,product_id):

    product = get_object_or_404(Product,id=product_id)

    attributes = (CategoryAttribute.objects.filter(product=product).order_by("attribute_name"))

    return render(request,"product_detail.html",{"product": product,"attributes": attributes,})

def product_delete(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.delete()

    return redirect("products")

def product_update(request, product_id):

    product = get_object_or_404(Product,id=product_id)

    if request.method == "POST":

        product.product_number = request.POST.get("product_number","").strip()

        product.model_number = request.POST.get("model_number","").strip()

        product.product_name = request.POST.get("product_name","").strip()

        product.product_category = request.POST.get("product_category","").strip()

        product.product_sub_category = request.POST.get("product_sub_category","").strip()

        product.collection_name = request.POST.get("collection_name","").strip()

        product.color_collection = request.POST.get("color_collection","").strip()

        product.product_color = request.POST.get("product_color","").strip()

        product.product_description = request.POST.get("product_description","").strip()

        product.bullets = request.POST.get("bullets","").strip()

        product.set_includes = request.POST.get("set_includes","").strip()

        product.product_weight = request.POST.get("product_weight","").strip()

        product.materials = request.POST.get("materials","").strip()

        product.product_dimensions = request.POST.get("product_dimensions","").strip()

        product.assembly_required = request.POST.get("assembly_required","").strip()

        product.is_set = request.POST.get("is_set","").strip()

        product.stackable = request.POST.get("stackable","").strip()

        product.country_of_origin = request.POST.get("country_of_origin","").strip()

        product.item_cost = request.POST.get("item_cost","").strip()

        product.map_price = request.POST.get("map_price","").strip()

        product.msrp = request.POST.get("msrp","").strip()

        product.image_1 = request.POST.get("image_1","").strip()

        product.image_2 = request.POST.get("image_2","").strip()

        product.image_3 = request.POST.get("image_3","").strip()

        product.image_4 = request.POST.get("image_4","").strip()

        product.image_5 = request.POST.get("image_5","").strip()

        product.save()

        messages.success(request,"Product updated successfully.")

        return redirect("product_detail",product_id=product.id)

    return render(request,"product_update.html",{"product": product})

@login_required
def import_products(request):

    if request.method == "GET":

        return render(request,"upload_products.html")

    if request.method != "POST":

        return redirect("dashboard")

    excel_file = request.FILES.get("file")

    if not excel_file:

        return render(request,"upload_products.html",{"error": ("Please select an Excel file.")})

    imported = 0
    created = 0
    updated = 0
    skipped = 0
    errors = []

    try:

        df = pd.read_excel(
            excel_file,
            engine="openpyxl"
        )

    except Exception as e:

        return render(request,"upload_products.html",{"error": ("Unable to read Excel file: {}".format(str(e)))})

    if "Product Number" not in df.columns:

        return render(request,"upload_products.html",{"error": ("Excel file must contain " "'Product Number' column.")})

    for row_number, row in df.iterrows():

        try:

            product_number = clean_value(row.get("Product Number"))

            if not product_number:

                skipped += 1
                continue

            defaults = {

                "model_number":
                    clean_value(row.get("Model Number")),

                "brand":
                    clean_value(row.get("Brand")),

                "product_category":
                    clean_value(row.get("Product Category")),

                "product_sub_category":
                    clean_value(row.get("Product Sub Category")),

                "collection_name":
                    clean_value(row.get("Collection Name")),

                "color_collection":
                    clean_value(row.get("Color Collection")),

                "product_color":
                    clean_value(row.get("Product Color")),

                "product_name":
                    clean_value(row.get("Product Name")) or "Unknown Product",

                "product_description":
                    clean_value(row.get("Product Description")),

                "bullets":
                    clean_value(row.get("Bullets")),

                "set_includes":
                    clean_value(row.get("Set Includes")),

                "product_weight":
                    clean_value(
                        row.get("Product Weight")),

                "materials":
                    clean_value(row.get("Materials")),

                "product_dimensions":
                    clean_value(row.get("Product Dimensions")),

                "assembly_required":
                    clean_value(row.get("Assembly Required")),

                "is_set":
                    clean_value(row.get("Is a Set")),

                "stackable":
                    clean_value(row.get("Stackable")),

                "country_of_origin":
                    clean_value(row.get("Country Of Origin")),

                "item_cost":
                    clean_value(row.get("Item Cost")),

                "map_price":
                    clean_value(row.get("MAP")),

                "msrp":
                    clean_value(row.get("MSRP")),

                "image_1":
                    clean_value(row.get("Image 1")),

                "image_2":
                    clean_value(row.get("Image 2")),

                "image_3":
                    clean_value(row.get("Image 3")),

                "image_4":
                    clean_value(row.get("Image 4")),

                "image_5":
                    clean_value(row.get("Image 5")),
            }

            product, was_created = (Product.objects.update_or_create(product_number=product_number,defaults=defaults))
            product.classification_status = (Product.STATUS_PENDING)
            product.shopify_category = None
            product.shopify_category_id = None
            product.confidence_score = None
            product.alternative_categories = None
            product.requires_manual_review = False
            product.manual_review_reason = None
            product.error_message = None
            product.classified_at = None
            product.approved_at = None
            product.classification_evidence = None
            product.detected_attributes = None

            product.save()

            CategoryAttribute.objects.filter(product=product).delete()

            imported += 1

            if was_created:
                created += 1
            else:
                updated += 1

        except Exception as e:

            errors.append("Row {}: {}".format(row_number + 2,str(e)))

    return render(request,"upload_products.html",{"success": True,"imported": imported,"created": created,"updated": updated,"skipped": skipped,"errors": errors,})



@login_required
def batch_processing(request):

    batch_size = 500


    if request.method == "POST":

        products = list(Product.objects.filter(classification_status=Product.STATUS_PENDING).order_by("id")[:batch_size])

        if not products:

            messages.info(request,"There are no pending products to process.")

            return redirect("batch_processing")

        total_products = len(products)

        last_batch = (ClassificationBatch.objects.order_by("-id").first())

        if last_batch:

            try:

                last_number = int(
                    last_batch.batch_number.replace(
                        "BATCH-",
                        ""
                    )
                )

            except (ValueError,AttributeError):

                last_number = last_batch.id

            batch_number = ("BATCH-{:05d}".format(last_number + 1))

        else:

            batch_number = "BATCH-00001"

        batch = ClassificationBatch.objects.create(batch_number=batch_number,status=(ClassificationBatch.STATUS_PROCESSING),
            batch_size=batch_size,

            total_products=total_products,

            processed_products=0,

            successful_products=0,

            manual_review_products=0,

            failed_products=0,

            started_at=timezone.now()
        )


        for product in products:

            try:

                product.classification_status = (Product.STATUS_PROCESSING)

                product.classification_attempts += 1

                product.save(
                    update_fields=[
                        "classification_status",
                        "classification_attempts",
                        "updated_at",
                    ]
                )


                (
                    category,
                    score,
                    alternatives,
                    detected_attributes
                ) = run_classifier(
                    product
                )

                confidence = set_classification_result(

                    product=product,

                    category=category,

                    confidence=score,

                    alternatives=alternatives,

                    detected_attributes=(detected_attributes))

                save_all_product_attributes( product,detected_attributes)

                batch.processed_products += 1

                if confidence < 60:

                    batch.manual_review_products += 1

                else:

                    batch.successful_products += 1

                batch.save()

            except Exception as e:


                product.classification_status = (Product.STATUS_ERROR)

                product.error_message = str(e)

                product.requires_manual_review = True

                product.manual_review_reason = ("Classification failed during ""batch processing.")

                product.save()

                batch.failed_products += 1
                batch.processed_products += 1

                batch.save()


        if batch.failed_products == batch.total_products:

            batch.status = (ClassificationBatch.STATUS_FAILED)

            batch.error_message = ("All products failed classification.")

        else:

            batch.status = (ClassificationBatch.STATUS_COMPLETED)

        batch.completed_at = timezone.now()

        batch.save()

        messages.success(request,"{} products processed in {}.".format(batch.processed_products,batch.batch_number))

        return redirect("batch_processing")


    total_products = Product.objects.count()

    pending_products = Product.objects.filter(classification_status=Product.STATUS_PENDING).count()

    processing_products = Product.objects.filter(classification_status=Product.STATUS_PROCESSING).count()

    processed_products = (total_products - pending_products - processing_products)

    if total_products > 0:

        progress = int((processed_products / total_products) * 100)

    else:

        progress = 0

    progress = min(max(progress, 0),100)

    latest_batch = (ClassificationBatch.objects.order_by("-id").first())

    batches = (ClassificationBatch.objects.order_by("-created_at")[:20])

    return render(request,"batch_processing.html",{"total_products": total_products,"processed_products": processed_products,"remaining_products": (pending_products + processing_products),"pending_products": pending_products,"processing_products": processing_products,"batch_size": batch_size,"progress": progress,"latest_batch": latest_batch,"batches": batches,})



@login_required
def classify_product(request,product_id):

    product = get_object_or_404(Product,id=product_id)

    try:


        product.classification_attempts += 1

        product.classification_status = (
            Product.STATUS_PROCESSING
        )

        product.save()


        (
            category,
            score,
            alternatives,
            detected_attributes
        ) = run_classifier(
            product
        )


        confidence = set_classification_result(

            product=product,

            category=category,

            confidence=score,

            alternatives=alternatives,

            detected_attributes=(detected_attributes))


        save_all_product_attributes(product,detected_attributes)


        if confidence < 60:

            messages.warning(request,("Product classified with low confidence. ""Manual review required."))

        else:

            messages.success(request,"Product classified successfully.")

        return redirect("product_detail",product_id=product.id)

    except Exception as e:

        product.classification_status = (Product.STATUS_ERROR)

        product.error_message = str(e)

        product.requires_manual_review = True

        product.manual_review_reason = ("Classification failed.")

        product.save()

        messages.error(request,"Classification failed: {}".format(str(e)))

        return redirect("product_detail",product_id=product.id)

@login_required
def classification_results(request):

    status = request.GET.get("status","classified")

    search = request.GET.get("search","").strip()

    all_products = Product.objects.all()

    total = all_products.count()

    high_confidence = all_products.filter(confidence_score__gte=80).count()

    low_confidence = all_products.filter(
        Q(confidence_score__lt=60) |
        Q(confidence_score__isnull=True)).count()

    products = all_products.order_by("-confidence_score","-id")

    if status == "classified":

        products = products.filter(
            classification_status__in=[
                Product.STATUS_CLASSIFIED,
                Product.STATUS_APPROVED,
            ]
        )

    elif status == "review":

        products = products.filter(classification_status=Product.STATUS_REVIEW)

    elif status == "pending":

        products = products.filter(
            Q(
                classification_status=Product.STATUS_PENDING
            )
            |
            Q(
                classification_status__isnull=True
            )
            |
            Q(
                classification_status=""
            )
        )

    elif status == "error":

        products = products.filter(classification_status=Product.STATUS_ERROR)

    else:

        status = "classified"

        products = products.filter(
            classification_status__in=[
                Product.STATUS_CLASSIFIED,
                Product.STATUS_APPROVED,
            ]
        )

    if search:

        products = products.filter(
            Q(product_name__icontains=search)
            |
            Q(product_number__icontains=search)
            |
            Q(model_number__icontains=search)
        )

    paginator = Paginator(products,20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(request,"classification_results.html",{"products": page_obj,"page_obj": page_obj,"total": total,"high_confidence": high_confidence,"low_confidence": low_confidence,"status": status,"search": search,})

@login_required
def manual_review(request):

    products = (Product.objects.filter(requires_manual_review=True).order_by("confidence_score","id"))


    paginator = Paginator(products,20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(request,"manual_review.html",{"products": page_obj,"page_obj": page_obj,})

@login_required
@require_POST
def update_classification(request,product_id):

    product = get_object_or_404(Product,id=product_id)

    category = request.POST.get("shopify_category")

    if not category:

        messages.error(request,"Please provide a classification.")

        return redirect("product_detail",product_id=product.id)

    product.shopify_category = (category.strip())

    category_id = request.POST.get("shopify_category_id")

    if category_id:

        product.shopify_category_id = (category_id.strip())

    product.classification_status = (Product.STATUS_APPROVED)

    product.requires_manual_review = False

    product.manual_review_reason = None

    product.approved_at = timezone.now()

    product.error_message = None

    product.save()

    messages.success(request,"Classification updated successfully.")

    return redirect("product_detail",product_id=product.id)

@login_required
@require_POST
def approve_classification(request,product_id):

    product = get_object_or_404(Product,id=product_id)

    if not product.shopify_category:

        messages.error(request,"Cannot approve a product without a category.")

        return redirect("product_detail",product_id=product.id)

    product.classification_status = (Product.STATUS_APPROVED)

    product.requires_manual_review = False

    product.manual_review_reason = None

    product.approved_at = timezone.now()

    product.error_message = None

    product.save()

    messages.success(request,"Classification approved successfully.")

    return redirect("product_detail",product_id=product.id)
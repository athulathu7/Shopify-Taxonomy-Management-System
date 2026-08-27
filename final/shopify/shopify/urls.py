"""shopify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shopifyapp import views


urlpatterns = [

    path("admin/",admin.site.urls),

    path("register/",views.register_view,name="register"),

    path("",views.login_view,name="login"),

    path("logout/",views.logout_view,name="logout"),

    path( "dashboard/",views.dashboard,name="dashboard"),
    
    path( "products/",views.product_list, name="products"),

    path("product/<int:product_id>/",views.product_detail,name="product_detail"),

    path("product/<int:product_id>/update/",views.product_update,name="product_update"),

    path("products/<int:product_id>/delete/",views.product_delete, name="product_delete",),

    path( "upload/",views.import_products,name="upload_products"),

    path("batch/",views.batch_processing, name="batch_processing"),

    path("classify/<int:product_id>/",views.classify_product,name="classify_product"),
    
    path("classifications/",views.classification_results,name="classification_results"),

    path("manual-review/",views.manual_review,name="manual_review"),

    path("update/<int:product_id>/",views.update_classification,name="update_classification"),

    path("approve/<int:product_id>/",views.approve_classification,name="approve_classification"),

]
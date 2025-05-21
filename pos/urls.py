from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sale/create/', views.create_sale, name='create_sale'),
    path('sale/drafts/', views.saved_sales, name='saved_sales'),
    path('sale/history/', views.sales_history, name='sales_history'),
    path('sale/<int:sale_id>/edit/', views.edit_sale, name='edit_sale'),
    path('sale/<int:sale_id>/save/', views.save_sale, name='save_sale'),
    path('sale/<int:sale_id>', views.sale_detail, name='sale_detail'),
    path('sale/<int:sale_id>/add-item/', views.add_item, name='add_item'),
    path('sale/item/<int:item_id>/update-quantity/', views.update_quantity, name='update_quantity'),
    path('sale/item/<int:item_id>/remove/', views.remove_item, name='remove_item'),
    path('sale/<int:sale_id>/complete/', views.complete_sale, name='complete_sale'),
    path('sale/<int:sale_id>/cancel/', views.cancel_sale, name='cancel_sale'),
    path('login/', views.SalesPersonLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_salesperson, name='register'),
 
]

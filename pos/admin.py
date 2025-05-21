from django.contrib import admin
from .models import Product, Sale, SaleItem

# Register your models here.
admin.site.register(Product)

admin.site.site_header = "BusyMart POS"


class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('sale__salesperson', 'product')
    search_fields = ('sale__salesperson__username', 'product__name')
    ordering = ('sale',)
    raw_id_fields = ('sale', 'product')

    def subtotal(self, obj):
        return obj.quantity * obj.price
    subtotal.short_description = 'Subtotal'


class SaleItemInline(admin.StackedInline):
    model = SaleItem
    extra = 0


class SaleAdmin(admin.ModelAdmin):
    list_display = ('salesperson', 'date_created', 'status', 'total_amount')
    list_filter = ('salesperson', 'status')
    search_fields = ('salesperson__username',)
    ordering = ('-date_created',)
    raw_id_fields = ('salesperson',)

    inlines = [SaleItemInline]


# Register the models with their respective admin classes
admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem, SaleItemAdmin)

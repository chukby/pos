from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import SalesPersonRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Sale, SaleItem, Product
from django.db.models import Sum
from django.utils import timezone
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings


class SalesPersonLoginView(LoginView):
    template_name = 'pos/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_name'] = settings.STORE_NAME
        return context

def register_salesperson(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SalesPersonRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
            return render(request, 'pos/register.html', {'form': form})

    else:
        form = SalesPersonRegistrationForm()
    
    return render(request, 'pos/register.html', {'form': form})

@login_required
def dashboard(request):
    today = timezone.now().date()
    store_name = settings.STORE_NAME

     # Get all the sales by a particular salesperson from the database for today
    sales_today_sp = Sale.objects.filter(
        salesperson=request.user,
        date_created__date=today,
        status=Sale.COMPLETED
    )
    # Get all the sales by a particular salesperson from the database
    sp_sales = Sale.objects.filter(
        salesperson=request.user,
        status=Sale.COMPLETED
    )
     # Get all the sales from the database for today
    all_sales_today = Sale.objects.filter(
        date_created__date=today,
        status=Sale.COMPLETED,
    )

    # Get the total sales amount by the salesperson for today
    sales_today_sp_total = sales_today_sp.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # Get the total sales amount by the salesperson historically
    sales_total_sp  = sp_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    store_sales = Sale.objects.filter(status=Sale.COMPLETED)

    sales_total_store = store_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'sales_today_sp_count': sales_today_sp.count(),
        'sales_today_store_count': all_sales_today.count(),
        'sales_today_sp_total': sales_today_sp_total,
        'sales_total_sp' : sales_total_sp,
        
        'store_sales_count' : store_sales.count(),
        'sales_total_store' : sales_total_store,
        'recent_sales_sp': sp_sales.order_by('-date_created')[:10],
        'salesperson': request.user,
        'store_name': store_name,
    }
    return render(request, 'pos/dashboard.html', context)

@login_required
def create_sale(request):
    sale = Sale.objects.create(salesperson=request.user)
    sale.status = Sale.DRAFT
    sale.save()
    # messages.success(request, 'Sale created successfully.')
    # Redirect to the edit sale page
    # where the user can add items to the sale                  
    return redirect('edit_sale', sale_id=sale.id)

@login_required
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
    products = Product.objects.filter(stock__gt=0)
    return render(request, 'pos/edit_sale.html', {'sale': sale, 'products': products})

def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
    products = Product.objects.all()
    return render(request, 'pos/sale_detail.html', {'sale': sale, 'products': products})

@login_required
def add_item(request, sale_id):
    if request.method == 'POST':
        sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Create the sale item
        SaleItem.objects.create(
            sale=sale,
            product=product,
            price=product.price
        )
        sale.update_total()
        
        # Render the updated sales items table
        context = {'sale': sale}
        table_html = render_to_string('pos/partials/sale_items_table.html', context, request)
        return HttpResponse(table_html)
    
    return HttpResponse(status=400)

@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(SaleItem, id=item_id, sale__salesperson=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
            item.sale.update_total()
            
            # Render the updated sales items table
            context = {'sale': item.sale}
            table_html = render_to_string('pos/partials/sale_items_table.html', context, request)
            return HttpResponse(table_html)
    return HttpResponse(status=400)

@login_required
def remove_item(request, item_id):
    if request.method == 'DELETE':
        item = get_object_or_404(SaleItem, id=item_id, sale__salesperson=request.user)
        sale = item.sale
        item.delete()
        sale.update_total()
        
        # Render the updated sales items table
        context = {'sale': sale}
        table_html = render_to_string('pos/partials/sale_items_table.html', context, request)
        return HttpResponse(table_html)
    return HttpResponse(status=400)

# @login_required
# def complete_sale(request, sale_id):
#     sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
#     sale.status = Sale.COMPLETED
#     sale.save()
#     return redirect('dashboard')

@login_required
def cancel_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
    sale.status = Sale.CANCELLED
    sale.save()
    
    return redirect('dashboard')

@login_required
def complete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
    if sale.status != Sale.COMPLETED:
        for item in sale.items.all():
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()
            else:
                # messages.error(request, f"Not enough stock for {item.product.name}.")
                HttpResponse(f"Not enough stock for {item.product.name}.")
                return redirect('edit_sale', sale_id=sale.id)
        sale.status = Sale.COMPLETED
        sale.save()
        # messages.success(request, 'Sale completed successfully.')
        HttpResponse("Sale completed successfully.")
    return redirect('dashboard')


@login_required
def save_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, salesperson=request.user)
    if sale.status == Sale.DRAFT:
        # messages.info(request, 'Sale is already saved.')
        return redirect('dashboard')
    else:
        sale.status = Sale.DRAFT
        sale.save()
        # messages.success(request, 'Sale has been saved temporarily.')
        return redirect('dashboard')

@login_required
def saved_sales(request):
    saved_sales = Sale.objects.filter(
        salesperson=request.user,
        status=Sale.DRAFT
    )
    context = {
        'saved_sales': saved_sales.order_by('-date_created')
    }
    return render(request, 'pos/saved_sale.html', context)


@login_required
def sales_history(request):
    cashier_sales = Sale.objects.filter(
        salesperson=request.user, status=Sale.COMPLETED
    )

    context = {
       "cashier_sales_history" : cashier_sales.order_by('-date_created')
    }
    return render(request, 'pos/sales_history.html', context)

from django.shortcuts import render ,redirect
from mystore.models  import MyUser
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .models import Product,Cart,Order,Order
from django.utils import timezone



# Create your views here.

def index(request):
    return render(request,'index.html',{})

def login(request):
    return render(request,'login.html')

def signin(request):
    return render(request,'signin.html')


def admin_dashboard(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    users = MyUser.objects.all().count()
    orders = Order.objects.all().count
    products_count = Product.objects.all().count()
    products = Product.objects.all()
    tickets = SupportTicket.objects.all()
    context = {
        'users': users,
        'total_users': MyUser.objects.count(),
        'orders' : orders,
        'products_count':products_count,
        'tickets':tickets
     }

    return render(request,'admin.html',context)

def support_dashboard(request):
    if request.session.get('role') != 'support':
        return redirect('login')
    return render(request,'support.html')

def logout(request):
    request.session.flush()
    return redirect('login')

def inser_details(request):
    if request.method == 'POST':
        print("it is working")
        user_name = request.POST['user_name']
        user_email = request.POST['user_email']
        user_number = request.POST['user_number']
        user_password = request.POST['user_password']
        print(user_name,user_email,user_number,user_password)
        hashed_password = make_password(user_password)
        store = MyUser()
        store.user_name = user_name
        store.user_email = user_email
        store.user_number = user_number
        store.user_password = hashed_password
        store.save()
        print("SAVED SUCCESS FULLY")
    return render(request,'login.html')

def check_email(request):
    hashed_password = make_password("support")
    print(hashed_password)
    email = request.POST.get('email')
    exists = MyUser.objects.filter(user_email=email).exists()
    return JsonResponse({'exists': exists})



def password_check(request):
    email = request.POST.get('email')
    password = request.POST.get('verify')
    print("xxxxxx")
    try:
        
        user = MyUser.objects.get(user_email=email)
        print(user.user_password)
    
        if check_password(password, user.user_password):
            return JsonResponse({"exists": True})
        else:
            return JsonResponse({"exists": False}) 

    except MyUser.DoesNotExist:
        
        return JsonResponse({"exists": False})


def login_user(request):
    if request.method == 'POST':
        print("it's working")
        name = request.POST['user_name']
        password = request .POST['user_password']
        print(name,password)
        try:
            user = MyUser.objects.get(user_email=name)
            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.user_name
            request.session['user_email'] = user.user_email
            request.session['role'] = user.role
            if check_password(password, user.user_password):
                print(user.role)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'support':
                    return redirect('support_dashboard')
                elif user.role == 'client':
                    return redirect('client_profile')
                else:
                    return redirect('/')
        except MyUser.DoesNotExist:
            print("i alredy told this happend")
            messages.error(request, " Invalid username or password")
            return redirect('login_page')
    
    return render(request, 'login.html')


def product_management(request):
    products = Product.objects.all().order_by('-id')  # show latest first
    return render(request, 'product_management.html', {'products': products})


def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('product_name')
        price = request.POST.get('product_price')
        stock = request.POST.get('product_stock')
        category = request.POST.get('product_category')
        description = request.POST.get('product_description')
        image = request.FILES.get('product_image')

        product = Product.objects.create(
            product_name=name,
            product_price=price,
            product_stock=stock,
            product_category=category,
            product_description=description,
            product_image=image
        )

        return JsonResponse({
            'product_id': product.id,
            'product_name': product.product_name,
            'product_price': product.product_price,
            'product_stock': product.product_stock,
            'product_image': product.product_image.url if product.product_image else ''
        })
    




def product_view(request):
    filter_type = request.GET.get('category', 'all')
    if filter_type == 'tv':
        products = Product.objects.filter(product_category__icontains='tv')
    elif filter_type == 'soundbar':
        products = Product.objects.filter(product_category__icontains='soundbar')
    else:
        products = Product.objects.all()

    return render(request, 'product.html', {'products': products, 'selected_filter': filter_type})




def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        data = {
            'product_name': product.product_name,
            'product_price': product.product_price,
            'product_description': product.product_description,
            'product_stock': product.product_stock,
            'product_image': product.product_image.url if product.product_image else '',
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Login required'}, status=401)

        user = MyUser.objects.get(user_id=user_id)
        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
        
        if not created:
            # If already exists, increment quantity
            cart_item.quantity += 1
            cart_item.save() 
        return JsonResponse({'message': f'{product.product_name} added to cart!'})



def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to buy the product.")
        return redirect('login_page')

    user = MyUser.objects.get(user_id=user_id)

    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        payment_method = request.POST.get('payment_method', 'Not Paid')
        address = request.POST.get('address')

        total_price = quantity * product.product_price

        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total_price,
            payment_method=payment_method,
            address = address
        )

        messages.success(request, f"Order placed successfully! Warranty Number: {order.warranty_number}")
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'buy_product.html', {'product': product})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})



from .models import Product,Cart,Order,SupportTicket

def client_profile(request):
    user_email = request.session.get('user_email')
    user_profile = MyUser.objects.get(user_email = user_email)
    cart_items = Cart.objects.filter(user = user_profile.user_id)
    print(user_profile.user_id)
    print("sample")
    orders = Order.objects.filter(user = user_profile.user_id)
    return render(request,'profile.html',{'user_profile':user_profile,'cart_items':cart_items,'orders':orders})


def verify_warranty(request):
    warranty_number = request.GET.get('warranty_number')
    try:
        order = Order.objects.get(warranty_number=warranty_number)
        # Check if still valid
        if order.warranty_end and order.warranty_end > timezone.now():
            return JsonResponse({
                'valid': True,
                'product_name': order.product.product_name,
                'user_id': order.user.user_id
            })
        else:
            return JsonResponse({'valid': False})
    except Order.DoesNotExist:
        return JsonResponse({'valid': False})
    


def create_ticket(request):
    if request.method == "POST":
        warranty_number = request.POST.get("warranty_number")
        issue = request.POST.get("issue")

        try:
            # Find the order linked to this warranty number
            order = Order.objects.select_related("user", "product").get(warranty_number=warranty_number)

            # Create the ticket linked to user and product
            ticket = SupportTicket.objects.create(
                user=order.user,
                product=order.product,
                issue=issue,
                status="open",
            )

            return JsonResponse({
                "success": True,
                "message": "Ticket created successfully!",
                "ticket_id": ticket.id,
                "product": ticket.product.product_name,
                "user": ticket.user.user_email
            })

        except Order.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid warranty number."})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method."})
    

from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.models import User

def user_management(request):
    users = MyUser.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    orders = orders = Order.objects.all()
    top_users = MyUser.objects.all().order_by('-user_id')[:5]

    context = {
        'users': page_obj,
        'total_users': MyUser.objects.count(),
        'top_users': top_users,
        'orders' : orders
    }
    return render(request, 'user_management.html', context)

def admin_orders(request):
    orders = Order.objects.all()
    print(orders)
    return render(request,'admin_orders.html',{"orders":orders})


# def ticket(request):
    # ticket = SupportTicket.objects.all()
    
    # staff =  MyUser.objects.get(role='support')
    # print(staff.user_name)
    # return render(request,'ticket.html',{'tickets':ticket},{'staff':staff})
# def ticket(request):
#     tickets = SupportTicket.objects.all()
#     staff_list = MyUser.objects.filter(role='support')

#     context = {
#         'tickets': tickets,
#         'staff_list': staff_list
#     }
#     return render(request, "ticket.html", context)


from django.http import JsonResponse

def assign_staff(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        staff_name = request.POST.get("staff_name")

        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            ticket.assigned_staff = staff_name
            ticket.save()

            return JsonResponse({"status": "success"})
        except SupportTicket.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "Ticket not found"})

    return JsonResponse({"status": "error", "msg": "Invalid request"})

def ticket(request):
    status = request.GET.get("status")

    if status:
        tickets = SupportTicket.objects.filter(status=status)
    else:
        tickets = SupportTicket.objects.all()

    staff_list = MyUser.objects.filter(role='support')

    context = {
        'tickets': tickets,
        'staff_list': staff_list,
        'selected_status': status
    }
    return render(request, "ticket.html", context)

def ticket_details(request):
    ticket_id = request.GET.get("ticket_id")

    try:
        ticket = SupportTicket.objects.get(id=ticket_id)

        data = {
            "id": ticket.id,
            "user": ticket.user.user_name,
            "product": ticket.product.product_name,
            "issue": ticket.issue,
            "status": ticket.status,
            "assigned_staff": ticket.assigned_staff,
            "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": ticket.updated_at.strftime("%Y-%m-%d %H:%M"),
        }

        return JsonResponse({"status": "success", "data": data})

    except SupportTicket.DoesNotExist:
        return JsonResponse({"status": "error"})

from django.http import JsonResponse

def update_ticket_status(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        new_status = request.POST.get("status")

        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            ticket.status = new_status
            ticket.save()

            return JsonResponse({"status": "success"})
        except SupportTicket.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "Ticket not found"})

    return JsonResponse({"status": "error", "msg": "Invalid request"})


def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()

            return JsonResponse({"status": "success"})
        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "Order not found"})

    return JsonResponse({"status": "error", "msg": "Invalid request"})


def support_dashboard(request):
    if request.session.get('role') != 'support':
        return redirect('login')

    orders = Order.objects.all()
    tickets = SupportTicket.objects.all()

    context = {
        "orders": orders,
        "tickets": tickets
    }
    return render(request, 'support.html', context)




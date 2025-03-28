from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Books, Order, OrderItem
from .forms import BookForm


@login_required(login_url='login')
def edit_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})


@login_required(login_url='login')
def delete_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return redirect('book_list')


@login_required(login_url='login')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})


def book_list(request):
    books = Books.objects.all()

    book_name = request.GET.get('book_name', '').strip()
    author = request.GET.get('author', '').strip()
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()

    if book_name:
        books = books.filter(book_name__icontains=book_name)
    if author:
        books = books.filter(author_book__icontains=author)
    if price_min:
        try:
            price_min = float(price_min)
            books = books.filter(book_price__gte=price_min)
        except ValueError:
            pass
    if price_max:
        try:
            price_max = float(price_max)
            books = books.filter(book_price__lte=price_max)
        except ValueError:
            pass
    paginator = Paginator(books, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/books_list.html', {
        'books': page_obj,
        'book_name': book_name,
        'author': author,
        'price_min': price_min,
        'price_max': price_max,
    })


def add_to_cart(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    if 'cart' not in request.session:
        request.session['cart'] = {}
    cart = request.session['cart']
    if str(book_id) in cart:
        cart[str(book_id)]['quantity'] += 1
    else:
        cart[str(book_id)] = {
            'quantity': 1,
            'price': str(book.book_price),
            'name': book.book_name,
        }
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('book_list')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_cost = 0
    for book_id, item in cart.items():
        item_total = float(item['price']) * item['quantity']
        cart_items.append({
            'book_id': book_id,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': float(item['price']),
            'total_price': item_total,
        })
        total_cost += item_total
    return render(request, 'books/cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost,
    })


def remove_from_cart(request, book_id):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    cart = request.session['cart']
    book_id_str = str(book_id)
    if book_id_str in cart:
        del cart[book_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')


@login_required(login_url='login')
def create_order(request):
    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    total_cost = 0
    for item in cart.values():
        total_cost += float(item['price']) * item['quantity']

    order = Order.objects.create(
        user=request.user,
        total_cost=total_cost,
    )

    for book_id, item in cart.items():
        OrderItem.objects.create(
            order=order,
            book_name=item['name'],
            quantity=item['quantity'],
            price=item['price'],
        )

    request.session['cart'] = {}
    request.session.modified = True
    return redirect('orders')


@login_required(login_url='login')
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'books/orders.html', {'orders': orders})


@login_required(login_url='login')
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ успешно удалён!')
        next_url = request.GET.get('next', 'orders')
        return redirect(next_url)
    return redirect('orders')

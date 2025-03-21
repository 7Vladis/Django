from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    paginator = Paginator(books, 5)
    page = request.GET.get('page')
    try:
        books_page = paginator.get_page(page)
    except PageNotAnInteger:
        books_page = paginator.page(1)
    except EmptyPage:
        books_page = paginator.page(paginator.num_pages)
    return render(request, 'books/books_list.html', {'books': books_page})


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

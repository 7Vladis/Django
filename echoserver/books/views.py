from pydoc import pager

from django.contrib.admin.templatetags.admin_list import pagination
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from .models import Books
from .forms import BookForm


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

def delete_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return redirect('book_list')

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form':form})

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
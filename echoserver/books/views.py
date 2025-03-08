from django.shortcuts import render, get_object_or_404, redirect
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

def book_list(request):
    books = Books.objects.all()
    return render(request, 'books/books_list.html', {'books': books})
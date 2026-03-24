from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Expense, Category
from .forms import ExpenseForm
from datetime import date
import json


def expense_list(request):
    # --- Month filter ---
    month = request.GET.get('month')  # e.g. "2026-03"
    if month:
        year, mon = month.split('-')
        expenses = Expense.objects.filter(
            date__year=year, date__month=mon
        ).order_by('-date')
    else:
        expenses = Expense.objects.all().order_by('-date')

    # --- Stats ---
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    highest = expenses.order_by('-amount').first()
    count = expenses.count()

    # --- Pie Chart: spending by category ---
    category_data = (
        expenses.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    pie_labels = [item['category__name'] or 'Uncategorized' for item in category_data]
    pie_values = [float(item['total']) for item in category_data]

    # --- Bar Chart: monthly spending (last 6 months) ---
    from django.db.models.functions import TruncMonth
    monthly_data = (
        Expense.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )[:6]

    bar_labels = [item['month'].strftime('%b %Y') for item in monthly_data]
    bar_values = [float(item['total']) for item in monthly_data]

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'total': total,
        'highest': highest,
        'count': count,
        'pie_labels': json.dumps(pie_labels),
        'pie_values': json.dumps(pie_values),
        'bar_labels': json.dumps(bar_labels),
        'bar_values': json.dumps(bar_values),
        'selected_month': month or '',
    })


def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('expense_list')


def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'edit': True,
        'expense': expense
    })
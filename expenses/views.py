from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import TruncYear, TruncMonth
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort')

        if sort == 'category':
            queryset = queryset.order_by('category__name')
        elif sort == 'category_desc':
            queryset = queryset.order_by('-category__name')
        elif sort == 'date':
            queryset = queryset.order_by('date')
        elif sort == 'date_desc':
            queryset = queryset.order_by('-date')

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            start_date_str = form.cleaned_data.get('start_date', '').strip()
            end_date_str = form.cleaned_data.get('end_date', '').strip()
            categories = form.cleaned_data.get('categories')

            if name:
                queryset = queryset.filter(name__icontains=name)
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                queryset = queryset.filter(date__range=(start_date, end_date))
            elif start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                queryset = queryset.filter(date__gte=start_date)
            elif end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                queryset = queryset.filter(date__lte=end_date)
            elif categories:
                queryset = queryset.filter(category__in=categories)

        total_amount = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

        summary_per_month = (
            queryset.annotate(year=TruncYear('date'), month=TruncMonth('date'))
            .values('year', 'month')
            .annotate(total=Sum('amount'))
            .order_by('-year', '-month')
        )

        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            total_amount=total_amount,
            summary_per_month=summary_per_month,
            **kwargs)


class CategoryListView(ListView):
    model = Category
    paginate_by = 5

from django import forms
from .models import Expense


class ExpenseSearchForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

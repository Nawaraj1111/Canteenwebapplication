from django import forms
from .models import Order, Customer, Product, Review
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime, AdminTimeWidget

payment_method = [
    ('Khalti', 'Khalti'),
    ('Pay with Cash', 'pay with Cash'),
]


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by",
                  "mobile", "email", "payment_method"]

        widgets = {
            "ordered_by": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dish orderer name "
            }),
            "mobile": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your phone number ",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email address "
            }),



        }

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError(
                "Customer with this username already exists.")
        return uname

    def clean_email(self):
        uemail = self.cleaned_data.get("email")
        if User.objects.filter(email=uemail).exists():
            raise forms.ValidationError(
                "Email already exists"
            )
        return uemail


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class ProductForm(forms.ModelForm):
    more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
        "class": "form-control",
        "multiple": True
    }))

    class Meta:
        model = Product
        fields = ["title", "slug", "category", "image", "normal_price",
                  "offer_price", "description", "carbohydrate", "protein", "fats", "other_energy"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the product title here..."
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the unique slug here..."
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "normal_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Marked price of the product..."
            }),
            "offer_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Selling price of the product..."
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Description of the product...",
                "rows": 5
            }),
            "carbohydrate": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter carbohydate calories"
            }),
            "Protein": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Protein calories"
            }),
            "fats": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Protein calories"
            }),
            "other_energy": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter other energy calories"
            }),
        }


class PasswordForgotForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your registered email address.."
    }))

    def clean_email(self):
        e = self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError(
                "Customer with this account does not exists..")
        return e


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Enter New Password',
    }), label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Confirm New Password',
    }), label="Confirm New Password")

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            raise forms.ValidationError(
                "New Passwords did not match!")
        return confirm_new_password

class ReviewForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder':  "Dish review here....",
        'class': 'md-textarea form-control',
        'row': '4',
        'height': "h-25"
    }))

    class Meta:
        model = Review
        fields = ("comment",)
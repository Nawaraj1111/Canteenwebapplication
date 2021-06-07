from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
import requests
from django.db import connection
from django.views.decorators.csrf import ensure_csrf_cookie


class CollegekhajagharsMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(CollegekhajagharsMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context


class AllProductsView(CollegekhajagharsMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context


class AllReview(TemplateView):
    template_name = "testing.html"

    def get_context_data(self, allreviews=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allreviews'] = Review.objects.get(slug=id)
        for i in allreviews:
            print(i)
        return context


class ProductDetailView(CollegekhajagharsMixin, TemplateView):
    template_name = "productdetail.html"
    form = ReviewForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        print(url_slug)
        product = Product.objects.get(slug=url_slug)
        print(product)
        reviews=Review.objects.prefetch_related('product_set').get
        reviews = Review.objects.all()
        reviews_count = Review.objects.all().count()
        product.view_count += 1
        product.save()
        context.update(
            {
                'product': product,
                'form': self.form,
                'reviews': reviews,
                'reviews_count': reviews_count,
            }
        )
        # context['product'] = product
        # context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST)
        if form.is_valid():
            url_slug = self.kwargs['slug']
            form.instance.product = Product.objects.get(slug=url_slug)
            form.instance.user = request.user
            form.save()
            return redirect("collegekhajaghar:productdetail", slug=url_slug)
            # return redirect(reverse("collegekhajaghar:productdetail", kwargs={
            #     product.slug
            # }))


class AddToCartView(CollegekhajagharsMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['dish_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.offer_price
                cartproduct.save()
                cart_obj.total += product_obj.offer_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.offer_price, quantity=1,
                    subtotal=product_obj.offer_price)
                cart_obj.total += product_obj.offer_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.offer_price, quantity=1,
                subtotal=product_obj.offer_price)
            cart_obj.total += product_obj.offer_price
            cart_obj.save()
        return context


class ManageCartView(CollegekhajagharsMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("collegekhajaghar:mycart")


class EmptyCartView(CollegekhajagharsMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("collegekhajaghar:mycart")


class MyCartView(CollegekhajagharsMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class CheckoutView(CollegekhajagharsMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("collegekhajaghar:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Pending"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                return redirect(reverse("collegekhajaghar:khaltirequest") + "?o_id=" + str(order.id))
        else:
            return redirect("collegekhajaghar:home")
        return super().form_valid(form)


class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "khaltirequest.html", context)


class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "Key test_secret_key_ce5f025f7f624d3194b9ba80ca6d6e1b"
        }

        order_obj = Order.objects.get(id=o_id)

        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False
        data = {
            "success": success
        }
        return JsonResponse(data)

# Customer Registration page
class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("collegekhajaghar:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("collegekhajaghar:home")


# login view of customer page
class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("collegekhajaghar:home")

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class AboutView(CollegekhajagharsMixin, TemplateView):
    template_name = "about.html"


class ContactView(CollegekhajagharsMixin, TemplateView):
    template_name = "contactus.html"


# class DashboardView(TemplateView):
#     template_name = "customerdashboard.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context["data"] = "Hello I am templates"
#         cursor = connection.cursor()
#         cursor.execute("select * from collegekhajagharapp_customer ")
#         r = cursor.fetchall()
#         context["list"] = r
#         print(context)
#         return context

def DashboardView(request):
    cursor = connection.cursor()
    cursor.execute("select count(username) from auth_user ")
    r = cursor.fetchone()
    print(r)
    return render(request, 'adminpages/admindashboard.html')


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class CustomerOrderView(TemplateView):
    template_name = "customerorder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer']: customer
        print(customer)
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            print(order_id)
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("collegekhajaghar:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw))
        if not results:
            context["results"] = results
        else:
            context["results"] = results
        return context


class PasswordForgotView(FormView):
    template_name = "forgetpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Reset your password following this link: '
        html_content = url + "/password-reset/" + email + \
                       "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'CollegeKhajaghar Password Reset',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("collegekhajaghar:passwordforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)


# admin pages
class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = CkgStaffLoginForm
    success_url = reverse_lazy("collegekhajaghar:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(
            order_status="Order Received").order_by("-id")
        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.all().order_by("-id")
        return context


class AdminOrderStatuChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("collegekhajaghar:adminorderdetail", kwargs={"pk": order_id}))


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"


class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("collegekhajaghar:adminproductlist")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)

#
# def detail(request, id):
#     product = Product.objects.get(id=id) # select * from Product where id=id
#     reviews = Review.objects.filter(product=id).order_by("-comment")
#     average = reviews.aggregate(Avg("rating"))["rating__avg"]
#     if average == None:
#         average = 0
#     average = round(average, 2)
#     context = {
#         "Product": product,
#         "reviews": reviews,
#         "average": average
#     }
#     return render(request, 'productdetail.html', context)
#

# @ensure_csrf_cookie
# def add_review(request, id):
#     if request.user.is_authenticated:
#         product = Product.objects.get(id=id)
#         context = {'allreviews': allreviews}
#         print(context)
#         if request.method == "POST":
#             form = ReviewForm(request.POST or None)
#             if form.is_valid():
#                 data = form.save(commit=False)
#                 data.comment = request.POST["comment"]
#                 data.user = request.user
#                 data.product = product
#                 data.save()
#                 return redirect("collegekhajaghar:customerlogin")
#         else:
#             form = ReviewForm()
#         return render(request, 'reviews.html', slug, context)
#     else:
#         return redirect("collegekhajaghar:customerlogin")

# def show_review(request, slug):
#     if request.method == "GET":
#         allreviews = Review.objects.all().get(slug=slug).order_by("-id")
#         context = {'allreviews': allreviews}
#     return render(request, 'testing.html', context, slug)


# # def add_review(request, id):
# #     if request.user.is_authenticated:
# #         product = Product.objects.get(id=id)
# #         if request.method == "POST":
# #             form = ReviewForm(request.POST or None)
# #             if form.is_valid():
# #                 data = form.save(commit=False)
# #                 data.comment = request.POST["comment"]
# #                 data.rating = request.POST["rating"]
# #                 data.user = request.user
# #                 data.product = product
# #                 data.save()
# #                 return redirect("collegekhajaghar:productdetail", id)
# #         else:
# #             form = ReviewForm()
# #         return render(request, 'productdetail.html', {"form": form})
# #     else:
# #         return redirect("collegekhajaghar:customerlogin")

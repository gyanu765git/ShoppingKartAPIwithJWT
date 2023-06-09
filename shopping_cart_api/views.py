from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Product, Cart, CartItem
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login,authenticate,logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, AnonymousUser
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


# write views here...

class ProductsView(APIView):
    
    permission_classes =[AllowAny]
    
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CategoryView(APIView):
    
    permission_classes =[AllowAny]
    
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class GetProductByCategoryView(APIView):
    
    permission_classes =[AllowAny]
     
    def get(self, request, category_id, format=None):
        queryset = Product.objects.filter(category_id=category_id)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    

class CartView(APIView):
    
    permission_classes =[AllowAny]
     
    def get(self, request):
        user = request.user
        cart_data = []

        if isinstance(user, AnonymousUser):
            # Guest user
            cart_data = request.session.get('cart', [])
        else:
            # Authenticated user
            guest_cart = request.session.pop('cart', {})

            cart = Cart.objects.filter(user=user).first()

            if cart:
                for guest_item in guest_cart.values():
                    guest_product_id = guest_item['id']
                    guest_quantity = guest_item['quantity']
                    cart_item = cart.cart_items.filter(product_id=guest_product_id).first()
                    if cart_item:
                        cart_item.quantity += guest_quantity
                        cart_item.save()
                    else:
                        guest_product = Product.objects.filter(pk=guest_product_id).first()
                        if guest_product:
                            cart_item = CartItem.objects.create(
                                cart=cart,
                                product=guest_product,
                                quantity=guest_quantity,
                            )
                            cart_item.save()

                for cart_item in cart.cart_items.all():
                    cart_data.append({
                        'id': cart_item.product.id,
                        'name': cart_item.product.name,
                        'img': cart_item.product.img.url,
                        'desc': cart_item.product.desc,
                        'quantity': cart_item.quantity,
                    })
            else:
                cart, created = Cart.objects.get_or_create(user=user)
                for guest_item in guest_cart.values():
                    guest_product_id = guest_item['id']
                    guest_quantity = guest_item['quantity']
                    guest_product = Product.objects.filter(pk=guest_product_id).first()
                    if guest_product:
                        cart_item = CartItem.objects.create(
                            cart=cart,
                            product=guest_product,
                            quantity=guest_quantity,
                        )
                        cart_item.save()
                        cart_data.append({
                            'id': guest_product.id,
                            'name': guest_product.name,
                            'img': guest_product.img.url,
                            'desc': guest_product.desc,
                            'quantity': guest_quantity,
                        })

        return Response(cart_data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'message': 'Product ID is required.'}, status=400)

        product = Product.objects.filter(pk=product_id).first()
        if not product:
            return Response({'message': 'Product not found.'}, status=404)

        user = request.user
        if isinstance(user, AnonymousUser):
            # Guest user
            cart = request.session.get('cart', {})
            cart_item = cart.get(str(product_id))
            if cart_item:
                cart_item['quantity'] += 1
            else:
                cart[str(product_id)] = {
                    'id': product.id,
                    'name': product.name,
                    'img': product.img.url,
                    'desc': product.desc,
                    'quantity': 1,
                }
            request.session['cart'] = cart
            return Response({'message': 'Product added to cart.'}, status=201)

        else:
            # Authenticated user
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                cart = Cart.objects.create(user=user)

            cart_item = cart.cart_items.filter(product=product).first()
            if cart_item:
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

            return Response({'message': 'Product added to cart.'}, status=201)
           
    def delete(self, request, pk=None):
        user = request.user
        if not isinstance(user, AnonymousUser):
            # Authenticated user
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return Response({'message': 'Cart not found.'}, status=404)

            cart_item = cart.cart_items.filter(product_id=pk).first()
            if cart_item:
                cart_item.delete()
                return Response({'message': 'Product removed from cart.'}, status=204)
            else:
                return Response({'message': 'Product not found in cart.'}, status=404)
        else:
            # Guest user
            cart = request.session.get('cart', {})
            if str(pk) in cart:
                del cart[str(pk)]
                request.session['cart'] = cart
                return Response({'message': 'Product removed from cart.'}, status=204)
            else:
                return Response({'message': 'Product not found in cart.'}, status=404)


class SignUpView(APIView):
    def post(self, request, format=None):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.create_user(email=email, username=username, password=password)
        login(request,user)
        refresh = RefreshToken.for_user(user)

        response_data = {
            'message': 'User is created',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            },
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }
        return Response(response_data)

class LoginView(APIView):
    def post(self,request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        login(request,user)
        return Response({"message":"you are logged in"})

class LogoutView(APIView):
    def post(self,request):
        logout(request) 
        return Response({"message":"you are logout"})     
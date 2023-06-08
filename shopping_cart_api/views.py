from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login,authenticate,logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets

# write views here...

class ProductsView(APIView):
    
    permission_classes =[IsAuthenticated]
    
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CategoryView(APIView):
    
    permission_classes =[IsAuthenticated]
    
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class GetProductByCategoryView(APIView):
    
    permission_classes =[IsAuthenticated]
     
    def get(self, request, category_id, format=None):
        queryset = Product.objects.filter(category_id=category_id)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    
class CartView(APIView):
    
    permission_classes =[IsAuthenticated]
     
    def get(self, request):
        cart = request.session.get('cart', {})
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart_data = []
        for product in products:
            cart_item = {
                'id': cart[str(product.id)]['id'],
                'name': cart[str(product.id)]['name'],
                'img': cart[str(product.id)]['img'],
                'desc': cart[str(product.id)]['desc'],
                'quantity': cart[str(product.id)]['quantity']
            }
            cart_data.append(cart_item)
        
        return Response(cart_data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'message': 'Product ID is required.'}, status=400)

        product = Product.objects.filter(pk=product_id).first()
        if not product:
            return Response({'message': 'Product not found.'}, status=404)

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
                'price': product.price,
                'quantity': 1,
            }
        request.session['cart'] = cart
        return Response({'message': 'Product added to cart.'}, status=201)

    def delete(self, request, pk=None):
        cart = request.session.get('cart', {})
        if str(pk) in cart:
            del cart[str(pk)]
            request.session['cart'] = cart
            return Response({'message': 'Product removed from cart.'}, status=204)
        return Response({'message': 'Product not found in cart.'}, status=404)

class SignUpView(APIView):
    def post(self, request, format=None):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.create_user(email=email, username=username, password=password)

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
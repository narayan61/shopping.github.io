from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import *
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

def home(request):

 topwears=Product.objects.filter(category='TW')
 mobiles=Product.objects.filter(category='M')
 bottomwears=Product.objects.filter(category='BW')

 if request.method=="POST":
   search_item=request.POST.get('search')
   search2=Product.objects.filter(Q(title=search_item)|Q(category=search_item)|Q(brand=search_item))
   print(search2 )
   print("hiiigggiii")
   return render(request, 'app/home.html',{'topwears':topwears,'mobiles':mobiles,'bottomwears':bottomwears,'search2':search2})

 return render(request, 'app/home.html',{'topwears':topwears,'mobiles':mobiles,'bottomwears':bottomwears})

 
def payment_done(request):
  user=request.user
  custid=request.GET.get('custid')
  customer=Customer.objects.get(id=custid)
  cart=Cart.objects.filter(user=user)
  for c in cart:
    OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
    c.delete()
  return redirect("orders")

class productdetailview(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
         
        cart_item=False
        cart_item=Cart.objects.filter(Q(user=request.user)&Q(product=product.id)).exists()
         
        return render(request,'app/productdetail.html',{'product':product,'cart_item':cart_item}) 
    

def add_to_cart(request):
 product_id=request.GET.get('prod_id') 
 product=Product.objects.get(id=product_id)
 user=request.user
 Cart(user=user,product=product).save()
 return redirect( '/cart' )

def show_cart(request):
  if request.user.is_authenticated:
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    
    cart_product=Cart.objects.filter(user=user)
    #print(cart_product)
    if cart_product:
      for p in cart_product:
        tempamount= (p.quantity * p.product.discounted_price)
        amount += tempamount
      totalamount = amount + shipping_amount
      return render(request, 'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount} )
    else:
      return render(request, 'app/emptycart.html' )


def buy_now(request):
 return render(request, 'app/buynow.html')

#def profile(request):
# return render(request, 'app/profile.html')

def Profile(request): 
    form=CustomerProfileForm()
    if request.method=="POST":
      form=CustomerProfileForm(request.POST )
      if form.is_valid():
        usr=request.user
        name=form.cleaned_data['name']
        locality=form.cleaned_data['locality']
        city=form.cleaned_data['city']
        state=form.cleaned_data['state']
        zipcode=form.cleaned_data['zipcode']
        reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
        reg.save()
        messages.success(request,'Congratulations!')
        return redirect ('profile')
        
    username=request.user
    return render (request,'app/profile.html',{'form':form,'active':'btn-primary'})

 
def address(request):
 adress=Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html',{'adress':adress,'active':'btn-primary'})

def orders(request):
 op=OrderPlaced.objects.filter(user=request.user) 
 return render(request, 'app/orders.html',{'order_placed':op})

 
def mobile(request,data=None):
 if data== None:
   mobiles=Product.objects.filter(category='M')
 elif data== 'redmi' or data=='realme' :
   mobiles=Product.objects.filter(category='M').filter(brand=data)
 elif data== 'below':
   mobiles=Product.objects.filter(category='M').filter(discounted_price__lt=10000)    
 elif data=='above':
   mobiles=Product.objects.filter(category='M').filter(discounted_price__gt=10000)    

 return render(request, 'app/mobile.html',{'mobiles':mobiles})


 
'''class CustomerRegistrationView(View):
   def get(self,request):
      form=CustomerRegistrationForm()
      return render(request, 'app/customerregistration.html',{'form':form})
   def post(self,request):
      form=CustomerRegistrationForm(request.POST)
      if form.is_valid():
         messages.success(request,'Congratulations! Registered Successfully')
         form.save()
      return render(request, 'app/customerregistration.html',{'form':form})'''

def CustomerRegistrationView(request):
  form=CustomerRegistrationForm()
  if request.method =="POST":
    form=CustomerRegistrationForm(request.POST)
    if form.is_valid():
        messages.success(request,'Congratulations! Registered Successfully')
        form.save()
        return redirect("profile")

  return render(request, 'app/customerregistration.html',{'form':form})


def checkout(request):
  user=request.user
  add=Customer.objects.filter(user=user)
  cart_item=Cart.objects.filter(user=user)
  amount=0.0
  shipping_amount=70.0
  totalamount=0.0   
  cart_product=[p for p in Cart.objects.all() if p.user==request.user]
  if cart_product:    
    for p in cart_product:
      tempamount= (p.quantity * p.product.discounted_price)
      amount += tempamount 
      totalamount=amount+ shipping_amount
  return render(request, 'app/checkout.html',{'add':add,'cart':cart_item,'totalamount':totalamount})

def plus_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    print(prod_id)
    c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
    c.quantity += 1
    c.save()
    amount=0.0
    shipping_amount=70.0
     
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    #print(cart_product)  
    for p in cart_product:
      tempamount= (p.quantity * p.product.discounted_price)
      amount += tempamount
   

    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)

def minus_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    print(prod_id)
    c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
    c.quantity -= 1
    c.save()
    amount=0.0
    shipping_amount=70.0
     
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    #print(cart_product)  
    for p in cart_product:
      tempamount= (p.quantity * p.product.discounted_price)
      amount += tempamount
     

    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)    

def remove_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    print(prod_id)
    c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
    c.delete()
    amount=0.0
    shipping_amount=70.0
     
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    print(cart_product)  
    for p in cart_product:
      tempamount= (p.quantity * p.product.discounted_price)
      amount += tempamount

    data={
       
      'amount':amount,
      'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)    

def search(request):
  if request.method=='GET':
    prod_id=request.GET['prod']
    print(prod_id)
    c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
    c.delete()
    amount=0.0
    shipping_amount=70.0
     
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    print(cart_product)  
    for p in cart_product:
      tempamount= (p.quantity * p.product.discounted_price)
      amount += tempamount

    data={
       
      'amount':amount,
      'totalamount':amount + shipping_amount
      }
    return JsonResponse(data)    

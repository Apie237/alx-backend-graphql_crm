

import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order, Product

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class OrderType(DjangoObjectType):it 
    class Meta:
        model = Order
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class UpdatedProductType(graphene.ObjectType):
    """Type for products updated in low stock mutation"""
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

class UpdateLowStockResult(graphene.ObjectType):
    """Result type for UpdateLowStockProducts mutation"""
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(UpdatedProductType)

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello World!")
    
    customers = graphene.List(CustomerType)
    orders = graphene.List(
        OrderType,
        order_date_after=graphene.String()
    )
    products = graphene.List(ProductType)
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_orders(self, info, order_date_after=None):
        queryset = Order.objects.all()
        if order_date_after:
            try:
                from datetime import datetime
                date_filter = datetime.strptime(order_date_after, '%Y-%m-%d').date()
                queryset = queryset.filter(order_date__gte=date_filter)
            except ValueError:
                pass
        return queryset
    
    def resolve_products(self, info):
        return Product.objects.all()

class UpdateLowStockProducts(graphene.Mutation):
    """
    Mutation to update products with low stock (< 10)
    Increments stock by 10 for each low-stock product
    """
    class Arguments:
        pass
    
    # Return type
    result = graphene.Field(UpdateLowStockResult)
    
    def mutate(self, info):
        try:
            # Find products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_products = []
            
            for product in low_stock_products:
                # Increment stock by 10
                product.stock += 10
                product.save()
                
                # Add to updated list
                updated_products.append(UpdatedProductType(
                    id=product.id,
                    name=product.name,
                    stock=product.stock
                ))
            
            return UpdateLowStockProducts(
                result=UpdateLowStockResult(
                    success=True,
                    message=f"Successfully updated {len(updated_products)} products with low stock",
                    updated_products=updated_products
                )
            )
            
        except Exception as e:
            return UpdateLowStockProducts(
                result=UpdateLowStockResult(
                    success=False,
                    message=f"Error updating low stock products: {str(e)}",
                    updated_products=[]
                )
            )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
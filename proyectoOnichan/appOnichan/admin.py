from django.contrib import admin
from .models import (
	Category,
	Product,
	ProductDetail,
	ProductSize,
	ProductSpec,
	ProductCare,
	ProductBreadcrumb,
	Customer,
	Order,
	OrderItem,
    PointReward,
    RedemptionHistory,
    UserCoupon,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug")
	search_fields = ("name",)


class ProductSizeInline(admin.TabularInline):
	model = ProductSize
	extra = 0


class ProductSpecInline(admin.TabularInline):
	model = ProductSpec
	extra = 0


class ProductCareInline(admin.TabularInline):
	model = ProductCare
	extra = 0


class ProductBreadcrumbInline(admin.TabularInline):
	model = ProductBreadcrumb
	extra = 0


class ProductDetailInline(admin.StackedInline):
	model = ProductDetail
	can_delete = False
	extra = 0


@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
	list_display = ("product", "rating", "rating_count", "color", "descuento_pct")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "price", "category")
	search_fields = ("name",)
	list_filter = ("category",)
	inlines = [ProductDetailInline, ProductSizeInline, ProductSpecInline, ProductCareInline, ProductBreadcrumbInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ("id", "name")


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("code", "fecha", "cliente", "estado", "total", "channel")
	list_filter = ("estado", "channel", "fecha")
	inlines = [OrderItemInline]


@admin.register(PointReward)
class PointRewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_cost', 'reward_type', 'active')
    list_filter = ('reward_type', 'active')
    search_fields = ('name', 'description')


@admin.register(RedemptionHistory)
class RedemptionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'points_spent', 'redeemed_at')
    list_filter = ('redeemed_at',)
    search_fields = ('user__username', 'reward__name')


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'acquired_at', 'is_used')
    list_filter = ('is_used', 'acquired_at')
    search_fields = ('user__username', 'coupon__code')


from django.contrib import admin

# Register your models here.

from .models import CustomUser, Register_form, Customer

admin.site.register(CustomUser)
admin.site.register(Register_form)
admin.site.register(Customer)

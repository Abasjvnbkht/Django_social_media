from django.contrib import admin
from .models import Relation, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ProfileInline(admin.StackedInline):
    # inja mikhaym modele profile ro karim konim k bechasbe b akhare user dar admin dge odda nabashe az user
    # admin.stackinline yani ye chizio bechasbun b tahe ye chize dge
    model = Profile
    can_delete = False


class ExtendedUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    # inline yani garare ye chizi biad bechasbe b tahe ma


admin.site.unregister(User)
# bayad in modele user ro unregister konim ta un modekle k khodemun mihaym ro benevisim
admin.site.register(User, ExtendedUserAdmin)
# modele user ro hamrah ba extended user admin register bokon
admin.site.register(Relation)

from django.contrib import admin
from .models import *


admin.site.register(Post)
admin.site.register(Review)
admin.site.register(UserProfile)
admin.site.register(Answer)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Planner)
admin.site.register(PlannerMandatory)
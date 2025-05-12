from django.contrib import admin
from .models import (Team,Department,Summary,Vote,Healthcheckcard,)


# Register your models here.
admin.site.register(Team)
admin.site.register(Department)
admin.site.register(Summary)
admin.site.register(Vote)
admin.site.register(Healthcheckcard)
admin.site.site_header = "Team Health Check Admin"
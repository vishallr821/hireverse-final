from django.contrib import admin
from .models import Test, Question, Answer, DSASession, FinalResult

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(DSASession)
admin.site.register(FinalResult)

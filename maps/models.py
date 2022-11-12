from django.contrib.auth import get_user_model
from django.db import models
user=get_user_model()
payment=settingsPAYMENT_MODEL
# Create your models here.
class Incident(models.Model):
    driver=models.ForeignKey(user,on_delete=models.CASCADE,related_name="driver")
    towtruck=models.ForeignKey(user,on_delete=models.CASCADE,related_name="towtruck")
    garage=models.ForeignKey(user,on_delete=models.CASCADE,related_name="garage")
    payment=models.ForeignKey(payment,on_delete=models.CASCADE,related_name="payment")

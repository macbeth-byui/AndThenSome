from django.db import models

class Categories(models.Model):

    class Type(models.IntegerChoices):
        INCOME = 1, "Income"
        EXPENSE = 2, "Expense"

    c_name = models.CharField(max_length=30)
    c_type = models.IntegerField(choices=Type.choices)
    c_monthly = models.FloatField()
    c_planned = models.FloatField()
    c_notes = models.CharField(max_length=200)

    def __str__(self):
        return "c_name={} c_type={} c_monthly={} c_planned={} c_notes={}".format(self.c_name,self.c_type,self.c_monthly,self.c_planned,self.c_notes)

class Budget(models.Model):

    b_month = models.IntegerField()
    b_year = models.IntegerField()
    b_starting = models.FloatField()

    def __str__(self):
        return "b_month={} b_year={} b_starting={}".format(self.b_month, self.b_year, self.b_starting)

class Transactions(models.Model):

    t_description = models.CharField(max_length=50)
    t_amount = models.FloatField()
    t_cleared = models.BooleanField()
    t_month = models.IntegerField()
    t_year = models.IntegerField()
    t_category = models.ForeignKey(Categories, on_delete=models.CASCADE)

    def __str__(self):
        return "t_description={} t_amount={} t_cleared={} t_month={} t_year={} ".format(self.t_description,self.t_amount,self.t_cleared,self.t_month,self.t_year)
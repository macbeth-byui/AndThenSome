from typing import ValuesView
from django.shortcuts import render, redirect
from budget.models import Categories
from budget.models import Transactions
from budget.models import Budget
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout

from datetime import datetime

def convert_month(month):
    months = ["January","February","March","April","May","June","July","August","September","October","Novemeber","December"]
    return months[month-1]

def login_app(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            values = {'error': "Invalid Username or Password"}
            return render(request, 'budget/login.html', values)
    else:
        values = {}
        return render(request, 'budget/login.html', values)    


def home(request):
    if request.method == "POST":
        if request.POST["action"] == "Logoff":
            logout(request)
            return redirect(login_app)

    if not request.user.is_authenticated:
        return redirect("login_app")
    try:
        budget = Budget.objects.get(id=1)
    except:
        budget = None
    if budget is None:
        # First time we need to put something in the budget table
        month = datetime.now().month
        year = datetime.now().year
        budget_rec = Budget(b_month=month, b_year=year, b_starting=0.00)
        budget_rec.save()
        # Read it back for use
        budget = Budget.objects.get(id=1)

    categories = Categories.objects.all().order_by("c_type","c_name")
    categories_income_sum = Categories.objects.filter(c_type=Categories.Type.INCOME).aggregate(Sum("c_monthly"),Sum("c_planned"))
    if categories_income_sum["c_monthly__sum"] == None:
        categories_income_sum["c_monthly__sum"] = 0
    if categories_income_sum["c_planned__sum"] == None:
        categories_income_sum["c_planned__sum"] = 0        
    categories_expense_sum = Categories.objects.filter(c_type=Categories.Type.EXPENSE).aggregate(Sum("c_monthly"),Sum("c_planned"))
    if categories_expense_sum["c_monthly__sum"] == None:
        categories_expense_sum["c_monthly__sum"] = 0
    if categories_expense_sum["c_planned__sum"] == None:
        categories_expense_sum["c_planned__sum"] = 0                  
    values = dict()
    values["month"] = convert_month(budget.b_month)
    values["year"] = budget.b_year
    values["starting"] = budget.b_starting
    values["total_monthly"] = categories_income_sum["c_monthly__sum"] - categories_expense_sum["c_monthly__sum"]
    values["total_planned"] = budget.b_starting + categories_income_sum["c_planned__sum"] - categories_expense_sum["c_planned__sum"]
    total_actual = 0
    for category in categories:
        trans_for_category = Transactions.objects.all().filter(t_category=category.id).filter(t_month=budget.b_month).filter(t_year=budget.b_year).aggregate(Sum("t_amount"))
        if trans_for_category["t_amount__sum"] is None:
            category.actual = 0
        else:
            category.actual = trans_for_category["t_amount__sum"]
        if category.c_type == Categories.Type.INCOME:
            total_actual += category.actual
            category.difference = category.actual - category.c_planned
        else:
            category.c_monthly *= -1
            category.c_planned *= -1
            category.actual *= -1
            total_actual += category.actual
            category.difference = (category.c_planned - category.actual) * -1
        
    values["total_actual"] = budget.b_starting + total_actual
    values["total_difference"] = values["total_actual"] - values["total_planned"]
    values["categories"] = categories

    if request.method == "POST":
        if request.POST["action"] == "Filter":
            month_display = request.POST["month"]
            year_display = request.POST["year"]
        else:
            month_display = budget.b_month
            year_display = budget.b_year
    else:
        month_display = budget.b_month
        year_display = budget.b_year

    transactions = Transactions.objects.all().filter(t_month=month_display).filter(t_year=year_display)        
    values["transactions"] = transactions
    values["month_display"] = month_display
    values["year_display"] = year_display

    return render(request,"budget/home.html", values)

def category(request, c_id=None):
    if not request.user.is_authenticated:
        return redirect("login_app")
    if c_id is not None:
        category = Categories.objects.get(id=c_id)
    else:
        category = Categories()

    if request.method == 'POST':
        if request.POST["action"] == "Submit":
            category.c_name = request.POST["name"]
            category.c_type = int(request.POST["type"])
            category.c_monthly = float(request.POST["monthly"])
            category.c_planned = float(request.POST["planned"])
            category.c_notes = request.POST["notes"]
            category.save()
        elif request.POST["action"] == "Delete":
            category.delete()
        return redirect("home")
    else:
        values = {'category': category, 'id': c_id}
        return render(request, 'budget/category.html', values)
    

def transact(request, t_id=None):
    if not request.user.is_authenticated:
        return redirect("login_app")    
    if t_id is not None:
        transact = Transactions.objects.get(id=t_id)
    else:
        transact = Transactions()

    if request.method == 'POST':
        if request.POST["action"] == "Submit" or request.POST["action"] == "Submit & Add Another":
            transact.t_month = int(request.POST["month"])
            transact.t_year = int(request.POST["year"])
            transact.t_description = request.POST["description"]
            category = Categories.objects.get(id=request.POST["category"])
            transact.t_category = category
            print(request.POST["amount"])
            transact.t_amount = float(request.POST["amount"])
            if "cleared" in request.POST:
                transact.t_cleared = True
            else:
                transact.t_cleared = False
            print(transact)                
            transact.save()
        elif request.POST["action"] == "Delete":
            transact.delete()
        if request.POST["action"] == "Submit":
            return redirect("home")
        else:
            return redirect("transact")
    else:
        categories = Categories.objects.all().order_by("c_name")
        budget = Budget.objects.get(id=1)
        transact.t_month = budget.b_month
        transact.t_year = budget.b_year
        values = {'transact': transact, 'id': t_id, 'categories': categories}
        return render(request, 'budget/transact.html', values)

def month(request):
    if not request.user.is_authenticated:
        return redirect("login_app")    
    budget = Budget.objects.get(id=1)
    if request.method == 'POST':
        if request.POST["action"] == "Submit":
            budget.b_month = int(request.POST["month"])
            budget.b_year = int(request.POST["year"])
            budget.b_starting = float(request.POST["starting"])
            budget.save()
        return redirect("home")
    else:
        values = {'budget': budget}
        return render(request, 'budget/month.html', values)


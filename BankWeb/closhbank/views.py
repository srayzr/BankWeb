from django.shortcuts import render, redirect
from django.views import View
from .models import Person, Money, BankAccount

class CreatePersonView(View):
    template_name = 'closhbank/create_person.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        person = Person.objects.create(name=name, surname=surname, age=age, gender=gender)
        return redirect('person_detail', person_id=person.id)

class PersonDetailView(View):
    template_name = 'closhbank/person_detail.html'
    
    def get(self, request, person_id):
        person = Person.objects.get(id=person_id)
        return render(request, self.template_name, {'person': person})

class CreateAccountView(View):
    template_name = 'closhbank/create_account.html'
    
    def get(self, request):
        persons = Person.objects.all()
        return render(request, self.template_name, {'persons': persons})
    
    def post(self, request):
        owner_id = int(request.POST.get('owner'))
        owner = Person.objects.get(id=owner_id)
        balance = float(request.POST.get('balance'))
        currency = request.POST.get('currency')
        account = BankAccount.objects.create(owner=owner, balance=balance, currency=currency)
        return redirect('account_detail', account_id=account.id)

class AccountDetailView(View):
    template_name = 'closhbank/account_detail.html'
    
    def get(self, request, account_id):
        account = BankAccount.objects.get(id=account_id)
        return render(request, self.template_name, {'account': account})

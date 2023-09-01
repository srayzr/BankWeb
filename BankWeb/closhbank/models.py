from django.db import models
import uuid
import hashlib

class Person(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)

    def __repr__(self):
        if self.gender == "Male":
            return "{} {} - {}".format(self.name, self.surname, self.age)
        else:
            return "{} {}".format(self.name, self.surname)

    def add_age(self, n=1):
        self.age += n

class Money(models.Model):
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    EXCHANGE_RATE = {
        "AMD": 1,
        "RUB": 4,
        "USD": 400,
        "EUR": 420
    }

    def __repr__(self):
        return "{} {}".format(self.amount, self.currency)

    def exchange(self, curr):
        rate = Money.EXCHANGE_RATE[self.currency] / Money.EXCHANGE_RATE[curr]
        return Money.objects.create(currency=curr, amount=rate * self.amount)

    def __add__(self, other):
        if self.currency != other.currency:
            other = other.exchange(self.currency)
        return Money.objects.create(currency=self.currency, amount=self.amount + other.amount)

    def deposit(self, p, n):
        return Money.objects.create(currency=self.currency, amount=round(self.amount * ((1 + p / 100) ** n), 2))

    def __mul__(self, n):
        return Money.objects.create(currency=self.currency, amount=self.amount * n)

class Hasher:
    def __init__(self, algorithm='sha256'):
        self.algorithm = algorithm

    def hash_string(self, string):
        hasher = hashlib.new(self.algorithm)
        hasher.update(string.encode('utf-8'))
        return hasher.hexdigest()

class Date(models.Model):
    MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    MONTH_NAMES = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    def __init__(self, y, m, d):
        self.year = y
        self.month = m
        self.day = d

    def __repr__(self):
        return "{} {} {}".format(self.day, self.MONTH_NAMES[self.month], self.year)

    def add_year(self, n=1):
        self.year += n

    def add_month(self, n=1):
        self.add_year((self.month + n - 1) // 12)
        self.month = (self.month + n - 1) % 12 + 1

    def add_day(self, n=1):
        self.add_month((self.day + n - 1) // 30)
        self.day = (self.day + n - 1) % 30 + 1

class TimeValueError(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value

    def __str__(self):
        return "Wrong value for {}: {}".format(self.message, self.value)

class TimeTypeError(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value

    def __str__(self):
        return "Wrong type for {}: {}".format(self.message, type(self.value))

class Time(models.Model):
    hour = models.PositiveIntegerField()
    minute = models.PositiveIntegerField()
    second = models.PositiveIntegerField()

    def __init__(self, h, m, s):
        try:
            if type(h) != int:
                raise TimeTypeError("hour", h)
            elif type(m) != int:
                raise TimeTypeError("minute", m)
            elif type(s) != int:
                raise TimeTypeError("second", s)

            if h < 0 or h > 23:
                raise TimeValueError("hour", h)
            elif m < 0 or m > 59:
                raise TimeValueError("minute", m)
            elif s < 0 or s > 59:
                raise TimeValueError("second", s)
        except TimeValueError as err:
            print(err)
        except TimeTypeError as err:
            print(err)
        else:
            self.hour = h
            self.minute = m
            self.second = s

    def __repr__(self):
        try:
            return "{}:{}:{}".format(self.hour, self.minute, self.second)
        except AttributeError:
            return "Object is empty."

    def add_hour(self, n):
        try:
            if type(n) != int:
                raise TimeTypeError("param n", type(n))
            if n <= 0:
                raise TimeValueError("param n", n)
            self.hour = (self.hour + n) % 24
        except TimeValueError as err:
            print(err)
        except TimeTypeError as err:
            print(err)
        except AttributeError:
            print("Object does not have attribute 'hour'")

class BankAccount(models.Model):
    account_number = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    system_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True)  # Allowing null values

    

    def __repr__(self):
        return "Account Number: {}\nOwner: {}\nBalance: {} {}".format(
            self.account_number, self.owner, self.balance, self.currency
        )

    def create_password(self):
        password = input("Enter your bank account password please\n")
        hasher = Hasher()
        self.password = hasher.hash_string(password)
        print("***Your password was successfully saved***")

    def get_password(self):
        print(f"***Hashed password is\n{self.password}***")

    def deposit(self, amount):
        if isinstance(amount, Money):
            if amount.currency == self.currency:
                self.balance += amount.amount
            else:
                converted_amount = amount.exchange(self.currency)
                self.balance += converted_amount.amount
        else:
            print("Invalid amount type.")

    def withdraw(self, amount):
        if isinstance(amount, Money):
            if amount.currency == self.currency:
                if amount.amount <= self.balance:
                    self.balance -= amount.amount
                else:
                    print("Insufficient balance.")
            else:
                print("Currency mismatch.")
        else:
            print("Invalid amount type.")

    def transfer(self, destination_account, amount):
        if isinstance(amount, Money):
            if amount.currency == self.currency:
                if amount.amount <= self.balance:
                    commission = amount.amount * 10 / 100
                    self.balance -= amount.amount
                    self.system_balance = commission
                    self.amount = amount.amount - commission
                    destination_account.balance += amount.amount - commission
                    return True
                else:
                    print("Insufficient balance.")
                    return False
            else:
                print("Currency mismatch.")
                return False
        else:
            print("Invalid amount type.")
            return False

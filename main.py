from __future__ import annotations

from abc import ABC, abstractmethod
import random
import datetime
from typing import Union, List


class Transaction:
    def __init__(self, transaction_type: str, amount: float, timestamp: datetime.datetime):
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f"{self.timestamp} - {self.transaction_type}: ${self.amount}"


class Bank:
    def __init__(self):
        self.customers: List[Customer] = []
        self.active_sessions: dict[str, Customer] = {}

    def create_account(self, account_type: str = "Savings", initial_balance: float = 0) -> Customer:
        account_number = str(random.randint(10000, 99999))
        if account_type == "Normal":
            account = NormalAccount(account_number, initial_balance)
        elif account_type == "Debit":
            account = DebitAccount(account_number, initial_balance)
        else:
            raise ValueError("Invalid account type.")

        customer = Customer(account_number, account)
        self.customers.append(customer)
        return customer

    def authenticate_customer(self, account_number: str, pin: str) -> Union[str, None]:
        for customer in self.customers:
            if customer.account.account_number == account_number and customer.authenticate(pin):
                session_token = str(random.randint(100000, 999999))
                self.active_sessions[session_token] = customer
                return session_token
        return None

    def end_session(self, session_token: str) -> None:
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            print("Session ended successfully.")
        else:
            print("Invalid session token.")

    def get_customer(self, account_number: str) -> Union[Customer, None]:
        for customer in self.customers:
            if customer.account.account_number == account_number:
                return customer
        return None


class Account(ABC):
    def __init__(self, account_number: str, balance: float = 0) -> None:
        self.account_number = account_number
        self.balance = balance
        self.is_locked = False
        self.transactions: List[Transaction] = []

    @abstractmethod
    def calculate_interest(self, rate: float) -> None:
        pass

    def deposit(self, amount: float) -> None:
        if not self.is_locked and amount > 0:
            self.balance += amount
            self.transactions.append(Transaction("Deposit", amount, datetime.datetime.now()))
            print(f"Deposited ${amount}. New balance: ${self.balance}")
        elif self.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid deposit amount.")

    @abstractmethod
    def withdraw(self, amount: float, overdraft_protection: bool = False) -> None:
        pass

    def get_balance(self) -> float:
        return self.balance

    def lock_account(self) -> None:
        self.is_locked = True
        print("Account locked.")

    def unlock_account(self) -> None:
        self.is_locked = False
        print("Account unlocked.")

    def view_transactions(self) -> None:
        if not self.is_locked:
            for transaction in self.transactions:
                print(transaction)
        else:
            print("Account is locked. Cannot view transactions.")


class NormalAccount(Account):
    def withdraw(self, amount: float, overdraft_protection: bool = False) -> None:
        if not self.is_locked and (
                0 < amount <= self.balance or (overdraft_protection and amount <= self.balance + 100)):
            self.balance -= amount
            self.transactions.append(Transaction("Withdrawal", amount, datetime.datetime.now()))
            print(f"Withdrew ${amount}. New balance: ${self.balance}")
        elif self.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid withdrawal amount or insufficient funds.")

    def calculate_interest(self, rate: float) -> None:
        if not self.is_locked:
            interest = self.balance * rate / 100
            self.balance += interest
            self.transactions.append(Transaction("Interest", interest, datetime.datetime.now()))
            print(f"Interest added: ${interest}. New balance: ${self.balance}")
        else:
            print("Account is locked. Cannot calculate interest.")


class DebitAccount(Account):
    def withdraw(self, amount: float, overdraft_protection: bool = False) -> None:
        if not self.is_locked and 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append(Transaction("Withdrawal", amount, datetime.datetime.now()))
            print(f"Withdrew ${amount}. New balance: ${self.balance}")
        elif self.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid withdrawal amount or insufficient funds.")

    def calculate_interest(self, rate: float) -> None:
        print("Debit accounts do not earn interest.")


class Customer:
    def __init__(self, account_number: str, account: Account) -> None:
        self.account_number = account_number
        self.account = account
        self.pin = str(random.randint(1000, 9999))

    def authenticate(self, entered_pin: str) -> bool:
        return entered_pin == self.pin

    def transfer(self, recipient_account: Account, amount: float) -> None:
        if not self.account.is_locked and 0 < amount <= self.account.balance:
            self.account.withdraw(amount)
            recipient_account.deposit(amount)
            self.account.transactions.append(Transaction("Transfer", amount, datetime.datetime.now()))
            print(f"Transferred ${amount} to {recipient_account.account_number}")
        elif self.account.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid transfer amount or insufficient funds.")


# Example usage:

bank = Bank()

# Create customer accounts
customer1 = bank.create_account("Normal", 1000)
customer2 = bank.create_account("Normal", 500)
customer3 = bank.create_account("Debit", 1500)

# Authenticate customers
session_token1 = bank.authenticate_customer(customer1.account_number, customer1.pin)
session_token2 = bank.authenticate_customer(customer2.account_number, customer2.pin)
session_token3 = bank.authenticate_customer(customer3.account_number, customer3.pin)

# Deposit and withdraw
customer1.account.deposit(500)
customer1.account.withdraw(200)

customer2.account.deposit(1000)
customer2.account.withdraw(200)

# Transfer funds
customer1.transfer(customer2.account, 300)

# Check balances
print(f"{customer1.account_number}'s balance: ${customer1.account.get_balance()}")
print(f"{customer2.account_number}'s balance: ${customer2.account.get_balance()}")
print(f"{customer3.account_number}'s balance: ${customer3.account.get_balance()}")

# Calculate interest
customer1.account.calculate_interest(2.5)
customer2.account.calculate_interest(1.5)
customer3.account.calculate_interest(3.0)

# Lock and unlock account
customer1.account.lock_account()
customer2.account.unlock_account()

# View transactions
customer1.account.view_transactions()
customer2.account.view_transactions()

# Withdraw with overdraft protection (not applicable for DebitAccount)
customer3.account.withdraw(1800, overdraft_protection=True)

# End sessions
bank.end_session(session_token1)
bank.end_session(session_token2)
bank.end_session(session_token3)

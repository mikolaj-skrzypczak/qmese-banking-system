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

    @staticmethod
    def create_account(account_type: str = "Normal", initial_balance: float = 0) -> Account:
        account_number = str(random.randint(10000, 99999))
        if account_type == "Normal":
            account = NormalAccount(account_number, initial_balance)
        elif account_type == "Debit":
            account = DebitAccount(account_number, initial_balance)
        else:
            raise ValueError("Invalid account type.")

        return account

    def add_customer(self, customer: Customer):
        self.customers.append(customer)

    def authenticate_customer(self, pin: str) -> Union[str, None]:
        for customer in self.customers:
            if customer.authenticate(pin):
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
            for account in customer.accounts:
                if account.account_number == account_number:
                    return customer
        return None

    def print_customers_info(self) -> None:
        for customer in self.customers:
            for account in customer.accounts:
                print(f"Account Number: {account.account_number}")
                print(f"Balance: ${account.balance}")
                print(f"Is Locked: {account.is_locked}")
                print("Transactions:")
                for transaction in account.transactions:
                    print(f"\t{transaction}")
                print()


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
        print("Normal accounts do not earn interest.")


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


class SavingsAccount:
    def __init__(self, account_number: str, balance: float = 0) -> None:
        self.account_number = account_number
        self.balance = balance
        self.is_locked = False
        self.transactions = []

    def deposit(self, amount: float) -> None:
        if not self.is_locked and amount > 0:
            self.balance += amount
            self.transactions.append(Transaction("Deposit", amount, datetime.datetime.now()))
            print(f"Deposited ${amount}. New balance: ${self.balance}")
        elif self.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid deposit amount.")

    def withdrawal(self, amount: float) -> None:
        if self.is_locked:
            self.balance -= amount
            self.transactions.append(Transaction("Withdrawal", amount, datetime.datetime.now()))
            print(f"Withdrew ${amount}. New balance: ${self.balance}")
        elif self.is_locked:
            print("Account is locked. Cannot perform transactions.")
        else:
            print("Invalid withdrawal amount or insufficient funds.")

    def get_balance(self):
        return self.balance

    def lock_account(self) -> None:
        self.is_locked = True
        print("Account locked.")

    def unlock_account(self) -> None:
        self.is_locked = False
        print("Account unlocked.")

    def view_transactions(self) -> None:
        if self.is_locked:
            for transaction in self.transactions:
                print(transaction)
        else:
            print("Account is locked. Cannot view transactions.")

    def calculate_interest(self, rate):
        if not self.is_locked:
            interest = self.balance + rate / 100
            self.balance += interest
            self.transactions.append(Transaction("Interest", interest, datetime.datetime.now()))
            print(f"Interest added: ${interest}. New balance: ${self.balance}")
        else:
            print("Account is locked. Cannot calculate interest.")


class Customer:
    def __init__(self, customer_id: int, accounts: List[Account]) -> None:
        self.customer_id = customer_id
        self.accounts = accounts
        self.pin = str(random.randint(1000, 9999))

    def authenticate(self, entered_pin: str) -> bool:
        return entered_pin == self.pin

    def add_account(self, account: Account) -> None:
        self.accounts.append(account)

    @staticmethod
    def transfer(sender_account: Account, recipient_account: Account, amount: float) -> None:
        if sender_account.is_locked or recipient_account.is_locked:
            print("One or more accounts involved in the transfer are locked. Cannot perform the transfer.")
            return

        if amount <= 0 or amount > sender_account.get_balance():
            print("Invalid transfer amount or insufficient funds.")
            return

        sender_account.withdraw(amount)
        recipient_account.deposit(amount)

        transaction = Transaction("Transfer", amount, datetime.datetime.now())
        sender_account.transactions.append(transaction)
        recipient_account.transactions.append(transaction)

        print(f"Transferred ${amount} from {sender_account.account_number} to {recipient_account.account_number}")


bank = Bank()

# Create customer accounts
customer1 = Customer(customer_id=1, accounts=[
    bank.create_account("Normal", 1000),
    bank.create_account("Debit", 500)])
customer2 = Customer(customer_id=2, accounts=[
    bank.create_account("Debit", 1500),
    bank.create_account("Normal", 2000)])
customer3 = Customer(customer_id=3, accounts=[
    bank.create_account("Savings", 2000),
    bank.create_account("Normal", 1500)])

bank.add_customer(customer1)
bank.add_customer(customer2)
bank.add_customer(customer3)

# Authenticate customers
session_token1 = bank.authenticate_customer(customer1.pin)
session_token2 = bank.authenticate_customer(customer2.pin)
session_token3 = bank.authenticate_customer(customer3.pin)

# Deposit and withdraw from different accounts
customer1.accounts[0].deposit(500)
customer1.accounts[1].withdraw(200)

customer2.accounts[0].deposit(1000)
customer2.accounts[1].withdraw(300)

customer3.accounts[0].deposit(1000)
customer3.accounts[1].withdraw(100)

# Transfer funds between accounts of the same customer
customer1.transfer(customer1.accounts[0], customer1.accounts[1], 300)

# Calculate interest
customer1.accounts[0].calculate_interest(2.5)
customer1.accounts[1].calculate_interest(1.5)

# Lock and unlock account
customer1.accounts[0].lock_account()
customer2.accounts[0].unlock_account()

# View transactions
customer1.accounts[0].view_transactions()
customer2.accounts[0].view_transactions()

# Withdraw with overdraft protection (not applicable for DebitAccount)
customer1.accounts[0].withdraw(1800, overdraft_protection=True)

# End sessions
bank.end_session(session_token1)
bank.end_session(session_token2)
bank.end_session(session_token3)

# print customers information
bank.print_customers_info()

# LLD & Design Patterns Assessment

> **Instructions:** 
> - Answer each question before looking at the answer key
> - Time yourself: ~45-60 minutes for full assessment
> - Score yourself honestly
> - Answers are at the end - NO PEEKING!

---

## Section 1: Pattern Identification (20 Questions)

*Given the scenario, identify the BEST design pattern to use.*

### Q1.
An e-commerce platform needs to calculate shipping costs. The calculation varies based on:
- Standard shipping
- Express shipping  
- Same-day delivery
- International shipping

The shipping method is selected by the user at checkout.

**Which pattern?** _______________

---

### Q2.
A document editor needs to support undo/redo functionality for operations like:
- Insert text
- Delete text
- Format text
- Insert image

**Which pattern?** _______________

---

### Q3.
A ride-sharing app has rides that go through these states:
- Requested → Driver Assigned → Driver Arrived → In Progress → Completed

Each state has different valid operations (e.g., can't cancel when in-progress).

**Which pattern?** _______________

---

### Q4.
A notification system needs to send alerts through multiple channels:
- Email
- SMS
- Push notification
- Slack

The channel is configured per user, and users can change their preference anytime.

**Which pattern?** _______________

---

### Q5.
A coffee ordering system where customers can customize their drink with:
- Extra shot (+$0.50)
- Whipped cream (+$0.75)
- Soy milk (+$0.40)
- Caramel drizzle (+$0.60)

Combinations can be stacked (e.g., extra shot + whipped cream + soy milk).

**Which pattern?** _______________

---

### Q6.
A game has different character types:
- Warrior
- Mage
- Archer
- Healer

The character type is chosen when the game starts based on user selection.

**Which pattern?** _______________

---

### Q7.
A stock trading platform needs to notify multiple components when a stock price changes:
- Update the price chart
- Check alert thresholds
- Update portfolio value
- Log to analytics

**Which pattern?** _______________

---

### Q8.
An API client that needs to:
- Cache responses to avoid redundant network calls
- Log all requests for debugging
- Handle authentication transparently

**Which pattern?** _______________

---

### Q9.
A hotel booking system where a reservation object has:
- Guest details (required)
- Room type (required)
- Check-in date (required)
- Check-out date (required)
- Special requests (optional)
- Meal plan (optional)
- Airport pickup (optional)
- Late checkout (optional)
- Extra bed (optional)
- Parking (optional)

**Which pattern?** _______________

---

### Q10.
A vending machine that operates differently based on whether:
- It's idle (waiting for selection)
- Item is selected (waiting for payment)
- Payment received (dispensing item)
- Out of stock (showing error)

**Which pattern?** _______________

---

### Q11.
An application needs exactly ONE instance of:
- Database connection pool
- Configuration manager
- Logger

**Which pattern?** _______________

---

### Q12.
A legacy payment gateway uses this interface:
```python
def charge(amount_cents: int, card_number: str, expiry: str)
```

But your system expects:
```python
def process_payment(amount_dollars: float, payment_info: PaymentInfo)
```

**Which pattern?** _______________

---

### Q13.
A ride request must go through multiple validation checks:
1. User verification
2. Payment validation
3. Fraud detection
4. Location validation
5. Surge pricing calculation

Each check can either pass (continue to next) or fail (reject request).

**Which pattern?** _______________

---

### Q14.
A file system where:
- Files have a name and size
- Folders contain files and other folders
- You want to calculate total size of a folder (including all nested contents)
- You want to treat files and folders uniformly

**Which pattern?** _______________

---

### Q15.
A booking platform has different booking flows:
- UberX booking
- UberBlack booking  
- UberPool booking

All follow the same steps:
1. Validate request
2. Find driver (logic varies)
3. Calculate fare (logic varies)
4. Create booking

**Which pattern?** _______________

---

### Q16.
A smart home system where pressing a button should:
- Turn on lights in the living room
- Set thermostat to 72°F
- Start playing music
- Close the blinds

The button doesn't know about individual devices.

**Which pattern?** _______________

---

### Q17.
A text editor that can have multiple views (GUI, console, web) all showing the same document. When the document changes, all views should update automatically.

**Which pattern?** _______________

---

### Q18.
A logistics system where:
- The driver matching algorithm needs to be swapped between:
  - Nearest driver
  - Highest rated driver
  - Fastest ETA driver
- The algorithm can be changed by the system based on demand

**Which pattern?** _______________

---

### Q19.
A payment processing system that needs to support:
- Credit card payments
- Debit card payments
- PayPal payments
- Crypto payments

Each payment type has different processing logic, and new types may be added.

**Which pattern?** _______________

---

### Q20.
An airline booking system that creates:
- Economy class → Economy seat + Basic meal + Standard baggage
- Business class → Business seat + Premium meal + Extra baggage
- First class → First class seat + Gourmet meal + Unlimited baggage

The seat, meal, and baggage must all be compatible with the class.

**Which pattern?** _______________

---

## Section 2: Pattern Comparison (10 Questions)

*Choose the correct answer.*

### Q21.
What is the PRIMARY difference between Strategy and State patterns?

A) Strategy uses inheritance, State uses composition  
B) Strategy is chosen by client, State transitions internally  
C) Strategy is for algorithms, State is for data  
D) There is no difference, they are the same pattern

**Answer:** ___

---

### Q22.
When would you use Builder over Factory?

A) When you need to create different types of objects  
B) When the object has many optional parameters  
C) When you need only one instance  
D) When objects need to notify others of changes

**Answer:** ___

---

### Q23.
What is the key difference between Decorator and Proxy?

A) Decorator adds behavior, Proxy controls access  
B) Decorator is faster than Proxy  
C) Proxy can only wrap one object, Decorator can wrap many  
D) They are used interchangeably

**Answer:** ___

---

### Q24.
Observer vs Mediator - which statement is TRUE?

A) Observer is for many-to-many communication  
B) Mediator eliminates direct communication between objects  
C) Observer requires a central hub  
D) Mediator is only for one-to-many relationships

**Answer:** ___

---

### Q25.
Factory vs Abstract Factory - which is correct?

A) Factory creates families of objects, Abstract Factory creates single objects  
B) Abstract Factory creates families of related objects  
C) They are the same pattern with different names  
D) Factory uses inheritance, Abstract Factory uses composition

**Answer:** ___

---

### Q26.
Template Method vs Strategy - which is TRUE?

A) Template Method allows changing the entire algorithm at runtime  
B) Strategy defines a fixed algorithm skeleton with customizable steps  
C) Template Method uses inheritance, Strategy uses composition  
D) Strategy is always better than Template Method

**Answer:** ___

---

### Q27.
Command vs Strategy - the main PURPOSE difference is:

A) Command is for undo/redo/queuing, Strategy is for algorithm swapping  
B) Command is faster than Strategy  
C) Strategy supports undo, Command doesn't  
D) They solve the same problem

**Answer:** ___

---

### Q28.
Adapter vs Facade - which statement is correct?

A) Adapter simplifies a complex subsystem  
B) Facade converts one interface to another  
C) Adapter makes incompatible interfaces work together  
D) They are the same pattern

**Answer:** ___

---

### Q29.
Which pattern violates the "prefer composition over inheritance" principle?

A) Strategy  
B) Decorator  
C) Template Method  
D) Observer

**Answer:** ___

---

### Q30.
In State pattern, who is responsible for state transitions?

A) Only the client  
B) Only the context class  
C) The state classes themselves (typically)  
D) A separate StateManager class

**Answer:** ___

---

## Section 3: Code Analysis (10 Questions)

*Identify the pattern used in each code snippet.*

### Q31.
```python
class PaymentProcessor:
    def process(self, payment_type: str, amount: float):
        if payment_type == "credit":
            return CreditCardPayment().charge(amount)
        elif payment_type == "paypal":
            return PayPalPayment().charge(amount)
        elif payment_type == "crypto":
            return CryptoPayment().charge(amount)
```

**Pattern:** _______________

---

### Q32.
```python
class Coffee:
    def get_cost(self): return 5.0
    def get_description(self): return "Coffee"

class MilkDecorator:
    def __init__(self, coffee):
        self._coffee = coffee
    def get_cost(self):
        return self._coffee.get_cost() + 1.5
    def get_description(self):
        return self._coffee.get_description() + " + Milk"

# Usage
drink = MilkDecorator(Coffee())
```

**Pattern:** _______________

---

### Q33.
```python
class Order:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def set_status(self, status):
        self._status = status
        for observer in self._observers:
            observer.update(self._status)
```

**Pattern:** _______________

---

### Q34.
```python
class Document:
    def __init__(self):
        self._state = DraftState()
    
    def set_state(self, state):
        self._state = state
    
    def publish(self):
        self._state.publish(self)
    
    def edit(self):
        self._state.edit(self)

class DraftState:
    def publish(self, doc):
        doc.set_state(ModerationState())
    
    def edit(self, doc):
        print("Editing draft...")
```

**Pattern:** _______________

---

### Q35.
```python
class ReportBuilder:
    def __init__(self):
        self._report = Report()
    
    def set_title(self, title):
        self._report.title = title
        return self
    
    def add_section(self, section):
        self._report.sections.append(section)
        return self
    
    def set_footer(self, footer):
        self._report.footer = footer
        return self
    
    def build(self):
        return self._report

# Usage
report = ReportBuilder().set_title("Q1").add_section("Sales").build()
```

**Pattern:** _______________

---

### Q36.
```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Pattern:** _______________

---

### Q37.
```python
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data): pass

class QuickSort(SortStrategy):
    def sort(self, data):
        # quicksort implementation
        pass

class MergeSort(SortStrategy):
    def sort(self, data):
        # mergesort implementation
        pass

class DataProcessor:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def process(self, data):
        return self._strategy.sort(data)
```

**Pattern:** _______________

---

### Q38.
```python
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

class InsertTextCommand(Command):
    def __init__(self, editor, text, position):
        self.editor = editor
        self.text = text
        self.position = position
    
    def execute(self):
        self.editor.insert(self.text, self.position)
    
    def undo(self):
        self.editor.delete(self.position, len(self.text))
```

**Pattern:** _______________

---

### Q39.
```python
class Handler(ABC):
    def __init__(self):
        self._next = None
    
    def set_next(self, handler):
        self._next = handler
        return handler
    
    def handle(self, request):
        if self._can_handle(request):
            return self._process(request)
        elif self._next:
            return self._next.handle(request)
        return None

class AuthHandler(Handler):
    def _can_handle(self, request):
        return "auth_token" not in request
    
    def _process(self, request):
        return "Auth failed"
```

**Pattern:** _______________

---

### Q40.
```python
class DataExporter(ABC):
    def export(self, data):
        self.validate(data)        # Common
        formatted = self.format(data)  # Varies
        self.save(formatted)       # Common
    
    def validate(self, data):
        if not data:
            raise ValueError("Empty data")
    
    @abstractmethod
    def format(self, data):
        pass
    
    def save(self, formatted):
        print(f"Saved: {formatted}")

class JSONExporter(DataExporter):
    def format(self, data):
        return json.dumps(data)

class XMLExporter(DataExporter):
    def format(self, data):
        return dict_to_xml(data)
```

**Pattern:** _______________

---

## Section 4: SOLID Principles (10 Questions)

*Identify which SOLID principle is violated or applied.*

### Q41.
```python
class Report:
    def __init__(self, data):
        self.data = data
    
    def generate(self):
        # Generate report content
        pass
    
    def save_to_file(self, filename):
        # Save to file
        pass
    
    def send_email(self, recipient):
        # Send report via email
        pass
    
    def print_report(self):
        # Print to printer
        pass
```

**Which principle is VIOLATED?** _______________

---

### Q42.
```python
class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

def total_area(shapes: list[Shape]):
    return sum(shape.area() for shape in shapes)
```

**Which principle is being FOLLOWED?** _______________

---

### Q43.
```python
class Bird:
    def fly(self):
        print("Flying...")

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")
```

**Which principle is VIOLATED?** _______________

---

### Q44.
```python
class Worker(ABC):
    @abstractmethod
    def work(self): pass
    
    @abstractmethod
    def eat(self): pass

class Robot(Worker):
    def work(self):
        print("Working...")
    
    def eat(self):
        pass  # Robots don't eat, but forced to implement
```

**Which principle is VIOLATED?** _______________

---

### Q45.
```python
class MySQLDatabase:
    def connect(self):
        # MySQL specific connection
        pass

class UserRepository:
    def __init__(self):
        self.db = MySQLDatabase()  # Direct dependency on concrete class
    
    def get_user(self, id):
        self.db.connect()
        # ...
```

**Which principle is VIOLATED?** _______________

---

### Q46.
```python
# Before
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

# Need to add color - modified existing class
class Rectangle:
    def __init__(self, width, height, color="white"):
        self.width = width
        self.height = height
        self.color = color
```

**Which principle is VIOLATED?** _______________

---

### Q47.
```python
class Database(ABC):
    @abstractmethod
    def connect(self): pass
    @abstractmethod
    def query(self, sql): pass

class MySQLDatabase(Database):
    def connect(self): ...
    def query(self, sql): ...

class PostgresDatabase(Database):
    def connect(self): ...
    def query(self, sql): ...

class UserService:
    def __init__(self, db: Database):  # Depends on abstraction
        self.db = db
```

**Which principle is being FOLLOWED?** _______________

---

### Q48.
```python
class Printer(ABC):
    @abstractmethod
    def print(self): pass

class Scanner(ABC):
    @abstractmethod
    def scan(self): pass

class Copier(ABC):
    @abstractmethod
    def copy(self): pass

# Simple printer only implements what it needs
class SimplePrinter(Printer):
    def print(self):
        print("Printing...")

# Multi-function device implements all
class MultiFunctionDevice(Printer, Scanner, Copier):
    def print(self): ...
    def scan(self): ...
    def copy(self): ...
```

**Which principle is being FOLLOWED?** _______________

---

### Q49.
```python
class PaymentProcessor:
    def process_payment(self, payment_type, amount):
        if payment_type == "credit":
            # credit card logic
            pass
        elif payment_type == "debit":
            # debit card logic
            pass
        elif payment_type == "paypal":
            # paypal logic
            pass
        # To add new payment type, must modify this class
```

**Which principle is VIOLATED?** _______________

---

### Q50.
```python
class EmailService:
    def send_email(self, to, subject, body):
        # Send email implementation
        pass

class SMSService:
    def send_sms(self, to, message):
        # Send SMS implementation
        pass

class NotificationService:
    def __init__(self, email_service: EmailService, sms_service: SMSService):
        self.email = email_service
        self.sms = sms_service
    
    def notify(self, user, message):
        self.email.send_email(user.email, "Notification", message)
        self.sms.send_sms(user.phone, message)
```

**Is this good or bad design? Why?** _______________

---

## Section 5: Design Decisions (10 Questions)

*Choose the best answer or explain your reasoning.*

### Q51.
You're designing a ride-sharing app. For the driver matching algorithm that can be:
- Nearest driver
- Highest rated
- Fastest ETA

Which pattern and why?

A) State - because the algorithm changes based on ride state  
B) Strategy - because the algorithm is chosen externally and can be swapped  
C) Factory - because we're creating different types of matchers  
D) Observer - because we need to notify when a match is found

**Answer:** ___

---

### Q52.
For a parking lot system, you need to track spot status (Available, Occupied, Reserved, Maintenance). Which pattern?

A) Strategy - different algorithms for different statuses  
B) State - behavior changes based on spot state  
C) Observer - to notify when status changes  
D) Factory - to create different spot types

**Answer:** ___

---

### Q53.
You're implementing a text editor with undo/redo for 20+ different operations. Which pattern combination is BEST?

A) Strategy for each operation type  
B) Command for each operation + Stack for history  
C) State for editor state + Observer for UI updates  
D) Factory for creating operations

**Answer:** ___

---

### Q54.
An order in an e-commerce system goes through: Created → Paid → Shipped → Delivered → Completed. Some transitions are invalid (e.g., can't ship unpaid order). Best pattern?

A) Strategy - to switch between order processing algorithms  
B) State - to encapsulate state-specific behavior and transitions  
C) Chain of Responsibility - to process order through stages  
D) Observer - to notify about state changes

**Answer:** ___

---

### Q55.
You need to add logging, caching, and authentication to an existing API client WITHOUT modifying its code. Which pattern?

A) Adapter - to adapt the interface  
B) Decorator - to add behavior by wrapping  
C) Proxy - to control access  
D) Either B or C would work, but B (Decorator) is better for stacking multiple concerns

**Answer:** ___

---

### Q56.
A chat application where users can send messages to:
- Individual users
- Groups
- Channels

Users shouldn't know about each other directly. Which pattern?

A) Observer - users observe each other  
B) Mediator - central hub manages all communication  
C) Strategy - different messaging strategies  
D) Command - encapsulate messages

**Answer:** ___

---

### Q57.
Creating a Pizza with size (S/M/L), crust (thin/thick/stuffed), and 15 possible toppings. Which pattern(s)?

A) Factory for pizza types  
B) Builder for construction + Decorator for toppings  
C) Strategy for different pizza algorithms  
D) Abstract Factory for pizza families

**Answer:** ___

---

### Q58.
A video player that can be in states: Stopped, Playing, Paused. Each state has different button behaviors (play/pause/stop). Which pattern?

A) Strategy - swap playing algorithms  
B) State - encapsulate state-specific button behavior  
C) Command - for button actions  
D) Observer - to update UI

**Answer:** ___

---

### Q59.
You need a configuration manager that loads settings once and is accessible throughout the app. BUT you also need to easily mock it for testing. Best approach?

A) Singleton - guaranteed one instance  
B) Singleton with dependency injection - testable singleton  
C) Static class - simpler than singleton  
D) Global variable - fastest access

**Answer:** ___

---

### Q60.
For a ride request that must pass through: UserAuth → PaymentCheck → FraudDetection → LocationValidation → PriceCalculation, where any step can reject. Which pattern?

A) Chain of Responsibility - each handler can process or reject  
B) Strategy - different validation strategies  
C) Template Method - fixed validation steps  
D) State - validation state machine

**Answer:** ___

---

## Section 6: Implementation Challenge (Bonus)

### Q61. Mini Design Challenge

Design a **Notification System** that:
1. Supports multiple channels (Email, SMS, Push, Slack)
2. Users can have preferences for which channels they want
3. Some notifications are urgent (send via all channels)
4. Some notifications are silent (just log, don't send)
5. Should be easy to add new channels

**List the patterns you would use and briefly explain why:**

```
Pattern 1: _______________ 
Reason: _______________________________________________

Pattern 2: _______________
Reason: _______________________________________________

Pattern 3: _______________
Reason: _______________________________________________
```

---

### Q62. Code Implementation

Implement a simple **State Pattern** for an ATM with states:
- Idle (waiting for card)
- CardInserted (waiting for PIN)
- Authenticated (ready for transaction)
- Transaction (processing)

Write the skeleton code (classes and key methods):

```python
# Write your implementation here








```

---

### Q63. Design Analysis

Given this code, identify ALL the problems and suggest patterns to fix them:

```python
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()
        self.emailer = SMTPEmailClient()
        self.logger = FileLogger()
    
    def place_order(self, order):
        # Validation
        if order.total < 0:
            raise ValueError("Invalid total")
        if not order.items:
            raise ValueError("No items")
        if order.status != "pending":
            raise ValueError("Invalid status")
        
        # Process based on payment type
        if order.payment_type == "credit":
            # Credit card processing
            pass
        elif order.payment_type == "paypal":
            # PayPal processing
            pass
        elif order.payment_type == "crypto":
            # Crypto processing
            pass
        
        # Save to database
        self.db.save(order)
        
        # Send confirmation based on preference
        if order.customer.email_preference:
            self.emailer.send(order.customer.email, "Order Confirmed")
        if order.customer.sms_preference:
            # SMS logic
            pass
        
        # Log
        self.logger.log(f"Order {order.id} placed")
        
        # Update inventory
        for item in order.items:
            item.product.stock -= item.quantity
            self.db.save(item.product)
```

**Problems and Solutions:**

```
Problem 1: _______________
Solution/Pattern: _______________

Problem 2: _______________
Solution/Pattern: _______________

Problem 3: _______________
Solution/Pattern: _______________

Problem 4: _______________
Solution/Pattern: _______________

Problem 5: _______________
Solution/Pattern: _______________
```

---

# ANSWER KEY

## Section 1: Pattern Identification

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | **Strategy** | Multiple shipping algorithms, client chooses |
| 2 | **Command** | Need undo/redo, encapsulate operations |
| 3 | **State** | Behavior varies by state, state transitions |
| 4 | **Strategy** | Multiple notification algorithms, swappable |
| 5 | **Decorator** | Stack add-ons dynamically |
| 6 | **Factory** | Create different character types at runtime |
| 7 | **Observer** | One-to-many notification on price change |
| 8 | **Proxy** | Control access (caching, logging, auth) |
| 9 | **Builder** | Many optional parameters |
| 10 | **State** | Machine states with different behaviors |
| 11 | **Singleton** | Exactly one instance needed |
| 12 | **Adapter** | Convert incompatible interface |
| 13 | **Chain of Responsibility** | Sequential checks, any can reject |
| 14 | **Composite** | Tree structure, uniform treatment |
| 15 | **Template Method** | Same algorithm skeleton, varying steps |
| 16 | **Facade** | Simplify access to multiple subsystems |
| 17 | **Observer** | Multiple views update when model changes |
| 18 | **Strategy** | Swap algorithms at runtime |
| 19 | **Strategy + Factory** | Factory to create, Strategy to process |
| 20 | **Abstract Factory** | Create families of related objects |

---

## Section 2: Pattern Comparison

| Q | Answer | Explanation |
|---|--------|-------------|
| 21 | **B** | Strategy = client chooses, State = internal transitions |
| 22 | **B** | Builder for many optional parameters |
| 23 | **A** | Decorator adds features, Proxy controls access |
| 24 | **B** | Mediator centralizes communication |
| 25 | **B** | Abstract Factory = families of related objects |
| 26 | **C** | Template = inheritance, Strategy = composition |
| 27 | **A** | Command = undo/queue, Strategy = swap algorithms |
| 28 | **C** | Adapter converts interfaces |
| 29 | **C** | Template Method uses inheritance |
| 30 | **C** | State classes typically handle transitions |

---

## Section 3: Code Analysis

| Q | Answer |
|---|--------|
| 31 | **Factory** (Simple Factory) |
| 32 | **Decorator** |
| 33 | **Observer** |
| 34 | **State** |
| 35 | **Builder** |
| 36 | **Singleton** |
| 37 | **Strategy** |
| 38 | **Command** |
| 39 | **Chain of Responsibility** |
| 40 | **Template Method** |

---

## Section 4: SOLID Principles

| Q | Answer | Explanation |
|---|--------|-------------|
| 41 | **SRP (Single Responsibility)** | Report class does too many things |
| 42 | **OCP (Open-Closed) & LSP** | New shapes via extension, substitutable |
| 43 | **LSP (Liskov Substitution)** | Penguin can't substitute Bird |
| 44 | **ISP (Interface Segregation)** | Robot forced to implement eat() |
| 45 | **DIP (Dependency Inversion)** | Depends on concrete class, not abstraction |
| 46 | **OCP (Open-Closed)** | Modified existing class instead of extending |
| 47 | **DIP (Dependency Inversion)** | Depends on Database abstraction |
| 48 | **ISP (Interface Segregation)** | Small, focused interfaces |
| 49 | **OCP (Open-Closed)** | Must modify to add new payment types |
| 50 | **Mixed** | Violates DIP (concrete deps), but follows SRP somewhat |

---

## Section 5: Design Decisions

| Q | Answer | Explanation |
|---|--------|-------------|
| 51 | **B** | Strategy - algorithms swapped externally |
| 52 | **B** | State - behavior varies with spot state |
| 53 | **B** | Command + Stack for undo/redo history |
| 54 | **B** | State - encapsulates valid transitions |
| 55 | **D** | Decorator stacks concerns, Proxy works too |
| 56 | **B** | Mediator - central communication hub |
| 57 | **B** | Builder for base, Decorator for toppings |
| 58 | **B** | State - button behavior varies by state |
| 59 | **B** | Singleton + DI for testability |
| 60 | **A** | Chain of Responsibility - pipeline with rejection |

---

## Section 6: Implementation Challenge

### Q61. Notification System Patterns

| Pattern | Reason |
|---------|--------|
| **Strategy** | Different notification channel algorithms (Email, SMS, etc.) |
| **Factory** | Create appropriate notifier based on channel type |
| **Observer** | User preferences can observe and react to notifications |
| **Decorator** | Add urgency behavior, logging without changing core |
| **Chain of Responsibility** | (Alternative) Notification goes through channels in order |

### Q62. ATM State Pattern

```python
from abc import ABC, abstractmethod

class ATMState(ABC):
    @abstractmethod
    def insert_card(self, atm): pass
    @abstractmethod
    def enter_pin(self, atm, pin): pass
    @abstractmethod
    def withdraw(self, atm, amount): pass
    @abstractmethod
    def eject_card(self, atm): pass

class IdleState(ATMState):
    def insert_card(self, atm):
        print("Card inserted")
        atm.set_state(CardInsertedState())
    
    def enter_pin(self, atm, pin):
        print("Error: Insert card first")
    
    def withdraw(self, atm, amount):
        print("Error: Insert card first")
    
    def eject_card(self, atm):
        print("Error: No card to eject")

class CardInsertedState(ATMState):
    def insert_card(self, atm):
        print("Error: Card already inserted")
    
    def enter_pin(self, atm, pin):
        if atm.validate_pin(pin):
            print("PIN correct")
            atm.set_state(AuthenticatedState())
        else:
            print("Wrong PIN")
    
    def withdraw(self, atm, amount):
        print("Error: Enter PIN first")
    
    def eject_card(self, atm):
        print("Card ejected")
        atm.set_state(IdleState())

class AuthenticatedState(ATMState):
    def insert_card(self, atm):
        print("Error: Card already inserted")
    
    def enter_pin(self, atm, pin):
        print("Error: Already authenticated")
    
    def withdraw(self, atm, amount):
        print(f"Processing withdrawal of ${amount}")
        atm.set_state(TransactionState())
        # After transaction completes, would return to Authenticated or Idle
    
    def eject_card(self, atm):
        print("Card ejected")
        atm.set_state(IdleState())

class ATM:
    def __init__(self):
        self._state = IdleState()
    
    def set_state(self, state):
        self._state = state
    
    def insert_card(self):
        self._state.insert_card(self)
    
    def enter_pin(self, pin):
        self._state.enter_pin(self, pin)
    
    def withdraw(self, amount):
        self._state.withdraw(self, amount)
    
    def eject_card(self):
        self._state.eject_card(self)
    
    def validate_pin(self, pin):
        return pin == "1234"
```

### Q63. OrderService Problems

| Problem | Solution/Pattern |
|---------|------------------|
| **Hard-coded dependencies** (MySQLDatabase, SMTPEmailClient, FileLogger) | **Dependency Injection** + **DIP** |
| **Payment type if-else** | **Strategy Pattern** (PaymentStrategy interface) |
| **Notification if-else** | **Observer Pattern** or **Strategy Pattern** |
| **Multiple responsibilities** (validation, payment, notification, logging, inventory) | **SRP** - Split into separate services |
| **Direct database coupling** | **Repository Pattern** + **DIP** |
| **No abstraction for external services** | **Adapter Pattern** for email/SMS services |

---

## Scoring Guide

| Section | Max Points |
|---------|------------|
| Section 1 (Q1-Q20) | 20 points |
| Section 2 (Q21-Q30) | 10 points |
| Section 3 (Q31-Q40) | 10 points |
| Section 4 (Q41-Q50) | 10 points |
| Section 5 (Q51-Q60) | 10 points |
| Section 6 (Q61-Q63) | 10 points |
| **Total** | **70 points** |

### Score Interpretation

| Score | Level | Recommendation |
|-------|-------|----------------|
| 60-70 | Expert | Ready for interview |
| 50-59 | Advanced | Review weak areas |
| 40-49 | Intermediate | More practice needed |
| 30-39 | Beginner | Study fundamentals |
| <30 | Novice | Start from basics |

---

Good luck! Review your weak areas and practice implementing the patterns you got wrong.

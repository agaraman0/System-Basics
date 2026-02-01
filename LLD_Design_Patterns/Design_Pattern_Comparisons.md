# Design Pattern Comparisons

> **Purpose:** Clear side-by-side comparisons of commonly confused patterns.

---

## Table of Contents

1. [Factory vs Builder](#1-factory-vs-builder)
2. [Strategy vs State](#2-strategy-vs-state)
3. [Decorator vs Proxy](#3-decorator-vs-proxy)
4. [Observer vs Mediator](#4-observer-vs-mediator)
5. [Factory vs Abstract Factory](#5-factory-vs-abstract-factory)
6. [Adapter vs Facade](#6-adapter-vs-facade)
7. [Template Method vs Strategy](#7-template-method-vs-strategy)
8. [Command vs Strategy](#8-command-vs-strategy)

---

## 1. Factory vs Builder

Both create objects, but solve **different problems**.

### Quick Comparison

| Aspect | Factory | Builder |
|--------|---------|---------|
| **Problem** | "Which class to instantiate?" | "How to construct complex object?" |
| **Focus** | Object **type** selection | Object **construction** process |
| **Parameters** | Few, usually same for all types | Many, often optional |
| **Returns** | Different types (polymorphic) | Same type, different configurations |
| **When to use** | Runtime type decision | Step-by-step construction |

### Factory Pattern

**Problem:** I don't know which concrete class to create until runtime.

```python
# FACTORY: "What TYPE of vehicle?"

class VehicleFactory:
    def create(self, vehicle_type: str) -> Vehicle:
        if vehicle_type == "UberX":
            return UberX()      # Different class
        elif vehicle_type == "UberXL":
            return UberXL()     # Different class
        elif vehicle_type == "UberBlack":
            return UberBlack()  # Different class

# Usage - client doesn't know concrete class
vehicle = VehicleFactory().create("UberX")
```

**Characteristics:**
- Returns **different types** (subclasses)
- Creation logic in **one place**
- Client is **decoupled** from concrete classes
- Usually **one method call**

### Builder Pattern

**Problem:** Object has many parameters, most are optional, construction is complex.

```python
# BUILDER: "HOW to configure this ride request?"

class RideRequest:
    # Imagine 15+ fields here...
    pass

class RideRequestBuilder:
    def __init__(self):
        self._request = RideRequest()
    
    def pickup(self, location: str):
        self._request.pickup = location
        return self
    
    def dropoff(self, location: str):
        self._request.dropoff = location
        return self
    
    def vehicle_type(self, vtype: str):
        self._request.vehicle_type = vtype
        return self
    
    def child_seats(self, count: int):
        self._request.child_seats = count
        return self
    
    def pet_friendly(self):
        self._request.pet_friendly = True
        return self
    
    def promo_code(self, code: str):
        self._request.promo_code = code
        return self
    
    def build(self) -> RideRequest:
        # Validate and return
        return self._request

# Usage - configure step by step
request = (RideRequestBuilder()
    .pickup("Airport")
    .dropoff("Downtown")
    .vehicle_type("UberXL")
    .child_seats(2)
    .pet_friendly()
    .build())
```

**Characteristics:**
- Returns **same type**, different configurations
- **Fluent interface** (method chaining)
- Handles **optional parameters** cleanly
- **Multiple method calls** before build()

### Visual Comparison

```
FACTORY:
                    ┌─► UberX
Input: "type" ──►  Factory ──┼─► UberXL
                    └─► UberBlack
                    
(Different CLASSES come out)


BUILDER:
                    ┌─ pickup()
                    ├─ dropoff()
Step by step ──►  Builder ──┼─ vehicle()  ──► RideRequest
                    ├─ childSeats()
                    └─ build()
                    
(Same CLASS, different CONFIGURATION)
```

### When to Use Which?

| Situation | Use |
|-----------|-----|
| "Create car OR bike OR truck" | **Factory** |
| "Create car with optional sunroof, GPS, leather seats" | **Builder** |
| Type unknown until runtime | **Factory** |
| Many optional parameters (>4) | **Builder** |
| Avoid telescoping constructors | **Builder** |
| Decouple client from concrete classes | **Factory** |
| Need immutable object with many fields | **Builder** |

### Combined Example

```python
# FACTORY: Which vehicle type?
class VehicleFactory:
    def create(self, type: str) -> Vehicle:
        types = {"UberX": UberX, "UberXL": UberXL, "UberBlack": UberBlack}
        return types[type]()

# BUILDER: How to configure the ride request?
class RideRequestBuilder:
    def pickup(self, loc): ...
    def dropoff(self, loc): ...
    def vehicle_type(self, t): ...
    def scheduled_time(self, t): ...
    def child_seats(self, n): ...
    def promo(self, code): ...
    def build(self): ...

# Using BOTH together
request = (RideRequestBuilder()
    .pickup("Airport")
    .dropoff("Hotel")
    .vehicle_type("UberXL")
    .child_seats(2)
    .build())

vehicle = VehicleFactory().create(request.vehicle_type)
```

### Anti-Pattern Check

```python
# ❌ DON'T use Factory for this (only one type, many params)
VehicleFactory().create("car", color="red", seats=4, sunroof=True, gps=True)

# ✅ Use Builder instead
CarBuilder().color("red").seats(4).sunroof().gps().build()

# ❌ DON'T use Builder for this (choosing between types)
CarBuilder().type("sedan").build()  # Wrong!
CarBuilder().type("suv").build()    # Wrong!

# ✅ Use Factory instead
VehicleFactory().create("sedan")
VehicleFactory().create("suv")
```

### Interview One-Liner

> **Factory:** "I need to decide **which class** to instantiate at runtime."
> 
> **Builder:** "I need to construct a **complex object** with many optional parameters."

---

## 2. Strategy vs State

Both change behavior, but for **different reasons**.

### Quick Comparison

| Aspect | Strategy | State |
|--------|----------|-------|
| **Problem** | Multiple algorithms for same task | Behavior changes with internal state |
| **Who decides** | Client chooses algorithm | Object changes its own state |
| **Awareness** | Strategies don't know about each other | States know about transitions |
| **Change trigger** | External (client sets it) | Internal (object changes itself) |
| **Example** | Pricing: normal, surge, discount | Ride: requested → in_progress → completed |

### Strategy Pattern

**Problem:** I have multiple ways to do something, client picks which one.

```python
# STRATEGY: Client CHOOSES the algorithm

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, distance: float) -> float:
        pass

class NormalPricing(PricingStrategy):
    def calculate(self, distance: float) -> float:
        return distance * 10

class SurgePricing(PricingStrategy):
    def calculate(self, distance: float) -> float:
        return distance * 10 * 2.5

class Ride:
    def __init__(self):
        self._pricing: PricingStrategy = NormalPricing()
    
    def set_pricing(self, strategy: PricingStrategy):
        """CLIENT decides which strategy to use"""
        self._pricing = strategy
    
    def get_fare(self, distance: float) -> float:
        return self._pricing.calculate(distance)

# Usage - CLIENT controls the strategy
ride = Ride()
ride.set_pricing(SurgePricing())  # Client chooses
fare = ride.get_fare(10)
```

### State Pattern

**Problem:** Object behaves differently based on its internal state.

```python
# STATE: Object ITSELF changes state based on actions

class RideState(ABC):
    @abstractmethod
    def cancel(self, ride: 'Ride'):
        pass
    
    @abstractmethod
    def start(self, ride: 'Ride'):
        pass

class RequestedState(RideState):
    def cancel(self, ride: 'Ride'):
        print("Cancelled - no fee")
        ride._state = CancelledState()  # State changes ITSELF
    
    def start(self, ride: 'Ride'):
        print("Error: Need driver first")

class DriverAssignedState(RideState):
    def cancel(self, ride: 'Ride'):
        print("Cancelled - $5 fee")
        ride._state = CancelledState()  # State changes ITSELF
    
    def start(self, ride: 'Ride'):
        print("Ride started!")
        ride._state = InProgressState()  # State changes ITSELF

class Ride:
    def __init__(self):
        self._state: RideState = RequestedState()
    
    def cancel(self):
        self._state.cancel(self)  # Delegate to current state
    
    def start(self):
        self._state.start(self)  # Delegate to current state

# Usage - OBJECT controls its own state
ride = Ride()  # Starts in RequestedState
ride.start()   # Error - need driver
ride.assign_driver()  # Now in DriverAssignedState
ride.start()   # Success! Now in InProgressState
```

### Visual Comparison

```
STRATEGY:
Client ──► sets strategy ──► Object uses it
(External control)

         ┌─► NormalPricing
Client ──┼─► SurgePricing    ──► Ride.get_fare()
         └─► PoolPricing


STATE:
Object ──► action ──► state changes ──► behavior changes
(Internal control)

Ride: Requested ──► DriverAssigned ──► InProgress ──► Completed
      (cancel=free)  (cancel=$5 fee)   (cancel=error)
```

### Key Differences

| Strategy | State |
|----------|-------|
| Algorithms are **independent** | States **know about each other** |
| Client **injects** the algorithm | Object **transitions** itself |
| Strategies **don't change** during use | States **change frequently** |
| "I want to use THIS algorithm" | "I AM in this state" |

### When to Use Which?

| Situation | Use |
|-----------|-----|
| Multiple algorithms, client chooses | **Strategy** |
| Object lifecycle with transitions | **State** |
| Behavior varies by external choice | **Strategy** |
| Behavior varies by internal condition | **State** |
| Algorithms are interchangeable | **Strategy** |
| Some operations invalid in some states | **State** |

### Interview One-Liner

> **Strategy:** "Client chooses **which algorithm** to use."
> 
> **State:** "Object changes **its own behavior** based on internal state."

---

## 3. Decorator vs Proxy

Both wrap an object, but for **different purposes**.

### Quick Comparison

| Aspect | Decorator | Proxy |
|--------|-----------|-------|
| **Purpose** | Add new behavior/features | Control access to object |
| **Focus** | Enhancement | Protection/Control |
| **Wrapping** | Multiple decorators stackable | Usually single proxy |
| **Interface** | Same as wrapped object | Same as wrapped object |
| **Example** | Ride + WiFi + ChildSeat | Lazy loading, caching, access control |

### Decorator Pattern

**Problem:** Add features dynamically without subclassing.

```python
# DECORATOR: Add features by wrapping

class RideService(ABC):
    @abstractmethod
    def get_cost(self) -> float:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass

class BasicRide(RideService):
    def get_cost(self) -> float:
        return 100.0
    
    def get_description(self) -> str:
        return "Basic Ride"

class WifiDecorator(RideService):
    def __init__(self, ride: RideService):
        self._ride = ride
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 5.0  # ADD to cost
    
    def get_description(self) -> str:
        return self._ride.get_description() + " + WiFi"

class ChildSeatDecorator(RideService):
    def __init__(self, ride: RideService):
        self._ride = ride
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 10.0  # ADD to cost
    
    def get_description(self) -> str:
        return self._ride.get_description() + " + Child Seat"

# Usage - STACK decorators
ride = BasicRide()
ride = WifiDecorator(ride)
ride = ChildSeatDecorator(ride)
print(ride.get_description())  # "Basic Ride + WiFi + Child Seat"
print(ride.get_cost())         # 115.0
```

### Proxy Pattern

**Problem:** Control access to an object (lazy load, cache, auth, logging).

```python
# PROXY: Control access to object

class DriverService(ABC):
    @abstractmethod
    def get_driver_info(self, driver_id: str) -> dict:
        pass

class RealDriverService(DriverService):
    def get_driver_info(self, driver_id: str) -> dict:
        # Expensive database call
        print(f"  [DB] Fetching driver {driver_id}...")
        return {"id": driver_id, "name": "John", "rating": 4.9}

class CachingProxy(DriverService):
    def __init__(self, real_service: DriverService):
        self._real_service = real_service
        self._cache = {}
    
    def get_driver_info(self, driver_id: str) -> dict:
        if driver_id not in self._cache:
            print(f"  [Cache] Miss - calling real service")
            self._cache[driver_id] = self._real_service.get_driver_info(driver_id)
        else:
            print(f"  [Cache] Hit!")
        return self._cache[driver_id]

class AuthProxy(DriverService):
    def __init__(self, real_service: DriverService, user_role: str):
        self._real_service = real_service
        self._user_role = user_role
    
    def get_driver_info(self, driver_id: str) -> dict:
        if self._user_role not in ["admin", "support"]:
            raise PermissionError("Access denied")
        return self._real_service.get_driver_info(driver_id)

# Usage - CONTROL access
real_service = RealDriverService()
cached_service = CachingProxy(real_service)

cached_service.get_driver_info("D001")  # Cache miss, DB call
cached_service.get_driver_info("D001")  # Cache hit, no DB call
```

### Visual Comparison

```
DECORATOR:
Client ──► Decorator1 ──► Decorator2 ──► RealObject
           (adds $5)      (adds $10)     (base $100)
           
Result: $115 (features STACKED)


PROXY:
Client ──► Proxy ──► RealObject (maybe)
           │
           ├─ Check cache first
           ├─ Check permissions
           └─ Log access
           
Result: Controlled access
```

### Types of Proxies

| Proxy Type | Purpose |
|------------|---------|
| **Caching Proxy** | Cache expensive results |
| **Virtual Proxy** | Lazy loading (create object on demand) |
| **Protection Proxy** | Access control/authorization |
| **Logging Proxy** | Log all method calls |
| **Remote Proxy** | Represent remote object locally |

### When to Use Which?

| Situation | Use |
|-----------|-----|
| Add optional features dynamically | **Decorator** |
| Cache expensive operations | **Proxy** |
| Stack multiple enhancements | **Decorator** |
| Control access/permissions | **Proxy** |
| Avoid class explosion from combinations | **Decorator** |
| Lazy load expensive objects | **Proxy** |

### Interview One-Liner

> **Decorator:** "Add **new features** to an object by wrapping it."
> 
> **Proxy:** "Control **access** to an object (cache, auth, lazy load)."

---

## 4. Observer vs Mediator

Both handle communication between objects, but differently.

### Quick Comparison

| Aspect | Observer | Mediator |
|--------|----------|----------|
| **Communication** | One-to-many | Many-to-many through central hub |
| **Coupling** | Subject knows observers exist | Objects only know mediator |
| **Direction** | Subject → Observers (broadcast) | Bidirectional through mediator |
| **Example** | Ride status → notify all services | Chat room, air traffic control |

### Observer Pattern

**Problem:** When one object changes, notify multiple interested objects.

```python
# OBSERVER: One-to-many broadcast

class RideObserver(ABC):
    @abstractmethod
    def on_ride_update(self, ride_id: str, status: str):
        pass

class RiderNotifier(RideObserver):
    def on_ride_update(self, ride_id: str, status: str):
        print(f"[Rider] Your ride {ride_id} is now {status}")

class DriverNotifier(RideObserver):
    def on_ride_update(self, ride_id: str, status: str):
        print(f"[Driver] Ride {ride_id} status: {status}")

class AnalyticsService(RideObserver):
    def on_ride_update(self, ride_id: str, status: str):
        print(f"[Analytics] Logged: {ride_id} -> {status}")

class Ride:
    def __init__(self, ride_id: str):
        self.ride_id = ride_id
        self._observers: list = []
        self._status = "requested"
    
    def add_observer(self, observer: RideObserver):
        self._observers.append(observer)
    
    def set_status(self, status: str):
        self._status = status
        # BROADCAST to all observers
        for observer in self._observers:
            observer.on_ride_update(self.ride_id, status)

# Usage
ride = Ride("R001")
ride.add_observer(RiderNotifier())
ride.add_observer(DriverNotifier())
ride.add_observer(AnalyticsService())
ride.set_status("driver_assigned")  # All three notified
```

### Mediator Pattern

**Problem:** Multiple objects need to communicate, but direct coupling is messy.

```python
# MEDIATOR: Central hub for communication

class ChatMediator:
    def __init__(self):
        self._users: dict = {}
    
    def register(self, user_id: str, user: 'ChatUser'):
        self._users[user_id] = user
    
    def send_message(self, from_id: str, to_id: str, message: str):
        if to_id in self._users:
            self._users[to_id].receive(from_id, message)
    
    def broadcast(self, from_id: str, message: str):
        for user_id, user in self._users.items():
            if user_id != from_id:
                user.receive(from_id, message)

class ChatUser:
    def __init__(self, user_id: str, mediator: ChatMediator):
        self.user_id = user_id
        self._mediator = mediator
        mediator.register(user_id, self)
    
    def send(self, to_id: str, message: str):
        # Don't know other users, only mediator
        self._mediator.send_message(self.user_id, to_id, message)
    
    def receive(self, from_id: str, message: str):
        print(f"[{self.user_id}] Message from {from_id}: {message}")

# Usage - users only know mediator, not each other
mediator = ChatMediator()
rider = ChatUser("rider", mediator)
driver = ChatUser("driver", mediator)
support = ChatUser("support", mediator)

rider.send("driver", "Where are you?")
driver.send("rider", "2 minutes away!")
```

### Visual Comparison

```
OBSERVER:
              ┌──► Observer1
Subject ──────┼──► Observer2  (Broadcast)
              └──► Observer3

Subject knows about observers, observers are passive.


MEDIATOR:
Object1 ◄───┐
            │
Object2 ◄───┼───► Mediator
            │
Object3 ◄───┘

Objects only know mediator, mediator coordinates all.
```

### When to Use Which?

| Situation | Use |
|-----------|-----|
| One object broadcasts to many | **Observer** |
| Many objects communicate with each other | **Mediator** |
| Passive listeners | **Observer** |
| Active bi-directional communication | **Mediator** |
| Event-driven (status changes) | **Observer** |
| Complex interactions (chat, trading) | **Mediator** |

### Interview One-Liner

> **Observer:** "One object **broadcasts** changes to many listeners."
> 
> **Mediator:** "Objects communicate **through a central hub**, not directly."

---

## 5. Factory vs Abstract Factory

Both create objects, but at different levels.

### Quick Comparison

| Aspect | Factory | Abstract Factory |
|--------|---------|------------------|
| **Creates** | One product | Family of related products |
| **Method** | Single create method | Multiple create methods |
| **Example** | Create a Vehicle | Create Vehicle + Driver + Insurance (family) |

### Factory Pattern

```python
# FACTORY: Create ONE type of object

class VehicleFactory:
    def create(self, type: str) -> Vehicle:
        if type == "car":
            return Car()
        elif type == "bike":
            return Bike()
```

### Abstract Factory Pattern

```python
# ABSTRACT FACTORY: Create FAMILY of related objects

class RideServiceFactory(ABC):
    @abstractmethod
    def create_vehicle(self) -> Vehicle:
        pass
    
    @abstractmethod
    def create_driver(self) -> Driver:
        pass
    
    @abstractmethod
    def create_insurance(self) -> Insurance:
        pass

class UberXFactory(RideServiceFactory):
    def create_vehicle(self) -> Vehicle:
        return EconomyCar()
    
    def create_driver(self) -> Driver:
        return StandardDriver()
    
    def create_insurance(self) -> Insurance:
        return BasicInsurance()

class UberBlackFactory(RideServiceFactory):
    def create_vehicle(self) -> Vehicle:
        return LuxuryCar()
    
    def create_driver(self) -> Driver:
        return PremiumDriver()
    
    def create_insurance(self) -> Insurance:
        return PremiumInsurance()

# Usage - get entire family of compatible objects
factory = UberBlackFactory()
vehicle = factory.create_vehicle()    # LuxuryCar
driver = factory.create_driver()      # PremiumDriver
insurance = factory.create_insurance() # PremiumInsurance
```

### Interview One-Liner

> **Factory:** "Create **one object** based on type."
> 
> **Abstract Factory:** "Create **family of related objects** that work together."

---

## 6. Adapter vs Facade

Both wrap other code, but for different reasons.

### Quick Comparison

| Aspect | Adapter | Facade |
|--------|---------|--------|
| **Purpose** | Make incompatible interfaces work together | Simplify complex subsystem |
| **Changes** | Converts interface | Provides simpler interface |
| **Scope** | Usually wraps one class | Wraps entire subsystem |

### Adapter Pattern

```python
# ADAPTER: Convert interface A to interface B

# Old payment system with different interface
class LegacyPaymentGateway:
    def make_payment(self, amount_cents: int, card_num: str):
        print(f"Legacy: Charging {amount_cents} cents to {card_num}")

# Your expected interface
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount_dollars: float, payment_method: dict):
        pass

# ADAPTER: Makes legacy work with new interface
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self, legacy: LegacyPaymentGateway):
        self._legacy = legacy
    
    def process(self, amount_dollars: float, payment_method: dict):
        # Convert to legacy format
        amount_cents = int(amount_dollars * 100)
        card_num = payment_method["card_number"]
        self._legacy.make_payment(amount_cents, card_num)

# Usage
legacy = LegacyPaymentGateway()
processor = LegacyPaymentAdapter(legacy)
processor.process(25.50, {"card_number": "1234-5678"})
```

### Facade Pattern

```python
# FACADE: Simplify complex subsystem

class DriverService:
    def find_driver(self, location): ...

class PricingService:
    def calculate_fare(self, pickup, dropoff): ...

class PaymentService:
    def charge(self, user_id, amount): ...

class NotificationService:
    def notify_rider(self, rider_id, message): ...
    def notify_driver(self, driver_id, message): ...

# FACADE: Simple interface to complex subsystem
class RideBookingFacade:
    def __init__(self):
        self._driver_service = DriverService()
        self._pricing_service = PricingService()
        self._payment_service = PaymentService()
        self._notification_service = NotificationService()
    
    def book_ride(self, rider_id: str, pickup: str, dropoff: str):
        """One simple method hides all complexity"""
        driver = self._driver_service.find_driver(pickup)
        fare = self._pricing_service.calculate_fare(pickup, dropoff)
        self._payment_service.charge(rider_id, fare)
        self._notification_service.notify_rider(rider_id, "Ride booked!")
        self._notification_service.notify_driver(driver.id, "New ride!")
        return {"driver": driver, "fare": fare}

# Usage - client only knows facade
facade = RideBookingFacade()
facade.book_ride("U123", "Airport", "Downtown")  # Simple!
```

### Interview One-Liner

> **Adapter:** "Convert **incompatible interface** to expected one."
> 
> **Facade:** "Provide **simple interface** to complex subsystem."

---

## 7. Template Method vs Strategy

Both vary algorithm steps, but differently.

### Quick Comparison

| Aspect | Template Method | Strategy |
|--------|-----------------|----------|
| **Variation** | Override specific steps | Replace entire algorithm |
| **Control** | Base class controls flow | Client controls choice |
| **Inheritance** | Uses inheritance | Uses composition |
| **Flexibility** | Fixed skeleton | Fully interchangeable |

### Template Method

```python
# TEMPLATE: Fixed skeleton, override steps

class BookingTemplate(ABC):
    def book(self, rider_id, pickup, dropoff):
        """FIXED skeleton - cannot be overridden"""
        self.validate(rider_id, pickup, dropoff)  # Common
        driver = self.find_driver(pickup)          # Varies
        fare = self.calculate_fare(pickup, dropoff) # Varies
        return self.create_booking(rider_id, driver, fare)  # Common
    
    def validate(self, rider_id, pickup, dropoff):
        # Common implementation
        pass
    
    @abstractmethod
    def find_driver(self, pickup):
        pass  # Subclass implements
    
    @abstractmethod
    def calculate_fare(self, pickup, dropoff):
        pass  # Subclass implements

class UberXBooking(BookingTemplate):
    def find_driver(self, pickup):
        return find_nearest_driver(pickup)
    
    def calculate_fare(self, pickup, dropoff):
        return distance * 10

class UberBlackBooking(BookingTemplate):
    def find_driver(self, pickup):
        return find_premium_driver(pickup)
    
    def calculate_fare(self, pickup, dropoff):
        return distance * 25
```

### Strategy

```python
# STRATEGY: Replace entire algorithm

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, distance): pass

class NormalPricing(PricingStrategy):
    def calculate(self, distance):
        return distance * 10

class SurgePricing(PricingStrategy):
    def calculate(self, distance):
        return distance * 10 * 2.5

class Ride:
    def __init__(self, strategy: PricingStrategy):
        self._strategy = strategy  # Composition, not inheritance
    
    def set_strategy(self, strategy: PricingStrategy):
        self._strategy = strategy
    
    def get_fare(self, distance):
        return self._strategy.calculate(distance)
```

### Interview One-Liner

> **Template Method:** "Define **algorithm skeleton**, let subclasses override steps."
> 
> **Strategy:** "**Swap entire algorithm** at runtime via composition."

---

## 8. Command vs Strategy

Both encapsulate behavior, but for different purposes.

### Quick Comparison

| Aspect | Command | Strategy |
|--------|---------|----------|
| **Purpose** | Encapsulate request for undo/queue | Encapsulate algorithm for swapping |
| **State** | Has state (for undo) | Usually stateless |
| **Features** | Undo, redo, queue, log | Runtime algorithm switching |
| **Focus** | WHAT to do | HOW to do it |

### Command

```python
# COMMAND: Encapsulate request + support undo

class Command(ABC):
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def undo(self): pass

class BookRideCommand(Command):
    def __init__(self, ride_service, ride_id, rider_id):
        self.ride_service = ride_service
        self.ride_id = ride_id
        self.rider_id = rider_id
        self._was_executed = False
    
    def execute(self):
        self.ride_service.create_ride(self.ride_id, self.rider_id)
        self._was_executed = True
    
    def undo(self):
        if self._was_executed:
            self.ride_service.cancel_ride(self.ride_id)

# Usage - support undo, queue, history
history = []
cmd = BookRideCommand(service, "R001", "U123")
cmd.execute()
history.append(cmd)

# Later: undo
history.pop().undo()
```

### Strategy

```python
# STRATEGY: Swap algorithm

class MatchingStrategy(ABC):
    @abstractmethod
    def find_driver(self, location): pass

class NearestDriverStrategy(MatchingStrategy):
    def find_driver(self, location):
        return find_by_distance(location)

class HighestRatedStrategy(MatchingStrategy):
    def find_driver(self, location):
        return find_by_rating(location)

# Usage - swap algorithm
class RideService:
    def __init__(self, strategy: MatchingStrategy):
        self._strategy = strategy
    
    def match_driver(self, location):
        return self._strategy.find_driver(location)
```

### Interview One-Liner

> **Command:** "Encapsulate request as object to **undo/queue/log**."
> 
> **Strategy:** "Encapsulate algorithm to **swap at runtime**."

---

## Quick Reference Table

| Confused Pair | Key Difference |
|---------------|----------------|
| Factory vs Builder | **Type selection** vs **Complex construction** |
| Strategy vs State | **Client chooses** vs **Object transitions** |
| Decorator vs Proxy | **Add features** vs **Control access** |
| Observer vs Mediator | **Broadcast** vs **Central hub** |
| Factory vs Abstract Factory | **One product** vs **Product family** |
| Adapter vs Facade | **Convert interface** vs **Simplify subsystem** |
| Template vs Strategy | **Override steps** vs **Replace algorithm** |
| Command vs Strategy | **Undo/queue** vs **Swap algorithm** |

---

## Interview Cheat Sheet

When asked "What's the difference between X and Y?":

1. **State the core purpose of each** (one sentence each)
2. **Give the key difference** (one sentence)
3. **Give a quick example** for each
4. **Say when you'd use each**

**Example answer for "Factory vs Builder":**

> "Factory is about deciding **which class** to instantiate at runtime - like creating UberX vs UberBlack vehicles. Builder is about constructing a **complex object** step by step with many optional parameters - like building a RideRequest with pickup, dropoff, promo code, child seats, etc.
> 
> The key difference is Factory returns **different types**, while Builder returns the **same type** with different configurations.
> 
> I'd use Factory when I don't know the concrete class until runtime, and Builder when I have more than 4-5 parameters, especially optional ones."

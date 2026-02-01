# Design Patterns Masterclass for LLD Interviews

> **Goal:** Master the essential design patterns with practical, Uber-relevant examples.
> **Approach:** Each pattern includes: Problem → Solution → Code → When to Use → Interview Tip

---

## Table of Contents

1. [Strategy Pattern](#1-strategy-pattern) ⭐⭐⭐
2. [Factory Pattern](#2-factory-pattern) ⭐⭐⭐
3. [Singleton Pattern](#3-singleton-pattern) ⭐⭐
4. [Observer Pattern](#4-observer-pattern) ⭐⭐⭐
5. [State Pattern](#5-state-pattern) ⭐⭐⭐
6. [Decorator Pattern](#6-decorator-pattern) ⭐⭐
7. [Builder Pattern](#7-builder-pattern) ⭐⭐
8. [Command Pattern](#8-command-pattern) ⭐⭐
9. [Template Method Pattern](#9-template-method-pattern) ⭐
10. [Chain of Responsibility](#10-chain-of-responsibility-pattern) ⭐⭐

⭐ = Interview Frequency

---

## 1. Strategy Pattern

### The Problem
Uber needs different pricing algorithms:
- Normal pricing
- Surge pricing (high demand)
- Discounted pricing (promotions)
- Pool pricing (shared rides)

**Bad approach:** Giant if-else in one class

```python
# ❌ BAD - Violates Open-Closed Principle
class RideService:
    def calculate_fare(self, distance, pricing_type):
        if pricing_type == "normal":
            return distance * 10
        elif pricing_type == "surge":
            return distance * 10 * 2.5
        elif pricing_type == "discount":
            return distance * 10 * 0.8
        elif pricing_type == "pool":
            return distance * 10 * 0.6
        # Adding new pricing = modifying this class 😞
```

### The Solution: Strategy Pattern

**Define a family of algorithms, encapsulate each one, and make them interchangeable.**

```python
from abc import ABC, abstractmethod

# Step 1: Define the Strategy Interface
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, distance_km: float, base_rate: float) -> float:
        pass

# Step 2: Implement Concrete Strategies
class NormalPricing(PricingStrategy):
    def calculate_fare(self, distance_km: float, base_rate: float) -> float:
        return distance_km * base_rate

class SurgePricing(PricingStrategy):
    def __init__(self, surge_multiplier: float = 2.0):
        self.surge_multiplier = surge_multiplier
    
    def calculate_fare(self, distance_km: float, base_rate: float) -> float:
        return distance_km * base_rate * self.surge_multiplier

class DiscountPricing(PricingStrategy):
    def __init__(self, discount_percent: float = 20):
        self.discount_percent = discount_percent
    
    def calculate_fare(self, distance_km: float, base_rate: float) -> float:
        base_fare = distance_km * base_rate
        return base_fare * (1 - self.discount_percent / 100)

class PoolPricing(PricingStrategy):
    def __init__(self, num_riders: int = 2):
        self.num_riders = num_riders
    
    def calculate_fare(self, distance_km: float, base_rate: float) -> float:
        base_fare = distance_km * base_rate
        return base_fare / self.num_riders

# Step 3: Context class that uses the strategy
class Ride:
    def __init__(self, rider_id: str, distance_km: float):
        self.rider_id = rider_id
        self.distance_km = distance_km
        self.base_rate = 10.0  # per km
        self._pricing_strategy: PricingStrategy = NormalPricing()
    
    def set_pricing_strategy(self, strategy: PricingStrategy):
        """Change pricing strategy at runtime"""
        self._pricing_strategy = strategy
    
    def get_fare(self) -> float:
        return self._pricing_strategy.calculate_fare(self.distance_km, self.base_rate)

# Step 4: Usage
if __name__ == "__main__":
    ride = Ride(rider_id="R123", distance_km=15)
    
    # Normal pricing
    print(f"Normal fare: ${ride.get_fare()}")  # $150
    
    # Surge hits!
    ride.set_pricing_strategy(SurgePricing(surge_multiplier=2.5))
    print(f"Surge fare: ${ride.get_fare()}")  # $375
    
    # User has coupon
    ride.set_pricing_strategy(DiscountPricing(discount_percent=30))
    print(f"Discounted fare: ${ride.get_fare()}")  # $105
    
    # Pool ride with 3 people
    ride.set_pricing_strategy(PoolPricing(num_riders=3))
    print(f"Pool fare per person: ${ride.get_fare()}")  # $50
```

### When to Use Strategy
- Multiple algorithms for the same task
- Need to switch algorithms at runtime
- Want to avoid large conditional statements
- Algorithm details should be hidden from client

### Interview Tip 💡
> "I'll use Strategy pattern here because we have multiple pricing algorithms that can change independently. This follows Open-Closed principle - we can add new pricing types without modifying existing code."

---

## 2. Factory Pattern

### The Problem
Uber has different vehicle types: UberX, UberXL, UberBlack, UberPool. Creating these vehicles involves complex logic.

```python
# ❌ BAD - Client needs to know all vehicle classes
if vehicle_type == "UberX":
    vehicle = UberX(driver, license)
elif vehicle_type == "UberXL":
    vehicle = UberXL(driver, license, extra_capacity)
elif vehicle_type == "UberBlack":
    vehicle = UberBlack(driver, license, luxury_features)
# Client is tightly coupled to all concrete classes
```

### The Solution: Factory Pattern

**Define an interface for creating objects, but let subclasses/factory decide which class to instantiate.**

```python
from abc import ABC, abstractmethod
from enum import Enum

# Step 1: Define Product Interface
class Vehicle(ABC):
    def __init__(self, driver_id: str, license_plate: str):
        self.driver_id = driver_id
        self.license_plate = license_plate
    
    @abstractmethod
    def get_capacity(self) -> int:
        pass
    
    @abstractmethod
    def get_base_rate(self) -> float:
        pass
    
    @abstractmethod
    def get_vehicle_type(self) -> str:
        pass

# Step 2: Concrete Products
class UberX(Vehicle):
    def get_capacity(self) -> int:
        return 4
    
    def get_base_rate(self) -> float:
        return 10.0
    
    def get_vehicle_type(self) -> str:
        return "UberX"

class UberXL(Vehicle):
    def get_capacity(self) -> int:
        return 6
    
    def get_base_rate(self) -> float:
        return 15.0
    
    def get_vehicle_type(self) -> str:
        return "UberXL"

class UberBlack(Vehicle):
    def get_capacity(self) -> int:
        return 4
    
    def get_base_rate(self) -> float:
        return 25.0
    
    def get_vehicle_type(self) -> str:
        return "UberBlack"

class UberPool(Vehicle):
    def get_capacity(self) -> int:
        return 4
    
    def get_base_rate(self) -> float:
        return 6.0
    
    def get_vehicle_type(self) -> str:
        return "UberPool"

# Step 3: Define Vehicle Type Enum
class VehicleType(Enum):
    UBER_X = "UberX"
    UBER_XL = "UberXL"
    UBER_BLACK = "UberBlack"
    UBER_POOL = "UberPool"

# Step 4: Factory
class VehicleFactory:
    """Factory to create vehicles - hides instantiation logic"""
    
    @staticmethod
    def create_vehicle(vehicle_type: VehicleType, driver_id: str, license_plate: str) -> Vehicle:
        vehicle_map = {
            VehicleType.UBER_X: UberX,
            VehicleType.UBER_XL: UberXL,
            VehicleType.UBER_BLACK: UberBlack,
            VehicleType.UBER_POOL: UberPool,
        }
        
        vehicle_class = vehicle_map.get(vehicle_type)
        if not vehicle_class:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
        
        return vehicle_class(driver_id, license_plate)

# Step 5: Usage
if __name__ == "__main__":
    # Client doesn't need to know concrete classes
    factory = VehicleFactory()
    
    uber_x = factory.create_vehicle(VehicleType.UBER_X, "D001", "ABC-123")
    uber_black = factory.create_vehicle(VehicleType.UBER_BLACK, "D002", "XYZ-789")
    
    print(f"{uber_x.get_vehicle_type()}: capacity={uber_x.get_capacity()}, rate=${uber_x.get_base_rate()}/km")
    print(f"{uber_black.get_vehicle_type()}: capacity={uber_black.get_capacity()}, rate=${uber_black.get_base_rate()}/km")
```

### Abstract Factory (Extension)

When you need to create families of related objects:

```python
from abc import ABC, abstractmethod

class VehicleFactory(ABC):
    @abstractmethod
    def create_economy_vehicle(self) -> Vehicle:
        pass
    
    @abstractmethod
    def create_premium_vehicle(self) -> Vehicle:
        pass

class USVehicleFactory(VehicleFactory):
    def create_economy_vehicle(self) -> Vehicle:
        return UberX("US-driver", "US-plate")
    
    def create_premium_vehicle(self) -> Vehicle:
        return UberBlack("US-driver", "US-plate")

class IndiaVehicleFactory(VehicleFactory):
    def create_economy_vehicle(self) -> Vehicle:
        return UberGo("IN-driver", "IN-plate")  # India-specific
    
    def create_premium_vehicle(self) -> Vehicle:
        return UberPremier("IN-driver", "IN-plate")  # India-specific
```

### When to Use Factory
- Object creation logic is complex
- Client shouldn't know about concrete classes
- Need to create families of related objects
- Want centralized control over object creation

### Interview Tip 💡
> "I'll use Factory pattern to encapsulate vehicle creation. This decouples the client from concrete classes and makes it easy to add new vehicle types without changing client code."

---

## 3. Singleton Pattern

### The Problem
Uber needs exactly ONE instance of:
- Configuration Manager
- Database Connection Pool
- Logger
- Cache Manager

Multiple instances would cause inconsistency or resource waste.

### The Solution: Singleton Pattern

**Ensure a class has only one instance and provide a global point of access to it.**

```python
import threading

# Method 1: Thread-Safe Singleton with Double-Checked Locking
class ConfigurationManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # Initialize configuration
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        # Simulate loading from file/env
        self._config = {
            "base_rate": 10.0,
            "surge_threshold": 0.8,
            "max_wait_time": 300,
            "db_host": "localhost",
            "db_port": 5432,
        }
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        self._config[key] = value

# Method 2: Singleton using Metaclass (Cleaner)
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.log_file = "uber_app.log"
    
    def log(self, level: str, message: str):
        print(f"[{level}] {message}")
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)

# Usage
if __name__ == "__main__":
    # Both variables point to the SAME instance
    config1 = ConfigurationManager()
    config2 = ConfigurationManager()
    
    print(f"Same instance? {config1 is config2}")  # True
    
    config1.set("base_rate", 15.0)
    print(f"Config2 sees change: {config2.get('base_rate')}")  # 15.0
    
    # Logger singleton
    logger1 = Logger()
    logger2 = Logger()
    print(f"Same logger? {logger1 is logger2}")  # True
    
    logger1.info("Ride requested by user U123")
```

### When to Use Singleton
- Exactly one instance needed (config, logging, caching)
- Global access point required
- Shared resource management

### When NOT to Use
- Testing becomes difficult (hard to mock)
- Can hide dependencies
- Can introduce global state issues

### Interview Tip 💡
> "I'll make ConfigurationManager a singleton since we need consistent configuration across the application. However, I'll inject it as a dependency for testability rather than accessing it globally."

---

## 4. Observer Pattern

### The Problem
When a ride status changes, multiple systems need to be notified:
- Rider app (show status update)
- Driver app (show navigation)
- Analytics service (track metrics)
- Billing service (prepare invoice on completion)
- Notification service (send push/SMS)

```python
# ❌ BAD - Ride class knows about all dependent systems
class Ride:
    def update_status(self, new_status):
        self.status = new_status
        # Tightly coupled to all observers
        self.rider_app.notify(self.status)
        self.driver_app.notify(self.status)
        self.analytics.track(self.status)
        self.billing.prepare(self.status)
        self.notification.send(self.status)
        # Adding new observer = modifying this class 😞
```

### The Solution: Observer Pattern

**Define a one-to-many dependency so that when one object changes state, all dependents are notified automatically.**

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from datetime import datetime

# Step 1: Define Event/State
class RideStatus(Enum):
    REQUESTED = "requested"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_ARRIVED = "driver_arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RideEvent:
    def __init__(self, ride_id: str, status: RideStatus, timestamp: datetime = None):
        self.ride_id = ride_id
        self.status = status
        self.timestamp = timestamp or datetime.now()

# Step 2: Observer Interface
class RideObserver(ABC):
    @abstractmethod
    def on_ride_update(self, event: RideEvent):
        pass

# Step 3: Concrete Observers
class RiderAppNotifier(RideObserver):
    def on_ride_update(self, event: RideEvent):
        messages = {
            RideStatus.DRIVER_ASSIGNED: "Driver is on the way!",
            RideStatus.DRIVER_ARRIVED: "Your driver has arrived!",
            RideStatus.IN_PROGRESS: "Enjoy your ride!",
            RideStatus.COMPLETED: "Thanks for riding with us!",
            RideStatus.CANCELLED: "Ride cancelled.",
        }
        if event.status in messages:
            print(f"[RiderApp] Push to rider: {messages[event.status]}")

class DriverAppNotifier(RideObserver):
    def on_ride_update(self, event: RideEvent):
        if event.status == RideStatus.REQUESTED:
            print(f"[DriverApp] New ride request! Ride ID: {event.ride_id}")
        elif event.status == RideStatus.COMPLETED:
            print(f"[DriverApp] Ride completed. Ready for next ride!")

class AnalyticsService(RideObserver):
    def on_ride_update(self, event: RideEvent):
        print(f"[Analytics] Tracking: ride={event.ride_id}, status={event.status.value}, time={event.timestamp}")

class BillingService(RideObserver):
    def on_ride_update(self, event: RideEvent):
        if event.status == RideStatus.COMPLETED:
            print(f"[Billing] Generating invoice for ride {event.ride_id}")
        elif event.status == RideStatus.CANCELLED:
            print(f"[Billing] Processing cancellation fee for ride {event.ride_id}")

class NotificationService(RideObserver):
    def on_ride_update(self, event: RideEvent):
        if event.status == RideStatus.COMPLETED:
            print(f"[SMS] Sending receipt SMS for ride {event.ride_id}")

# Step 4: Subject (Observable)
class Ride:
    def __init__(self, ride_id: str, rider_id: str):
        self.ride_id = ride_id
        self.rider_id = rider_id
        self.driver_id = None
        self._status = RideStatus.REQUESTED
        self._observers: List[RideObserver] = []
    
    def add_observer(self, observer: RideObserver):
        self._observers.append(observer)
    
    def remove_observer(self, observer: RideObserver):
        self._observers.remove(observer)
    
    def _notify_observers(self):
        event = RideEvent(self.ride_id, self._status)
        for observer in self._observers:
            observer.on_ride_update(event)
    
    @property
    def status(self) -> RideStatus:
        return self._status
    
    @status.setter
    def status(self, new_status: RideStatus):
        self._status = new_status
        self._notify_observers()  # Automatically notify all observers
    
    def assign_driver(self, driver_id: str):
        self.driver_id = driver_id
        self.status = RideStatus.DRIVER_ASSIGNED
    
    def start_ride(self):
        self.status = RideStatus.IN_PROGRESS
    
    def complete_ride(self):
        self.status = RideStatus.COMPLETED
    
    def cancel_ride(self):
        self.status = RideStatus.CANCELLED

# Step 5: Usage
if __name__ == "__main__":
    # Create ride
    ride = Ride(ride_id="R001", rider_id="U123")
    
    # Register observers
    ride.add_observer(RiderAppNotifier())
    ride.add_observer(DriverAppNotifier())
    ride.add_observer(AnalyticsService())
    ride.add_observer(BillingService())
    ride.add_observer(NotificationService())
    
    # Simulate ride lifecycle - observers are automatically notified
    print("=" * 50)
    print("RIDE LIFECYCLE")
    print("=" * 50)
    
    ride.assign_driver("D456")
    print()
    ride.status = RideStatus.DRIVER_ARRIVED
    print()
    ride.start_ride()
    print()
    ride.complete_ride()
```

### When to Use Observer
- One-to-many relationships
- State changes need to broadcast to multiple objects
- Loose coupling between subject and observers
- Event-driven systems

### Interview Tip 💡
> "Observer pattern is perfect here because ride status changes need to notify multiple independent services. The Ride class doesn't need to know about specific observers - we can add or remove them without changing the Ride class."

---

## 5. State Pattern

### The Problem
A ride has different states, and behavior changes based on state:
- **Requested:** Can cancel, cannot start
- **Driver Assigned:** Can cancel (with fee), cannot complete
- **In Progress:** Cannot cancel, can complete
- **Completed:** Cannot do anything

```python
# ❌ BAD - Complex if-else everywhere
class Ride:
    def cancel(self):
        if self.status == "requested":
            self.status = "cancelled"
        elif self.status == "driver_assigned":
            self.status = "cancelled"
            self.charge_cancellation_fee()
        elif self.status == "in_progress":
            raise Exception("Cannot cancel ongoing ride")
        elif self.status == "completed":
            raise Exception("Ride already completed")
        # This grows with every new state and action 😞
```

### The Solution: State Pattern

**Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.**

```python
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from __future__ import annotations

# Step 1: State Interface
class RideState(ABC):
    @abstractmethod
    def request_ride(self, ride: 'Ride'):
        pass
    
    @abstractmethod
    def assign_driver(self, ride: 'Ride', driver_id: str):
        pass
    
    @abstractmethod
    def start_ride(self, ride: 'Ride'):
        pass
    
    @abstractmethod
    def complete_ride(self, ride: 'Ride'):
        pass
    
    @abstractmethod
    def cancel_ride(self, ride: 'Ride'):
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        pass

# Step 2: Concrete States
class IdleState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Ride requested! Looking for drivers...")
        ride.set_state(RequestedState())
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print("Error: Cannot assign driver. Request a ride first.")
    
    def start_ride(self, ride: 'Ride'):
        print("Error: Cannot start. Request a ride first.")
    
    def complete_ride(self, ride: 'Ride'):
        print("Error: No ride to complete.")
    
    def cancel_ride(self, ride: 'Ride'):
        print("Error: No ride to cancel.")
    
    def get_state_name(self) -> str:
        return "IDLE"

class RequestedState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Error: Ride already requested.")
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print(f"Driver {driver_id} assigned!")
        ride.driver_id = driver_id
        ride.set_state(DriverAssignedState())
    
    def start_ride(self, ride: 'Ride'):
        print("Error: Wait for driver to be assigned.")
    
    def complete_ride(self, ride: 'Ride'):
        print("Error: Ride hasn't started yet.")
    
    def cancel_ride(self, ride: 'Ride'):
        print("Ride cancelled. No charges.")
        ride.set_state(CancelledState())
    
    def get_state_name(self) -> str:
        return "REQUESTED"

class DriverAssignedState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Error: Ride already in progress.")
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print("Error: Driver already assigned.")
    
    def start_ride(self, ride: 'Ride'):
        print("Ride started! Enjoy your trip.")
        ride.set_state(InProgressState())
    
    def complete_ride(self, ride: 'Ride'):
        print("Error: Ride hasn't started yet.")
    
    def cancel_ride(self, ride: 'Ride'):
        print("Ride cancelled. Cancellation fee of $5 charged.")
        ride.cancellation_fee = 5.0
        ride.set_state(CancelledState())
    
    def get_state_name(self) -> str:
        return "DRIVER_ASSIGNED"

class InProgressState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Error: Ride already in progress.")
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print("Error: Ride already in progress.")
    
    def start_ride(self, ride: 'Ride'):
        print("Error: Ride already in progress.")
    
    def complete_ride(self, ride: 'Ride'):
        print("Ride completed! Calculating fare...")
        ride.calculate_fare()
        ride.set_state(CompletedState())
    
    def cancel_ride(self, ride: 'Ride'):
        print("Error: Cannot cancel an ongoing ride. Please complete it first.")
    
    def get_state_name(self) -> str:
        return "IN_PROGRESS"

class CompletedState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Error: This ride is completed. Create a new ride.")
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print("Error: This ride is completed.")
    
    def start_ride(self, ride: 'Ride'):
        print("Error: This ride is completed.")
    
    def complete_ride(self, ride: 'Ride'):
        print("Error: Ride already completed.")
    
    def cancel_ride(self, ride: 'Ride'):
        print("Error: Cannot cancel a completed ride.")
    
    def get_state_name(self) -> str:
        return "COMPLETED"

class CancelledState(RideState):
    def request_ride(self, ride: 'Ride'):
        print("Error: This ride is cancelled. Create a new ride.")
    
    def assign_driver(self, ride: 'Ride', driver_id: str):
        print("Error: This ride is cancelled.")
    
    def start_ride(self, ride: 'Ride'):
        print("Error: This ride is cancelled.")
    
    def complete_ride(self, ride: 'Ride'):
        print("Error: This ride is cancelled.")
    
    def cancel_ride(self, ride: 'Ride'):
        print("Error: Ride already cancelled.")
    
    def get_state_name(self) -> str:
        return "CANCELLED"

# Step 3: Context
class Ride:
    def __init__(self, ride_id: str, rider_id: str):
        self.ride_id = ride_id
        self.rider_id = rider_id
        self.driver_id = None
        self.fare = 0.0
        self.cancellation_fee = 0.0
        self.distance_km = 0.0
        self._state: RideState = IdleState()
    
    def set_state(self, state: RideState):
        print(f"  [State Change: {self._state.get_state_name()} -> {state.get_state_name()}]")
        self._state = state
    
    def get_state(self) -> str:
        return self._state.get_state_name()
    
    # Delegate all actions to current state
    def request_ride(self):
        self._state.request_ride(self)
    
    def assign_driver(self, driver_id: str):
        self._state.assign_driver(self, driver_id)
    
    def start_ride(self):
        self._state.start_ride(self)
    
    def complete_ride(self):
        self._state.complete_ride(self)
    
    def cancel_ride(self):
        self._state.cancel_ride(self)
    
    def calculate_fare(self):
        self.distance_km = 10.0  # Simulated
        self.fare = self.distance_km * 12  # $12 per km
        print(f"  Fare: ${self.fare} for {self.distance_km} km")

# Step 4: Usage
if __name__ == "__main__":
    print("=" * 60)
    print("RIDE STATE MACHINE DEMO")
    print("=" * 60)
    
    ride = Ride("R001", "U123")
    print(f"\nCurrent State: {ride.get_state()}")
    
    # Happy path
    print("\n--- Happy Path ---")
    ride.request_ride()
    ride.assign_driver("D456")
    ride.start_ride()
    ride.complete_ride()
    
    # Try invalid operations
    print("\n--- Invalid Operations ---")
    ride.cancel_ride()  # Can't cancel completed ride
    ride.start_ride()   # Can't start completed ride
    
    # Cancellation path
    print("\n--- Cancellation Path ---")
    ride2 = Ride("R002", "U789")
    ride2.request_ride()
    ride2.assign_driver("D111")
    ride2.cancel_ride()  # Cancelled with fee
    print(f"Cancellation fee: ${ride2.cancellation_fee}")
```

### When to Use State
- Object behavior depends on its state
- Large conditional statements based on state
- State transitions are explicit and well-defined
- Finite State Machine scenarios

### Interview Tip 💡
> "State pattern eliminates complex conditionals by encapsulating state-specific behavior in separate classes. Each state knows what actions are valid and handles transitions. This makes the code much more maintainable."

---

## 6. Decorator Pattern

### The Problem
Rides can have optional features:
- Basic ride
- With WiFi
- With child seat
- With premium audio
- With wheelchair accessibility

```python
# ❌ BAD - Class explosion
class BasicRide: pass
class RideWithWifi: pass
class RideWithChildSeat: pass
class RideWithWifiAndChildSeat: pass
class RideWithWifiAndChildSeatAndPremiumAudio: pass
# Combinations grow exponentially! 😞
```

### The Solution: Decorator Pattern

**Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing.**

```python
from abc import ABC, abstractmethod

# Step 1: Component Interface
class RideService(ABC):
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_cost(self) -> float:
        pass

# Step 2: Concrete Component
class BasicRide(RideService):
    def __init__(self, distance_km: float):
        self.distance_km = distance_km
        self.base_rate = 10.0
    
    def get_description(self) -> str:
        return f"Basic Ride ({self.distance_km} km)"
    
    def get_cost(self) -> float:
        return self.distance_km * self.base_rate

# Step 3: Decorator Base Class
class RideDecorator(RideService, ABC):
    def __init__(self, ride: RideService):
        self._ride = ride
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_cost(self) -> float:
        pass

# Step 4: Concrete Decorators
class WifiDecorator(RideDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + WiFi"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 5.0  # $5 for WiFi

class ChildSeatDecorator(RideDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Child Seat"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 10.0  # $10 for child seat

class PremiumAudioDecorator(RideDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Premium Audio"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 3.0  # $3 for premium audio

class WheelchairAccessDecorator(RideDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Wheelchair Access"
    
    def get_cost(self) -> float:
        return self._ride.get_cost()  # No extra charge for accessibility

class PetFriendlyDecorator(RideDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Pet Friendly"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 8.0  # $8 for pet friendly

# Step 5: Usage
if __name__ == "__main__":
    # Basic ride
    ride = BasicRide(distance_km=15)
    print(f"{ride.get_description()}: ${ride.get_cost()}")
    
    # Add WiFi
    ride_with_wifi = WifiDecorator(ride)
    print(f"{ride_with_wifi.get_description()}: ${ride_with_wifi.get_cost()}")
    
    # Add child seat on top
    ride_with_wifi_and_child = ChildSeatDecorator(ride_with_wifi)
    print(f"{ride_with_wifi_and_child.get_description()}: ${ride_with_wifi_and_child.get_cost()}")
    
    # Full featured ride
    full_ride = PremiumAudioDecorator(
        PetFriendlyDecorator(
            WifiDecorator(
                BasicRide(distance_km=20)
            )
        )
    )
    print(f"{full_ride.get_description()}: ${full_ride.get_cost()}")
```

### When to Use Decorator
- Add responsibilities dynamically
- Avoid class explosion from feature combinations
- Features can be combined in any order
- Single Responsibility - each decorator handles one feature

### Interview Tip 💡
> "Decorator pattern lets us add features like WiFi or child seats dynamically without subclassing. Each decorator wraps the base ride and adds its cost/description. We can stack decorators in any combination."

---

## 7. Builder Pattern

### The Problem
Creating a complex Ride object with many optional parameters:

```python
# ❌ BAD - Constructor with too many parameters
ride = Ride(
    rider_id="U123",
    pickup="123 Main St",
    dropoff="456 Oak Ave",
    vehicle_type="UberX",
    scheduled_time=None,
    promo_code="SAVE20",
    payment_method="card",
    notes="Ring doorbell",
    accessibility_needs=True,
    child_seats=2,
    # ... many more
)
```

### The Solution: Builder Pattern

**Separate the construction of a complex object from its representation.**

```python
from datetime import datetime
from typing import Optional
from enum import Enum

class VehicleType(Enum):
    UBER_X = "UberX"
    UBER_XL = "UberXL"
    UBER_BLACK = "UberBlack"
    UBER_POOL = "UberPool"

class PaymentMethod(Enum):
    CARD = "card"
    CASH = "cash"
    WALLET = "wallet"

# Step 1: Product
class RideRequest:
    def __init__(self):
        # Required
        self.rider_id: str = None
        self.pickup_location: str = None
        self.dropoff_location: str = None
        
        # Optional
        self.vehicle_type: VehicleType = VehicleType.UBER_X
        self.scheduled_time: Optional[datetime] = None
        self.promo_code: Optional[str] = None
        self.payment_method: PaymentMethod = PaymentMethod.CARD
        self.notes: Optional[str] = None
        self.wheelchair_accessible: bool = False
        self.child_seats: int = 0
        self.pet_friendly: bool = False
        self.quiet_ride: bool = False
        self.preferred_temperature: Optional[int] = None
    
    def __str__(self):
        return f"""
RideRequest:
  Rider: {self.rider_id}
  From: {self.pickup_location}
  To: {self.dropoff_location}
  Vehicle: {self.vehicle_type.value}
  Scheduled: {self.scheduled_time or 'Now'}
  Payment: {self.payment_method.value}
  Promo: {self.promo_code or 'None'}
  Wheelchair: {self.wheelchair_accessible}
  Child Seats: {self.child_seats}
  Pet Friendly: {self.pet_friendly}
  Quiet Ride: {self.quiet_ride}
  Notes: {self.notes or 'None'}
"""

# Step 2: Builder
class RideRequestBuilder:
    def __init__(self):
        self._request = RideRequest()
    
    # Required fields
    def set_rider(self, rider_id: str) -> 'RideRequestBuilder':
        self._request.rider_id = rider_id
        return self
    
    def set_pickup(self, location: str) -> 'RideRequestBuilder':
        self._request.pickup_location = location
        return self
    
    def set_dropoff(self, location: str) -> 'RideRequestBuilder':
        self._request.dropoff_location = location
        return self
    
    # Optional fields
    def set_vehicle_type(self, vehicle_type: VehicleType) -> 'RideRequestBuilder':
        self._request.vehicle_type = vehicle_type
        return self
    
    def schedule_for(self, time: datetime) -> 'RideRequestBuilder':
        self._request.scheduled_time = time
        return self
    
    def apply_promo(self, code: str) -> 'RideRequestBuilder':
        self._request.promo_code = code
        return self
    
    def set_payment(self, method: PaymentMethod) -> 'RideRequestBuilder':
        self._request.payment_method = method
        return self
    
    def add_notes(self, notes: str) -> 'RideRequestBuilder':
        self._request.notes = notes
        return self
    
    def require_wheelchair_access(self) -> 'RideRequestBuilder':
        self._request.wheelchair_accessible = True
        return self
    
    def add_child_seats(self, count: int) -> 'RideRequestBuilder':
        self._request.child_seats = count
        return self
    
    def pet_friendly(self) -> 'RideRequestBuilder':
        self._request.pet_friendly = True
        return self
    
    def quiet_ride(self) -> 'RideRequestBuilder':
        self._request.quiet_ride = True
        return self
    
    def set_temperature(self, temp: int) -> 'RideRequestBuilder':
        self._request.preferred_temperature = temp
        return self
    
    def build(self) -> RideRequest:
        # Validate required fields
        if not self._request.rider_id:
            raise ValueError("Rider ID is required")
        if not self._request.pickup_location:
            raise ValueError("Pickup location is required")
        if not self._request.dropoff_location:
            raise ValueError("Dropoff location is required")
        
        return self._request

# Step 3: Director (optional - for common configurations)
class RideRequestDirector:
    def __init__(self, builder: RideRequestBuilder):
        self._builder = builder
    
    def build_family_ride(self, rider_id: str, pickup: str, dropoff: str, child_count: int) -> RideRequest:
        return (self._builder
            .set_rider(rider_id)
            .set_pickup(pickup)
            .set_dropoff(dropoff)
            .set_vehicle_type(VehicleType.UBER_XL)
            .add_child_seats(child_count)
            .build())
    
    def build_business_ride(self, rider_id: str, pickup: str, dropoff: str) -> RideRequest:
        return (self._builder
            .set_rider(rider_id)
            .set_pickup(pickup)
            .set_dropoff(dropoff)
            .set_vehicle_type(VehicleType.UBER_BLACK)
            .quiet_ride()
            .set_temperature(72)
            .build())

# Step 4: Usage
if __name__ == "__main__":
    # Fluent builder usage
    ride_request = (RideRequestBuilder()
        .set_rider("U123")
        .set_pickup("123 Main St, San Francisco")
        .set_dropoff("456 Market St, San Francisco")
        .set_vehicle_type(VehicleType.UBER_XL)
        .add_child_seats(2)
        .pet_friendly()
        .apply_promo("FAMILY20")
        .add_notes("Please call when arriving")
        .build())
    
    print(ride_request)
    
    # Using director for common configurations
    builder = RideRequestBuilder()
    director = RideRequestDirector(builder)
    
    family_ride = director.build_family_ride(
        "U456", 
        "Airport", 
        "Hotel Downtown", 
        child_count=2
    )
    print(family_ride)
```

### When to Use Builder
- Object has many optional parameters
- Object construction has multiple steps
- Need immutable objects with many fields
- Want fluent interface for construction

### Interview Tip 💡
> "Builder pattern gives us a fluent API to construct complex objects step by step. Required fields are validated in build(), and optional features can be added in any order."

---

## 8. Command Pattern

### The Problem
Actions in the Uber app need to:
- Be executed
- Be undone (cancel ride, refund)
- Be queued (schedule rides)
- Be logged (audit trail)

### The Solution: Command Pattern

**Encapsulate a request as an object, allowing you to parameterize clients with queues, requests, and operations.**

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from collections import deque

# Step 1: Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass

# Step 2: Receiver (the actual business logic)
class RideService:
    def __init__(self):
        self.rides = {}
    
    def create_ride(self, ride_id: str, rider_id: str, pickup: str, dropoff: str) -> bool:
        if ride_id in self.rides:
            return False
        self.rides[ride_id] = {
            "rider_id": rider_id,
            "pickup": pickup,
            "dropoff": dropoff,
            "status": "created"
        }
        print(f"  [RideService] Created ride {ride_id}")
        return True
    
    def cancel_ride(self, ride_id: str) -> bool:
        if ride_id not in self.rides:
            return False
        self.rides[ride_id]["status"] = "cancelled"
        print(f"  [RideService] Cancelled ride {ride_id}")
        return True
    
    def restore_ride(self, ride_id: str) -> bool:
        if ride_id not in self.rides:
            return False
        self.rides[ride_id]["status"] = "created"
        print(f"  [RideService] Restored ride {ride_id}")
        return True

class PaymentService:
    def __init__(self):
        self.transactions = {}
    
    def charge(self, user_id: str, amount: float, transaction_id: str) -> bool:
        self.transactions[transaction_id] = {
            "user_id": user_id,
            "amount": amount,
            "status": "charged"
        }
        print(f"  [PaymentService] Charged ${amount} to user {user_id}")
        return True
    
    def refund(self, transaction_id: str) -> bool:
        if transaction_id not in self.transactions:
            return False
        txn = self.transactions[transaction_id]
        txn["status"] = "refunded"
        print(f"  [PaymentService] Refunded ${txn['amount']} to user {txn['user_id']}")
        return True

# Step 3: Concrete Commands
class CreateRideCommand(Command):
    def __init__(self, ride_service: RideService, ride_id: str, rider_id: str, pickup: str, dropoff: str):
        self.ride_service = ride_service
        self.ride_id = ride_id
        self.rider_id = rider_id
        self.pickup = pickup
        self.dropoff = dropoff
        self.executed = False
    
    def execute(self) -> bool:
        self.executed = self.ride_service.create_ride(
            self.ride_id, self.rider_id, self.pickup, self.dropoff
        )
        return self.executed
    
    def undo(self) -> bool:
        if not self.executed:
            return False
        return self.ride_service.cancel_ride(self.ride_id)
    
    def get_description(self) -> str:
        return f"CreateRide({self.ride_id})"

class CancelRideCommand(Command):
    def __init__(self, ride_service: RideService, ride_id: str):
        self.ride_service = ride_service
        self.ride_id = ride_id
        self.executed = False
    
    def execute(self) -> bool:
        self.executed = self.ride_service.cancel_ride(self.ride_id)
        return self.executed
    
    def undo(self) -> bool:
        if not self.executed:
            return False
        return self.ride_service.restore_ride(self.ride_id)
    
    def get_description(self) -> str:
        return f"CancelRide({self.ride_id})"

class ChargeUserCommand(Command):
    def __init__(self, payment_service: PaymentService, user_id: str, amount: float, transaction_id: str):
        self.payment_service = payment_service
        self.user_id = user_id
        self.amount = amount
        self.transaction_id = transaction_id
        self.executed = False
    
    def execute(self) -> bool:
        self.executed = self.payment_service.charge(
            self.user_id, self.amount, self.transaction_id
        )
        return self.executed
    
    def undo(self) -> bool:
        if not self.executed:
            return False
        return self.payment_service.refund(self.transaction_id)
    
    def get_description(self) -> str:
        return f"ChargeUser({self.user_id}, ${self.amount})"

# Step 4: Invoker (Command Manager)
class CommandManager:
    def __init__(self):
        self.history: List[Command] = []
        self.command_queue: deque = deque()
    
    def execute(self, command: Command) -> bool:
        result = command.execute()
        if result:
            self.history.append(command)
            print(f"  [CommandManager] Executed: {command.get_description()}")
        return result
    
    def undo_last(self) -> bool:
        if not self.history:
            print("  [CommandManager] Nothing to undo")
            return False
        command = self.history.pop()
        result = command.undo()
        print(f"  [CommandManager] Undone: {command.get_description()}")
        return result
    
    def queue_command(self, command: Command):
        self.command_queue.append(command)
        print(f"  [CommandManager] Queued: {command.get_description()}")
    
    def process_queue(self):
        print(f"  [CommandManager] Processing {len(self.command_queue)} queued commands")
        while self.command_queue:
            command = self.command_queue.popleft()
            self.execute(command)
    
    def get_history(self) -> List[str]:
        return [cmd.get_description() for cmd in self.history]

# Step 5: Usage
if __name__ == "__main__":
    # Services
    ride_service = RideService()
    payment_service = PaymentService()
    command_manager = CommandManager()
    
    print("=" * 50)
    print("EXECUTING COMMANDS")
    print("=" * 50)
    
    # Execute commands
    create_cmd = CreateRideCommand(ride_service, "R001", "U123", "Airport", "Downtown")
    command_manager.execute(create_cmd)
    
    charge_cmd = ChargeUserCommand(payment_service, "U123", 45.00, "TXN001")
    command_manager.execute(charge_cmd)
    
    print("\n" + "=" * 50)
    print("UNDO OPERATIONS")
    print("=" * 50)
    
    # Undo last command (refund)
    command_manager.undo_last()
    
    print("\n" + "=" * 50)
    print("COMMAND HISTORY")
    print("=" * 50)
    print(command_manager.get_history())
    
    print("\n" + "=" * 50)
    print("QUEUED COMMANDS (Scheduled Rides)")
    print("=" * 50)
    
    # Queue commands for later
    command_manager.queue_command(
        CreateRideCommand(ride_service, "R002", "U456", "Home", "Office")
    )
    command_manager.queue_command(
        ChargeUserCommand(payment_service, "U456", 30.00, "TXN002")
    )
    
    # Process queue
    command_manager.process_queue()
```

### When to Use Command
- Need undo/redo functionality
- Queue or schedule operations
- Support transactions
- Need audit logs of all operations
- Decouple invoker from receiver

### Interview Tip 💡
> "Command pattern encapsulates actions as objects. This enables undo/redo, command queuing for scheduled rides, and transaction logging. Each command knows how to execute and reverse itself."

---

## 9. Template Method Pattern

### The Problem
Different ride types (UberX, UberPool, UberBlack) follow the same booking flow but with variations:
1. Validate request
2. Find drivers (different logic per type)
3. Calculate fare (different formula)
4. Create booking

### The Solution: Template Method Pattern

**Define the skeleton of an algorithm in a method, deferring some steps to subclasses.**

```python
from abc import ABC, abstractmethod

# Step 1: Abstract Class with Template Method
class RideBookingTemplate(ABC):
    """Template for booking a ride - defines the algorithm skeleton"""
    
    def book_ride(self, rider_id: str, pickup: str, dropoff: str) -> dict:
        """
        Template method - defines the booking algorithm.
        Subclasses cannot override this method.
        """
        print(f"\n{'='*50}")
        print(f"Booking {self.get_ride_type()} ride")
        print(f"{'='*50}")
        
        # Step 1: Validate (common)
        if not self._validate_request(rider_id, pickup, dropoff):
            return {"status": "failed", "reason": "validation_failed"}
        
        # Step 2: Find drivers (varies by ride type)
        driver = self._find_driver(pickup)
        if not driver:
            return {"status": "failed", "reason": "no_driver_found"}
        
        # Step 3: Calculate fare (varies by ride type)
        fare = self._calculate_fare(pickup, dropoff)
        
        # Step 4: Apply promotions (hook - optional override)
        fare = self._apply_promotions(fare, rider_id)
        
        # Step 5: Create booking (common)
        booking = self._create_booking(rider_id, driver, pickup, dropoff, fare)
        
        # Step 6: Send notifications (common)
        self._send_notifications(booking)
        
        return booking
    
    # Common methods (not meant to be overridden)
    def _validate_request(self, rider_id: str, pickup: str, dropoff: str) -> bool:
        print(f"  Validating request for rider {rider_id}")
        if not rider_id or not pickup or not dropoff:
            return False
        print("  ✓ Request valid")
        return True
    
    def _create_booking(self, rider_id: str, driver: dict, pickup: str, dropoff: str, fare: float) -> dict:
        booking = {
            "status": "confirmed",
            "rider_id": rider_id,
            "driver": driver,
            "pickup": pickup,
            "dropoff": dropoff,
            "fare": fare,
            "ride_type": self.get_ride_type()
        }
        print(f"  ✓ Booking created: ${fare:.2f}")
        return booking
    
    def _send_notifications(self, booking: dict):
        print(f"  ✓ Notification sent to rider and driver")
    
    # Abstract methods (MUST be overridden)
    @abstractmethod
    def get_ride_type(self) -> str:
        pass
    
    @abstractmethod
    def _find_driver(self, pickup: str) -> dict:
        pass
    
    @abstractmethod
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        pass
    
    # Hook method (CAN be overridden, has default implementation)
    def _apply_promotions(self, fare: float, rider_id: str) -> float:
        """Hook - subclasses can override to apply promotions"""
        return fare  # Default: no promotions

# Step 2: Concrete Implementations
class UberXBooking(RideBookingTemplate):
    def get_ride_type(self) -> str:
        return "UberX"
    
    def _find_driver(self, pickup: str) -> dict:
        print(f"  Finding nearest UberX driver...")
        # Logic: Find any available driver within 5km
        driver = {"id": "D001", "name": "John", "rating": 4.8, "distance_km": 2.5}
        print(f"  ✓ Found driver: {driver['name']} ({driver['distance_km']}km away)")
        return driver
    
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        print(f"  Calculating UberX fare...")
        base_fare = 5.0
        distance = 10.0  # Simulated
        rate_per_km = 2.0
        fare = base_fare + (distance * rate_per_km)
        return fare

class UberPoolBooking(RideBookingTemplate):
    def get_ride_type(self) -> str:
        return "UberPool"
    
    def _find_driver(self, pickup: str) -> dict:
        print(f"  Finding UberPool driver with matching route...")
        # Logic: Find driver already going in similar direction
        driver = {"id": "D002", "name": "Sarah", "rating": 4.9, "current_riders": 1}
        print(f"  ✓ Found driver: {driver['name']} (currently has {driver['current_riders']} rider)")
        return driver
    
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        print(f"  Calculating shared Pool fare...")
        base_fare = 3.0
        distance = 10.0  # Simulated
        rate_per_km = 1.2  # Cheaper due to sharing
        fare = base_fare + (distance * rate_per_km)
        return fare
    
    def _apply_promotions(self, fare: float, rider_id: str) -> float:
        # Pool has automatic 10% off for new riders
        discount = fare * 0.10
        print(f"  Applied Pool promotion: -${discount:.2f}")
        return fare - discount

class UberBlackBooking(RideBookingTemplate):
    def get_ride_type(self) -> str:
        return "UberBlack"
    
    def _find_driver(self, pickup: str) -> dict:
        print(f"  Finding premium UberBlack driver...")
        # Logic: Find highly rated driver with luxury vehicle
        driver = {"id": "D003", "name": "Michael", "rating": 4.95, "vehicle": "Mercedes S-Class"}
        print(f"  ✓ Found driver: {driver['name']} ({driver['vehicle']})")
        return driver
    
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        print(f"  Calculating premium Black fare...")
        base_fare = 15.0
        distance = 10.0  # Simulated
        rate_per_km = 4.0  # Premium rate
        fare = base_fare + (distance * rate_per_km)
        return fare

# Step 3: Usage
if __name__ == "__main__":
    rider_id = "U123"
    pickup = "123 Main St"
    dropoff = "456 Oak Ave"
    
    # Book different ride types - same flow, different implementations
    uber_x = UberXBooking()
    booking1 = uber_x.book_ride(rider_id, pickup, dropoff)
    
    uber_pool = UberPoolBooking()
    booking2 = uber_pool.book_ride(rider_id, pickup, dropoff)
    
    uber_black = UberBlackBooking()
    booking3 = uber_black.book_ride(rider_id, pickup, dropoff)
    
    print("\n" + "="*50)
    print("FARE COMPARISON")
    print("="*50)
    print(f"UberX:     ${booking1['fare']:.2f}")
    print(f"UberPool:  ${booking2['fare']:.2f}")
    print(f"UberBlack: ${booking3['fare']:.2f}")
```

### When to Use Template Method
- Multiple classes follow similar algorithm structure
- Common steps should be reused, specific steps customized
- Control the order of operations
- Want to enforce an algorithm skeleton

### Interview Tip 💡
> "Template Method defines the booking algorithm skeleton in the base class, while letting subclasses override specific steps like driver matching and fare calculation. Hook methods allow optional customization."

---

## 10. Chain of Responsibility Pattern

### The Problem
A ride request goes through multiple checks:
1. User verification
2. Payment validation
3. Fraud detection
4. Location validation
5. Surge pricing check

Each handler should process and pass to the next, or reject.

### The Solution: Chain of Responsibility

**Pass a request along a chain of handlers. Each handler decides to process or pass along.**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum

# Step 1: Request object
@dataclass
class RideRequest:
    rider_id: str
    pickup: str
    dropoff: str
    payment_method: str
    estimated_fare: float
    
    # Will be set by handlers
    is_verified: bool = False
    payment_valid: bool = False
    fraud_score: float = 0.0
    surge_multiplier: float = 1.0
    final_fare: float = 0.0
    rejection_reason: Optional[str] = None

class RequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Step 2: Handler Interface
class RequestHandler(ABC):
    def __init__(self):
        self._next_handler: Optional['RequestHandler'] = None
    
    def set_next(self, handler: 'RequestHandler') -> 'RequestHandler':
        self._next_handler = handler
        return handler
    
    def handle(self, request: RideRequest) -> RequestStatus:
        """Process the request and pass to next handler if approved"""
        status = self._process(request)
        
        if status == RequestStatus.REJECTED:
            return status
        
        if self._next_handler:
            return self._next_handler.handle(request)
        
        return RequestStatus.APPROVED
    
    @abstractmethod
    def _process(self, request: RideRequest) -> RequestStatus:
        pass
    
    @abstractmethod
    def get_handler_name(self) -> str:
        pass

# Step 3: Concrete Handlers
class UserVerificationHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.verified_users = {"U001", "U002", "U003", "U123"}  # Simulated DB
    
    def get_handler_name(self) -> str:
        return "UserVerification"
    
    def _process(self, request: RideRequest) -> RequestStatus:
        print(f"  [{self.get_handler_name()}] Checking user {request.rider_id}...")
        
        if request.rider_id in self.verified_users:
            request.is_verified = True
            print(f"    ✓ User verified")
            return RequestStatus.PENDING
        else:
            request.rejection_reason = "User not verified"
            print(f"    ✗ User not verified")
            return RequestStatus.REJECTED

class PaymentValidationHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.valid_payments = {"card_123", "wallet_456", "card"}  # Simulated
    
    def get_handler_name(self) -> str:
        return "PaymentValidation"
    
    def _process(self, request: RideRequest) -> RequestStatus:
        print(f"  [{self.get_handler_name()}] Validating payment method...")
        
        if request.payment_method in self.valid_payments:
            request.payment_valid = True
            print(f"    ✓ Payment method valid")
            return RequestStatus.PENDING
        else:
            request.rejection_reason = "Invalid payment method"
            print(f"    ✗ Payment method invalid")
            return RequestStatus.REJECTED

class FraudDetectionHandler(RequestHandler):
    def __init__(self, threshold: float = 0.7):
        super().__init__()
        self.threshold = threshold
    
    def get_handler_name(self) -> str:
        return "FraudDetection"
    
    def _process(self, request: RideRequest) -> RequestStatus:
        print(f"  [{self.get_handler_name()}] Running fraud detection...")
        
        # Simulated fraud scoring
        import random
        request.fraud_score = random.uniform(0, 0.5)  # Most users are legit
        
        if request.fraud_score < self.threshold:
            print(f"    ✓ Fraud score: {request.fraud_score:.2f} (below {self.threshold})")
            return RequestStatus.PENDING
        else:
            request.rejection_reason = f"High fraud score: {request.fraud_score:.2f}"
            print(f"    ✗ High fraud score: {request.fraud_score:.2f}")
            return RequestStatus.REJECTED

class LocationValidationHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.service_areas = ["San Francisco", "New York", "Los Angeles", "Main St", "Oak Ave"]
    
    def get_handler_name(self) -> str:
        return "LocationValidation"
    
    def _process(self, request: RideRequest) -> RequestStatus:
        print(f"  [{self.get_handler_name()}] Validating locations...")
        
        pickup_valid = any(area in request.pickup for area in self.service_areas)
        dropoff_valid = any(area in request.dropoff for area in self.service_areas)
        
        if pickup_valid and dropoff_valid:
            print(f"    ✓ Locations valid")
            return RequestStatus.PENDING
        else:
            request.rejection_reason = "Location outside service area"
            print(f"    ✗ Location outside service area")
            return RequestStatus.REJECTED

class SurgePricingHandler(RequestHandler):
    def __init__(self):
        super().__init__()
        self.demand_multipliers = {
            "San Francisco": 1.5,
            "Main St": 1.2,
            "default": 1.0
        }
    
    def get_handler_name(self) -> str:
        return "SurgePricing"
    
    def _process(self, request: RideRequest) -> RequestStatus:
        print(f"  [{self.get_handler_name()}] Calculating surge pricing...")
        
        for location, multiplier in self.demand_multipliers.items():
            if location in request.pickup:
                request.surge_multiplier = multiplier
                break
        else:
            request.surge_multiplier = self.demand_multipliers["default"]
        
        request.final_fare = request.estimated_fare * request.surge_multiplier
        print(f"    ✓ Surge: {request.surge_multiplier}x, Final fare: ${request.final_fare:.2f}")
        return RequestStatus.PENDING

# Step 4: Build and use the chain
class RideRequestProcessor:
    def __init__(self):
        # Build the chain
        self.chain = UserVerificationHandler()
        
        (self.chain
            .set_next(PaymentValidationHandler())
            .set_next(FraudDetectionHandler())
            .set_next(LocationValidationHandler())
            .set_next(SurgePricingHandler()))
    
    def process(self, request: RideRequest) -> RequestStatus:
        print(f"\n{'='*50}")
        print(f"Processing ride request for {request.rider_id}")
        print(f"{'='*50}")
        
        status = self.chain.handle(request)
        
        print(f"\n{'='*50}")
        if status == RequestStatus.APPROVED:
            print(f"✓ APPROVED - Final fare: ${request.final_fare:.2f}")
        else:
            print(f"✗ REJECTED - Reason: {request.rejection_reason}")
        print(f"{'='*50}")
        
        return status

# Step 5: Usage
if __name__ == "__main__":
    processor = RideRequestProcessor()
    
    # Valid request
    request1 = RideRequest(
        rider_id="U123",
        pickup="123 Main St, San Francisco",
        dropoff="456 Oak Ave",
        payment_method="card",
        estimated_fare=25.0
    )
    processor.process(request1)
    
    # Invalid user
    request2 = RideRequest(
        rider_id="U999",  # Not in verified users
        pickup="123 Main St",
        dropoff="456 Oak Ave",
        payment_method="card",
        estimated_fare=25.0
    )
    processor.process(request2)
    
    # Invalid payment
    request3 = RideRequest(
        rider_id="U123",
        pickup="123 Main St",
        dropoff="456 Oak Ave",
        payment_method="expired_card",  # Invalid
        estimated_fare=25.0
    )
    processor.process(request3)
```

### When to Use Chain of Responsibility
- Multiple handlers can process a request
- Handler order matters
- Want to decouple sender from receivers
- Request may be handled by different handlers at runtime

### Interview Tip 💡
> "Chain of Responsibility lets us build a processing pipeline where each handler focuses on one concern - verification, payment, fraud, etc. We can easily add, remove, or reorder handlers without changing the client code."

---

## Quick Reference Card

| Pattern | Use When | Key Benefit |
|---------|----------|-------------|
| **Strategy** | Multiple interchangeable algorithms | Runtime algorithm switching |
| **Factory** | Complex object creation | Decouples client from concrete classes |
| **Singleton** | Exactly one instance needed | Global access point |
| **Observer** | One-to-many notifications | Loose coupling |
| **State** | Behavior changes with state | Eliminates conditionals |
| **Decorator** | Add features dynamically | Avoids class explosion |
| **Builder** | Complex object with many params | Fluent construction |
| **Command** | Undo/redo, queuing operations | Encapsulates requests |
| **Template Method** | Same algorithm, varying steps | Code reuse with customization |
| **Chain of Responsibility** | Multiple handlers for request | Decoupled processing pipeline |

---

## Practice Exercises

1. **Implement a Notification System** using Strategy (email, SMS, push) and Observer
2. **Build a Payment Gateway** using Factory and Chain of Responsibility
3. **Create an Order Management System** using State and Command patterns
4. **Design a Coffee Shop** using Decorator and Builder patterns
5. **Implement a File Processing Pipeline** using Template Method and Chain of Responsibility

---

## Interview Success Checklist

- [ ] Can implement all 10 patterns from memory
- [ ] Know when to use each pattern (and when NOT to)
- [ ] Can combine patterns (Strategy + Factory, Observer + State, etc.)
- [ ] Understand trade-offs (e.g., Singleton testing issues)
- [ ] Can explain SOLID principles with pattern examples
- [ ] Practice speaking while coding - explain your design decisions

Good luck with your Uber interview! 🚀

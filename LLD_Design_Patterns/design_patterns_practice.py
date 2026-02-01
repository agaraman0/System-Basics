"""
Design Patterns Practice File - Uber LLD Interview Prep
========================================================
Run this file to see all patterns in action.
Modify and experiment with the code to learn!

Usage:
    python design_patterns_practice.py

Or run individual sections by uncommenting them at the bottom.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass
import threading


# =============================================================================
# 1. STRATEGY PATTERN - Dynamic Pricing
# =============================================================================

class PricingStrategy(ABC):
    """Strategy interface for different pricing algorithms"""
    
    @abstractmethod
    def calculate(self, distance_km: float, duration_min: float, base_rate: float) -> float:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


class NormalPricing(PricingStrategy):
    def calculate(self, distance_km: float, duration_min: float, base_rate: float) -> float:
        return (distance_km * base_rate) + (duration_min * 0.5)
    
    def get_name(self) -> str:
        return "Normal"


class SurgePricing(PricingStrategy):
    def __init__(self, multiplier: float = 2.0):
        self.multiplier = multiplier
    
    def calculate(self, distance_km: float, duration_min: float, base_rate: float) -> float:
        normal_fare = (distance_km * base_rate) + (duration_min * 0.5)
        return normal_fare * self.multiplier
    
    def get_name(self) -> str:
        return f"Surge ({self.multiplier}x)"


class PoolPricing(PricingStrategy):
    def __init__(self, riders: int = 2):
        self.riders = max(1, riders)
    
    def calculate(self, distance_km: float, duration_min: float, base_rate: float) -> float:
        normal_fare = (distance_km * base_rate) + (duration_min * 0.5)
        return normal_fare / self.riders
    
    def get_name(self) -> str:
        return f"Pool (÷{self.riders})"


class FareCalculator:
    """Context class that uses pricing strategy"""
    
    def __init__(self, strategy: PricingStrategy = None):
        self._strategy = strategy or NormalPricing()
        self.base_rate = 10.0
    
    def set_strategy(self, strategy: PricingStrategy):
        self._strategy = strategy
    
    def calculate_fare(self, distance_km: float, duration_min: float) -> float:
        fare = self._strategy.calculate(distance_km, duration_min, self.base_rate)
        print(f"  [{self._strategy.get_name()}] Distance: {distance_km}km, Duration: {duration_min}min -> ${fare:.2f}")
        return fare


def demo_strategy_pattern():
    """Demonstrate Strategy Pattern"""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - Dynamic Pricing Demo")
    print("="*60)
    
    calculator = FareCalculator()
    distance, duration = 10, 15
    
    # Normal pricing
    calculator.calculate_fare(distance, duration)
    
    # Surge pricing
    calculator.set_strategy(SurgePricing(2.5))
    calculator.calculate_fare(distance, duration)
    
    # Pool pricing
    calculator.set_strategy(PoolPricing(3))
    calculator.calculate_fare(distance, duration)


# =============================================================================
# 2. FACTORY PATTERN - Vehicle Creation
# =============================================================================

class VehicleType(Enum):
    UBER_X = "UberX"
    UBER_XL = "UberXL"
    UBER_BLACK = "UberBlack"


class Vehicle(ABC):
    def __init__(self, vehicle_id: str, driver_name: str):
        self.vehicle_id = vehicle_id
        self.driver_name = driver_name
    
    @abstractmethod
    def get_capacity(self) -> int:
        pass
    
    @abstractmethod
    def get_rate_per_km(self) -> float:
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        pass
    
    def __str__(self):
        return f"{self.get_type()} (ID: {self.vehicle_id}, Driver: {self.driver_name}, Capacity: {self.get_capacity()}, Rate: ${self.get_rate_per_km()}/km)"


class UberX(Vehicle):
    def get_capacity(self) -> int:
        return 4
    
    def get_rate_per_km(self) -> float:
        return 10.0
    
    def get_type(self) -> str:
        return "UberX"


class UberXL(Vehicle):
    def get_capacity(self) -> int:
        return 6
    
    def get_rate_per_km(self) -> float:
        return 15.0
    
    def get_type(self) -> str:
        return "UberXL"


class UberBlack(Vehicle):
    def get_capacity(self) -> int:
        return 4
    
    def get_rate_per_km(self) -> float:
        return 25.0
    
    def get_type(self) -> str:
        return "UberBlack"


class VehicleFactory:
    """Factory for creating different vehicle types"""
    
    _vehicle_map = {
        VehicleType.UBER_X: UberX,
        VehicleType.UBER_XL: UberXL,
        VehicleType.UBER_BLACK: UberBlack,
    }
    
    @staticmethod
    def create(vehicle_type: VehicleType, vehicle_id: str, driver_name: str) -> Vehicle:
        vehicle_class = VehicleFactory._vehicle_map.get(vehicle_type)
        if not vehicle_class:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
        return vehicle_class(vehicle_id, driver_name)


def demo_factory_pattern():
    """Demonstrate Factory Pattern"""
    print("\n" + "="*60)
    print("FACTORY PATTERN - Vehicle Creation Demo")
    print("="*60)
    
    # Client doesn't need to know about concrete classes
    vehicles = [
        VehicleFactory.create(VehicleType.UBER_X, "V001", "John"),
        VehicleFactory.create(VehicleType.UBER_XL, "V002", "Sarah"),
        VehicleFactory.create(VehicleType.UBER_BLACK, "V003", "Michael"),
    ]
    
    for vehicle in vehicles:
        print(f"  Created: {vehicle}")


# =============================================================================
# 3. SINGLETON PATTERN - Configuration Manager
# =============================================================================

class ConfigManager:
    """Thread-safe Singleton Configuration Manager"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = {
            "base_rate": 10.0,
            "surge_threshold": 0.8,
            "max_wait_time": 300,
            "cancellation_fee": 5.0,
        }
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        self._config[key] = value


def demo_singleton_pattern():
    """Demonstrate Singleton Pattern"""
    print("\n" + "="*60)
    print("SINGLETON PATTERN - Configuration Manager Demo")
    print("="*60)
    
    config1 = ConfigManager()
    config2 = ConfigManager()
    
    print(f"  Same instance? {config1 is config2}")  # True
    print(f"  Base rate: ${config1.get('base_rate')}")
    
    config1.set("base_rate", 15.0)
    print(f"  After update via config1, config2 sees: ${config2.get('base_rate')}")


# =============================================================================
# 4. OBSERVER PATTERN - Ride Status Updates
# =============================================================================

class RideStatus(Enum):
    REQUESTED = "requested"
    DRIVER_ASSIGNED = "driver_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class RideEvent:
    ride_id: str
    status: RideStatus
    timestamp: datetime = None
    
    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now()


class RideObserver(ABC):
    @abstractmethod
    def on_ride_update(self, event: RideEvent):
        pass


class RiderNotifier(RideObserver):
    def on_ride_update(self, event: RideEvent):
        messages = {
            RideStatus.DRIVER_ASSIGNED: "Your driver is on the way!",
            RideStatus.IN_PROGRESS: "Enjoy your ride!",
            RideStatus.COMPLETED: "Thanks for riding with us!",
        }
        if event.status in messages:
            print(f"    [RiderApp] {messages[event.status]}")


class DriverNotifier(RideObserver):
    def on_ride_update(self, event: RideEvent):
        if event.status == RideStatus.REQUESTED:
            print(f"    [DriverApp] New ride request: {event.ride_id}")


class AnalyticsTracker(RideObserver):
    def on_ride_update(self, event: RideEvent):
        print(f"    [Analytics] {event.ride_id}: {event.status.value}")


class BillingService(RideObserver):
    def on_ride_update(self, event: RideEvent):
        if event.status == RideStatus.COMPLETED:
            print(f"    [Billing] Generating invoice for {event.ride_id}")


class ObservableRide:
    def __init__(self, ride_id: str):
        self.ride_id = ride_id
        self._status = RideStatus.REQUESTED
        self._observers: List[RideObserver] = []
    
    def add_observer(self, observer: RideObserver):
        self._observers.append(observer)
    
    def _notify(self):
        event = RideEvent(self.ride_id, self._status)
        for observer in self._observers:
            observer.on_ride_update(event)
    
    def set_status(self, status: RideStatus):
        print(f"  Ride {self.ride_id} -> {status.value}")
        self._status = status
        self._notify()


def demo_observer_pattern():
    """Demonstrate Observer Pattern"""
    print("\n" + "="*60)
    print("OBSERVER PATTERN - Ride Status Updates Demo")
    print("="*60)
    
    ride = ObservableRide("R001")
    
    # Register observers
    ride.add_observer(RiderNotifier())
    ride.add_observer(DriverNotifier())
    ride.add_observer(AnalyticsTracker())
    ride.add_observer(BillingService())
    
    # Status changes trigger notifications
    ride.set_status(RideStatus.DRIVER_ASSIGNED)
    print()
    ride.set_status(RideStatus.IN_PROGRESS)
    print()
    ride.set_status(RideStatus.COMPLETED)


# =============================================================================
# 5. STATE PATTERN - Ride State Machine
# =============================================================================

class RideState(ABC):
    @abstractmethod
    def can_cancel(self) -> bool:
        pass
    
    @abstractmethod
    def can_start(self) -> bool:
        pass
    
    @abstractmethod
    def can_complete(self) -> bool:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


class RequestedState(RideState):
    def can_cancel(self) -> bool:
        return True  # Free cancellation
    
    def can_start(self) -> bool:
        return False  # Need driver first
    
    def can_complete(self) -> bool:
        return False
    
    def get_name(self) -> str:
        return "REQUESTED"


class DriverAssignedState(RideState):
    def can_cancel(self) -> bool:
        return True  # With fee
    
    def can_start(self) -> bool:
        return True
    
    def can_complete(self) -> bool:
        return False
    
    def get_name(self) -> str:
        return "DRIVER_ASSIGNED"


class InProgressState(RideState):
    def can_cancel(self) -> bool:
        return False  # Can't cancel ongoing
    
    def can_start(self) -> bool:
        return False  # Already started
    
    def can_complete(self) -> bool:
        return True
    
    def get_name(self) -> str:
        return "IN_PROGRESS"


class CompletedState(RideState):
    def can_cancel(self) -> bool:
        return False
    
    def can_start(self) -> bool:
        return False
    
    def can_complete(self) -> bool:
        return False
    
    def get_name(self) -> str:
        return "COMPLETED"


class StatefulRide:
    def __init__(self, ride_id: str):
        self.ride_id = ride_id
        self._state: RideState = RequestedState()
    
    def get_state(self) -> str:
        return self._state.get_name()
    
    def assign_driver(self):
        if isinstance(self._state, RequestedState):
            print(f"  Driver assigned to {self.ride_id}")
            self._state = DriverAssignedState()
        else:
            print(f"  Error: Cannot assign driver in {self.get_state()} state")
    
    def start(self):
        if self._state.can_start():
            print(f"  Ride {self.ride_id} started")
            self._state = InProgressState()
        else:
            print(f"  Error: Cannot start in {self.get_state()} state")
    
    def complete(self):
        if self._state.can_complete():
            print(f"  Ride {self.ride_id} completed")
            self._state = CompletedState()
        else:
            print(f"  Error: Cannot complete in {self.get_state()} state")
    
    def cancel(self):
        if self._state.can_cancel():
            fee = "$5 fee" if isinstance(self._state, DriverAssignedState) else "no fee"
            print(f"  Ride {self.ride_id} cancelled ({fee})")
        else:
            print(f"  Error: Cannot cancel in {self.get_state()} state")


def demo_state_pattern():
    """Demonstrate State Pattern"""
    print("\n" + "="*60)
    print("STATE PATTERN - Ride State Machine Demo")
    print("="*60)
    
    ride = StatefulRide("R001")
    print(f"  Initial state: {ride.get_state()}")
    
    # Happy path
    ride.assign_driver()
    print(f"  Current state: {ride.get_state()}")
    
    ride.start()
    print(f"  Current state: {ride.get_state()}")
    
    # Try invalid operation
    ride.cancel()  # Should fail
    
    ride.complete()
    print(f"  Current state: {ride.get_state()}")


# =============================================================================
# 6. DECORATOR PATTERN - Ride Add-ons
# =============================================================================

class RideServiceInterface(ABC):
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_cost(self) -> float:
        pass


class BasicRideService(RideServiceInterface):
    def __init__(self, distance_km: float):
        self.distance_km = distance_km
    
    def get_description(self) -> str:
        return f"Basic Ride ({self.distance_km}km)"
    
    def get_cost(self) -> float:
        return self.distance_km * 10


class RideAddonDecorator(RideServiceInterface, ABC):
    def __init__(self, ride: RideServiceInterface):
        self._ride = ride


class WifiAddon(RideAddonDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + WiFi"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 5


class ChildSeatAddon(RideAddonDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Child Seat"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 10


class PetFriendlyAddon(RideAddonDecorator):
    def get_description(self) -> str:
        return self._ride.get_description() + " + Pet Friendly"
    
    def get_cost(self) -> float:
        return self._ride.get_cost() + 8


def demo_decorator_pattern():
    """Demonstrate Decorator Pattern"""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - Ride Add-ons Demo")
    print("="*60)
    
    # Basic ride
    ride = BasicRideService(15)
    print(f"  {ride.get_description()}: ${ride.get_cost()}")
    
    # Add WiFi
    ride = WifiAddon(ride)
    print(f"  {ride.get_description()}: ${ride.get_cost()}")
    
    # Add child seat
    ride = ChildSeatAddon(ride)
    print(f"  {ride.get_description()}: ${ride.get_cost()}")
    
    # Fully loaded ride
    full_ride = PetFriendlyAddon(
        ChildSeatAddon(
            WifiAddon(
                BasicRideService(20)
            )
        )
    )
    print(f"  {full_ride.get_description()}: ${full_ride.get_cost()}")


# =============================================================================
# 7. BUILDER PATTERN - Complex Ride Request
# =============================================================================

@dataclass
class RideRequest:
    rider_id: str = None
    pickup: str = None
    dropoff: str = None
    vehicle_type: str = "UberX"
    scheduled_time: datetime = None
    promo_code: str = None
    notes: str = None
    child_seats: int = 0
    pet_friendly: bool = False
    
    def __str__(self):
        return f"""RideRequest:
    Rider: {self.rider_id}
    From: {self.pickup} -> To: {self.dropoff}
    Vehicle: {self.vehicle_type}
    Scheduled: {self.scheduled_time or 'Now'}
    Promo: {self.promo_code or 'None'}
    Child Seats: {self.child_seats}
    Pet Friendly: {self.pet_friendly}
    Notes: {self.notes or 'None'}"""


class RideRequestBuilder:
    def __init__(self):
        self._request = RideRequest()
    
    def rider(self, rider_id: str) -> 'RideRequestBuilder':
        self._request.rider_id = rider_id
        return self
    
    def pickup(self, location: str) -> 'RideRequestBuilder':
        self._request.pickup = location
        return self
    
    def dropoff(self, location: str) -> 'RideRequestBuilder':
        self._request.dropoff = location
        return self
    
    def vehicle(self, vehicle_type: str) -> 'RideRequestBuilder':
        self._request.vehicle_type = vehicle_type
        return self
    
    def schedule(self, time: datetime) -> 'RideRequestBuilder':
        self._request.scheduled_time = time
        return self
    
    def promo(self, code: str) -> 'RideRequestBuilder':
        self._request.promo_code = code
        return self
    
    def child_seats(self, count: int) -> 'RideRequestBuilder':
        self._request.child_seats = count
        return self
    
    def pet_friendly(self) -> 'RideRequestBuilder':
        self._request.pet_friendly = True
        return self
    
    def notes(self, text: str) -> 'RideRequestBuilder':
        self._request.notes = text
        return self
    
    def build(self) -> RideRequest:
        # Validate required fields
        if not self._request.rider_id:
            raise ValueError("Rider ID required")
        if not self._request.pickup or not self._request.dropoff:
            raise ValueError("Pickup and dropoff required")
        return self._request


def demo_builder_pattern():
    """Demonstrate Builder Pattern"""
    print("\n" + "="*60)
    print("BUILDER PATTERN - Complex Ride Request Demo")
    print("="*60)
    
    # Fluent builder
    request = (RideRequestBuilder()
        .rider("U123")
        .pickup("123 Main St")
        .dropoff("456 Oak Ave")
        .vehicle("UberXL")
        .child_seats(2)
        .pet_friendly()
        .promo("FAMILY20")
        .notes("Please call on arrival")
        .build())
    
    print(request)


# =============================================================================
# 8. COMMAND PATTERN - Undoable Operations
# =============================================================================

class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass


class BookRideCommand(Command):
    def __init__(self, rides: Dict, ride_id: str, rider_id: str):
        self.rides = rides
        self.ride_id = ride_id
        self.rider_id = rider_id
        self._executed = False
    
    def execute(self) -> bool:
        if self.ride_id not in self.rides:
            self.rides[self.ride_id] = {"rider": self.rider_id, "status": "booked"}
            self._executed = True
            print(f"    Booked ride {self.ride_id}")
            return True
        return False
    
    def undo(self) -> bool:
        if self._executed and self.ride_id in self.rides:
            del self.rides[self.ride_id]
            print(f"    Cancelled ride {self.ride_id}")
            return True
        return False
    
    def description(self) -> str:
        return f"Book({self.ride_id})"


class ChargeCommand(Command):
    def __init__(self, transactions: Dict, txn_id: str, user_id: str, amount: float):
        self.transactions = transactions
        self.txn_id = txn_id
        self.user_id = user_id
        self.amount = amount
        self._executed = False
    
    def execute(self) -> bool:
        self.transactions[self.txn_id] = {"user": self.user_id, "amount": self.amount}
        self._executed = True
        print(f"    Charged ${self.amount} to {self.user_id}")
        return True
    
    def undo(self) -> bool:
        if self._executed and self.txn_id in self.transactions:
            print(f"    Refunded ${self.amount} to {self.user_id}")
            del self.transactions[self.txn_id]
            return True
        return False
    
    def description(self) -> str:
        return f"Charge(${self.amount})"


class CommandManager:
    def __init__(self):
        self.history: List[Command] = []
    
    def execute(self, cmd: Command):
        if cmd.execute():
            self.history.append(cmd)
    
    def undo_last(self):
        if self.history:
            cmd = self.history.pop()
            cmd.undo()
            print(f"    Undone: {cmd.description()}")


def demo_command_pattern():
    """Demonstrate Command Pattern"""
    print("\n" + "="*60)
    print("COMMAND PATTERN - Undoable Operations Demo")
    print("="*60)
    
    rides = {}
    transactions = {}
    manager = CommandManager()
    
    print("  Executing commands:")
    manager.execute(BookRideCommand(rides, "R001", "U123"))
    manager.execute(ChargeCommand(transactions, "TXN001", "U123", 45.0))
    
    print("\n  Undoing last command:")
    manager.undo_last()
    
    print(f"\n  Remaining transactions: {transactions}")


# =============================================================================
# 9. CHAIN OF RESPONSIBILITY - Request Validation
# =============================================================================

class ValidationHandler(ABC):
    def __init__(self):
        self._next: Optional['ValidationHandler'] = None
    
    def set_next(self, handler: 'ValidationHandler') -> 'ValidationHandler':
        self._next = handler
        return handler
    
    def handle(self, request: dict) -> bool:
        if not self._validate(request):
            return False
        if self._next:
            return self._next.handle(request)
        return True
    
    @abstractmethod
    def _validate(self, request: dict) -> bool:
        pass


class UserValidationHandler(ValidationHandler):
    def _validate(self, request: dict) -> bool:
        valid_users = {"U001", "U002", "U123"}
        if request.get("user_id") in valid_users:
            print("    ✓ User validated")
            return True
        print("    ✗ Invalid user")
        request["error"] = "Invalid user"
        return False


class PaymentValidationHandler(ValidationHandler):
    def _validate(self, request: dict) -> bool:
        if request.get("payment_method") in ["card", "wallet"]:
            print("    ✓ Payment validated")
            return True
        print("    ✗ Invalid payment")
        request["error"] = "Invalid payment"
        return False


class LocationValidationHandler(ValidationHandler):
    def _validate(self, request: dict) -> bool:
        if request.get("pickup") and request.get("dropoff"):
            print("    ✓ Locations validated")
            return True
        print("    ✗ Invalid locations")
        request["error"] = "Invalid locations"
        return False


def demo_chain_of_responsibility():
    """Demonstrate Chain of Responsibility Pattern"""
    print("\n" + "="*60)
    print("CHAIN OF RESPONSIBILITY - Request Validation Demo")
    print("="*60)
    
    # Build chain
    chain = UserValidationHandler()
    chain.set_next(PaymentValidationHandler()).set_next(LocationValidationHandler())
    
    # Valid request
    print("  Testing valid request:")
    request1 = {"user_id": "U123", "payment_method": "card", "pickup": "A", "dropoff": "B"}
    result = chain.handle(request1)
    print(f"  Result: {'✓ Approved' if result else '✗ Rejected'}")
    
    # Invalid request
    print("\n  Testing invalid user:")
    request2 = {"user_id": "U999", "payment_method": "card", "pickup": "A", "dropoff": "B"}
    result = chain.handle(request2)
    print(f"  Result: {'✓ Approved' if result else '✗ Rejected'}")


# =============================================================================
# 10. TEMPLATE METHOD - Booking Flow
# =============================================================================

class BookingTemplate(ABC):
    """Template for booking flow"""
    
    def book(self, rider_id: str, pickup: str, dropoff: str) -> dict:
        """Template method - defines the algorithm"""
        print(f"\n  Booking {self.get_service_type()} ride...")
        
        # Step 1: Validate
        if not self._validate(rider_id, pickup, dropoff):
            return {"status": "failed", "reason": "validation"}
        
        # Step 2: Find driver (varies)
        driver = self._find_driver(pickup)
        
        # Step 3: Calculate fare (varies)
        fare = self._calculate_fare(pickup, dropoff)
        
        return {"status": "confirmed", "driver": driver, "fare": fare}
    
    def _validate(self, rider_id: str, pickup: str, dropoff: str) -> bool:
        print("    Validating request...")
        return bool(rider_id and pickup and dropoff)
    
    @abstractmethod
    def get_service_type(self) -> str:
        pass
    
    @abstractmethod
    def _find_driver(self, pickup: str) -> dict:
        pass
    
    @abstractmethod
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        pass


class UberXBooking(BookingTemplate):
    def get_service_type(self) -> str:
        return "UberX"
    
    def _find_driver(self, pickup: str) -> dict:
        print("    Finding nearest UberX driver...")
        return {"id": "D001", "name": "John"}
    
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        return 25.0


class UberBlackBooking(BookingTemplate):
    def get_service_type(self) -> str:
        return "UberBlack"
    
    def _find_driver(self, pickup: str) -> dict:
        print("    Finding premium UberBlack driver...")
        return {"id": "D002", "name": "Michael", "vehicle": "Mercedes"}
    
    def _calculate_fare(self, pickup: str, dropoff: str) -> float:
        return 55.0


def demo_template_method():
    """Demonstrate Template Method Pattern"""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - Booking Flow Demo")
    print("="*60)
    
    uber_x = UberXBooking()
    result1 = uber_x.book("U123", "Airport", "Downtown")
    print(f"  Result: {result1}")
    
    uber_black = UberBlackBooking()
    result2 = uber_black.book("U123", "Airport", "Downtown")
    print(f"  Result: {result2}")


# =============================================================================
# MAIN - Run all demos
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DESIGN PATTERNS PRACTICE - UBER LLD PREP")
    print("="*60)
    
    demo_strategy_pattern()
    demo_factory_pattern()
    demo_singleton_pattern()
    demo_observer_pattern()
    demo_state_pattern()
    demo_decorator_pattern()
    demo_builder_pattern()
    demo_command_pattern()
    demo_chain_of_responsibility()
    demo_template_method()
    
    print("\n" + "="*60)
    print("  ALL DEMOS COMPLETE!")
    print("  Practice modifying each pattern to learn better.")
    print("="*60 + "\n")

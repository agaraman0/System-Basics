# Design Pattern Selection Guide

> **Purpose:** Quickly identify which pattern to use based on the problem behavior or requirement.

---

## Table of Contents

1. [Quick Decision Matrix](#quick-decision-matrix)
2. [Pattern Selection by Problem Type](#pattern-selection-by-problem-type)
3. [Pattern Selection by Keyword](#pattern-selection-by-keyword)
4. [Decision Flowcharts](#decision-flowcharts)
5. [Common LLD Scenarios → Patterns](#common-lld-scenarios--patterns)
6. [Pattern Combinations](#pattern-combinations)
7. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
8. [Interview Cheat Sheet](#interview-cheat-sheet)

---

## Quick Decision Matrix

| If You Need To... | Use This Pattern |
|-------------------|------------------|
| Switch algorithms at runtime | **Strategy** |
| Create objects without specifying exact class | **Factory** |
| Ensure only one instance exists | **Singleton** |
| Notify multiple objects of state changes | **Observer** |
| Change behavior based on internal state | **State** |
| Add features without modifying class | **Decorator** |
| Build complex objects step by step | **Builder** |
| Encapsulate requests as objects (undo/queue) | **Command** |
| Define algorithm skeleton with customizable steps | **Template Method** |
| Pass request through chain of handlers | **Chain of Responsibility** |
| Provide simplified interface to complex system | **Facade** |
| Convert interface to another interface | **Adapter** |
| Compose objects into tree structures | **Composite** |
| Cache expensive objects | **Flyweight** |
| Control access to an object | **Proxy** |

---

## Pattern Selection by Problem Type

### 1. ALGORITHM VARIATION

**Symptom:** Multiple ways to do the same thing

```
"We need different pricing algorithms"
"Users can pay via card, wallet, or cash"
"Rides can be matched using distance, rating, or availability"
"Notifications can be sent via SMS, email, or push"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Algorithms are interchangeable | **Strategy** | Swap at runtime |
| Algorithm has fixed steps but varying implementations | **Template Method** | Reuse common logic |
| Need to add behavior dynamically | **Decorator** | Stack behaviors |

**Decision:**
```
Is the algorithm structure same but steps differ?
  YES → Template Method
  NO → Are algorithms completely different?
    YES → Strategy
    NO → Is it about adding optional features?
      YES → Decorator
```

---

### 2. OBJECT CREATION

**Symptom:** Complex or varying object instantiation

```
"Create different vehicle types based on input"
"Build a ride request with many optional parameters"
"Need exactly one config manager"
"Clone existing objects for efficiency"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Object type determined at runtime | **Factory** | Decouple creation |
| Object has many optional parameters | **Builder** | Fluent construction |
| Need exactly one instance | **Singleton** | Global access |
| Creating object is expensive, need copies | **Prototype** | Clone existing |
| Need families of related objects | **Abstract Factory** | Create related objects |

**Decision:**
```
Is object type unknown until runtime?
  YES → Factory
  NO → Does object have many optional params (>4)?
    YES → Builder
    NO → Need exactly one instance?
      YES → Singleton
      NO → Need to copy existing objects?
        YES → Prototype
```

---

### 3. STATE-DEPENDENT BEHAVIOR

**Symptom:** Object behaves differently based on its state

```
"Ride can be requested, assigned, in-progress, completed"
"Order can be placed, paid, shipped, delivered"
"Vending machine has idle, selecting, dispensing states"
"Document can be draft, moderation, published"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Many states with different behaviors | **State** | Encapsulate state logic |
| Simple flag-based behavior | No pattern needed | Use if-else |
| States form a workflow/pipeline | **State + Chain** | Combine patterns |

**Decision:**
```
Does behavior change significantly per state?
  YES → Are there >3 states with complex transitions?
    YES → State Pattern
    NO → Simple if-else may suffice
  NO → Look at other patterns
```

**State Pattern Indicators:**
- Methods have large switch/if-else on state
- Same operation does different things in different states
- State transitions are explicit
- Invalid operations exist in certain states

---

### 4. NOTIFICATION / EVENT HANDLING

**Symptom:** One change needs to notify many objects

```
"When ride status changes, notify rider, driver, analytics"
"When order is placed, update inventory, send email, log"
"When price changes, update all displays"
"When user logs in, update UI, start session, log activity"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| One-to-many notifications | **Observer** | Loose coupling |
| Event-driven architecture | **Observer + Mediator** | Centralized events |
| Need to undo/replay events | **Command + Observer** | Event sourcing |

**Decision:**
```
Does one object need to notify multiple objects?
  YES → Observer
  NO → Do objects need to communicate through central hub?
    YES → Mediator
    NO → Direct communication may suffice
```

---

### 5. REQUEST PROCESSING / VALIDATION

**Symptom:** Request goes through multiple checks/steps

```
"Validate user, then payment, then fraud, then location"
"Process refund through approval chain"
"Handle request with multiple possible handlers"
"Apply series of filters/transformations"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Sequential processing, any can reject | **Chain of Responsibility** | Pipeline |
| Request must go through all steps | **Template Method** | Fixed sequence |
| Request should be queued/undoable | **Command** | Encapsulate request |
| Multiple handlers, exactly one handles | **Chain of Responsibility** | Find handler |

**Decision:**
```
Can request be rejected at any step?
  YES → Chain of Responsibility
  NO → Must all steps execute in order?
    YES → Template Method
    NO → Should request be undoable/queueable?
      YES → Command
```

---

### 6. INTERFACE / COMPATIBILITY

**Symptom:** Incompatible interfaces or complex subsystems

```
"Legacy payment system has different interface"
"Need to simplify access to multiple microservices"
"Want to add logging without changing existing code"
"Control access to expensive resource"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Convert one interface to another | **Adapter** | Compatibility |
| Simplify complex subsystem | **Facade** | Single entry point |
| Add behavior transparently | **Proxy / Decorator** | Wrap original |
| Control access, lazy loading, caching | **Proxy** | Access control |

**Decision:**
```
Is interface incompatible with what you need?
  YES → Adapter
  NO → Is subsystem too complex?
    YES → Facade
    NO → Need to control access/add cross-cutting concerns?
      YES → Proxy
```

---

### 7. OBJECT STRUCTURE / COMPOSITION

**Symptom:** Objects form hierarchies or need dynamic features

```
"File system with files and folders (folders contain files)"
"UI components that contain other components"
"Add features like WiFi, child seat to basic ride"
"Menu items that can be single or combo"
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Part-whole hierarchies (tree structure) | **Composite** | Uniform treatment |
| Add features dynamically | **Decorator** | Stack features |
| Share common data among objects | **Flyweight** | Memory efficiency |

**Decision:**
```
Do objects form tree-like hierarchy?
  YES → Composite
  NO → Need to add features dynamically?
    YES → Decorator
    NO → Many similar objects wasting memory?
      YES → Flyweight
```

---

## Pattern Selection by Keyword

When you hear these words in requirements, think of these patterns:

### Action Keywords

| Keyword | Pattern |
|---------|---------|
| "different types of..." | Factory |
| "multiple ways to..." | Strategy |
| "based on state..." | State |
| "notify when..." | Observer |
| "validate then..." | Chain of Responsibility |
| "undo/redo..." | Command |
| "add-on/extra feature..." | Decorator |
| "optional parameters..." | Builder |
| "exactly one..." | Singleton |
| "convert/adapt..." | Adapter |
| "simplify access..." | Facade |
| "step by step process..." | Template Method |
| "hierarchy/tree..." | Composite |
| "lazy load/cache..." | Proxy |

### Domain Keywords (Uber/Ride-sharing)

| Domain Concept | Likely Patterns |
|----------------|-----------------|
| Pricing (normal, surge, pool) | Strategy |
| Vehicle types (X, XL, Black) | Factory |
| Ride status (requested → completed) | State, Observer |
| Ride features (WiFi, child seat) | Decorator |
| Booking request | Builder |
| Request validation | Chain of Responsibility |
| Driver matching algorithm | Strategy |
| Notifications | Observer |
| Configuration | Singleton |
| Payment processing | Strategy, Chain |
| Cancellation/Refund | Command |

---

## Decision Flowcharts

### Flowchart 1: Behavioral Pattern Selection

```
START: What's the primary concern?
│
├─► Object behavior varies by STATE?
│   └─► State Pattern
│
├─► Need to NOTIFY multiple objects?
│   └─► Observer Pattern
│
├─► Multiple ALGORITHMS for same task?
│   └─► Strategy Pattern
│
├─► Request goes through MULTIPLE HANDLERS?
│   └─► Chain of Responsibility
│
├─► Need to UNDO/QUEUE operations?
│   └─► Command Pattern
│
├─► Algorithm has FIXED STEPS but varying details?
│   └─► Template Method
│
└─► None of above → Consider Creational/Structural
```

### Flowchart 2: Creational Pattern Selection

```
START: How is object created?
│
├─► Type unknown until RUNTIME?
│   ├─► Single type decision → Factory Method
│   └─► Family of types → Abstract Factory
│
├─► Object has MANY PARAMETERS (>4)?
│   └─► Builder Pattern
│
├─► Need EXACTLY ONE instance?
│   └─► Singleton Pattern
│
├─► Object EXPENSIVE to create, need copies?
│   └─► Prototype Pattern
│
└─► Simple instantiation → new/constructor is fine
```

### Flowchart 3: Structural Pattern Selection

```
START: What's the structural concern?
│
├─► INTERFACE incompatible?
│   └─► Adapter Pattern
│
├─► Subsystem TOO COMPLEX?
│   └─► Facade Pattern
│
├─► Add features WITHOUT modifying class?
│   └─► Decorator Pattern
│
├─► Control ACCESS to object?
│   └─► Proxy Pattern
│
├─► TREE/hierarchy structure?
│   └─► Composite Pattern
│
├─► Many similar objects, MEMORY concern?
│   └─► Flyweight Pattern
│
└─► None → Direct composition/aggregation
```

---

## Common LLD Scenarios → Patterns

### Scenario 1: Parking Lot

| Requirement | Pattern |
|-------------|---------|
| Different vehicle types (car, bike, truck) | Factory |
| Different parking spot types | Factory |
| Parking spot states (available, occupied) | State |
| Payment calculation (hourly, daily, monthly) | Strategy |
| Entry/exit logging | Observer |
| Complex ParkingLot construction | Builder |

### Scenario 2: Ride Sharing (Uber/Lyft)

| Requirement | Pattern |
|-------------|---------|
| Vehicle types (X, XL, Black, Pool) | Factory |
| Pricing (normal, surge, discount) | Strategy |
| Ride states (requested → completed) | State |
| Notifications to rider/driver | Observer |
| Ride add-ons (WiFi, child seat) | Decorator |
| Ride request with many options | Builder |
| Request validation pipeline | Chain of Responsibility |
| Cancellation/refund | Command |
| Driver matching algorithm | Strategy |
| Configuration manager | Singleton |

### Scenario 3: Elevator System

| Requirement | Pattern |
|-------------|---------|
| Elevator states (idle, moving, stopped) | State |
| Direction algorithm (FCFS, SCAN, LOOK) | Strategy |
| Multiple elevators | Factory |
| Floor request queue | Command |
| Notify displays on each floor | Observer |

### Scenario 4: Library Management

| Requirement | Pattern |
|-------------|---------|
| Different item types (book, DVD, magazine) | Factory |
| Item states (available, borrowed, reserved) | State |
| Fine calculation strategies | Strategy |
| Notify members of availability | Observer |
| Search/filter pipeline | Chain of Responsibility |

### Scenario 5: Chess / Board Game

| Requirement | Pattern |
|-------------|---------|
| Different piece types (King, Queen, Pawn) | Factory |
| Game states (playing, check, checkmate) | State |
| Move validation | Chain of Responsibility |
| Move history (undo) | Command |
| Observer for UI updates | Observer |

### Scenario 6: Vending Machine

| Requirement | Pattern |
|-------------|---------|
| Machine states (idle, selecting, dispensing) | State |
| Payment methods (cash, card, mobile) | Strategy |
| Product types | Factory |
| Inventory update notifications | Observer |

### Scenario 7: Hotel Booking

| Requirement | Pattern |
|-------------|---------|
| Room types (single, double, suite) | Factory |
| Pricing (weekday, weekend, holiday) | Strategy |
| Booking states (pending, confirmed, cancelled) | State |
| Add-ons (breakfast, spa, late checkout) | Decorator |
| Complex booking with many options | Builder |
| Notification on booking changes | Observer |

### Scenario 8: Food Delivery (Swiggy/Zomato)

| Requirement | Pattern |
|-------------|---------|
| Order states (placed, preparing, delivered) | State |
| Delivery assignment algorithms | Strategy |
| Multiple restaurant types | Factory |
| Order customizations | Decorator |
| Real-time tracking updates | Observer |
| Order validation pipeline | Chain of Responsibility |
| Complex order creation | Builder |

---

## Pattern Combinations

Patterns often work together. Here are common combinations:

### Strategy + Factory

**When:** You have multiple algorithms AND need to create them dynamically.

```python
# Factory creates the right strategy
class PricingStrategyFactory:
    def create(self, ride_type: str) -> PricingStrategy:
        if ride_type == "surge":
            return SurgePricing()
        elif ride_type == "pool":
            return PoolPricing()
        return NormalPricing()
```

### State + Observer

**When:** State changes need to notify external systems.

```python
class Ride:
    def set_state(self, new_state: RideState):
        self._state = new_state
        self._notify_observers()  # Observer pattern
```

### Factory + Singleton

**When:** Factory itself should be single instance.

```python
class VehicleFactory:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### Builder + Factory

**When:** Builder creates complex object, Factory chooses which builder.

```python
class RideRequestDirector:
    def create_family_ride(self, builder: RideRequestBuilder):
        return builder.vehicle("XL").child_seats(2).build()
    
    def create_business_ride(self, builder: RideRequestBuilder):
        return builder.vehicle("Black").quiet_ride().build()
```

### Chain of Responsibility + Command

**When:** Commands go through validation chain before execution.

```python
class CommandProcessor:
    def process(self, command: Command):
        if self.validation_chain.handle(command):
            command.execute()
            self.history.append(command)
```

### Decorator + Strategy

**When:** Add features that each use different algorithms.

```python
class DynamicPricingDecorator(RideDecorator):
    def __init__(self, ride, pricing_strategy: PricingStrategy):
        super().__init__(ride)
        self.strategy = pricing_strategy
    
    def get_cost(self):
        base = self._ride.get_cost()
        return self.strategy.calculate(base)
```

### Template Method + Strategy

**When:** Algorithm skeleton is fixed, but specific steps use strategies.

```python
class BookingTemplate(ABC):
    def book(self, request):
        self.validate(request)
        fare = self.pricing_strategy.calculate(request)  # Strategy
        return self.create_booking(request, fare)
    
    def set_pricing_strategy(self, strategy: PricingStrategy):
        self.pricing_strategy = strategy
```

---

## Anti-Patterns to Avoid

### 1. Overusing Singleton

**Problem:** Makes testing hard, creates hidden dependencies.

```python
# ❌ BAD: Global access everywhere
class RideService:
    def calculate_fare(self):
        config = ConfigManager.get_instance()  # Hidden dependency
        return config.get("base_rate")

# ✅ GOOD: Inject dependency
class RideService:
    def __init__(self, config: ConfigManager):
        self.config = config  # Explicit dependency
```

### 2. Wrong State vs Strategy

**Problem:** Confusing when to use each.

```
State: Object's INTERNAL state changes its behavior
  - Ride is in "requested" state, then "in_progress" state
  - The SAME object changes behavior
  
Strategy: EXTERNAL algorithm is swapped
  - Pricing uses "normal" or "surge" algorithm
  - Algorithm is INJECTED from outside
```

### 3. Chain Without Exit

**Problem:** Chain must always have a way to terminate.

```python
# ❌ BAD: No end to chain
class Handler:
    def handle(self, request):
        # Process...
        return self._next.handle(request)  # What if _next is None?

# ✅ GOOD: Handle None case
class Handler:
    def handle(self, request):
        if not self._process(request):
            return False
        if self._next:
            return self._next.handle(request)
        return True  # End of chain = success
```

### 4. Factory for Simple Creation

**Problem:** Unnecessary complexity.

```python
# ❌ BAD: Factory for simple object
class UserFactory:
    def create(self, name):
        return User(name)  # Just use User(name) directly!

# ✅ GOOD: Factory when logic is complex
class VehicleFactory:
    def create(self, type):
        if type == "UberX":
            return UberX(default_config)
        elif type == "UberBlack":
            return UberBlack(premium_config, luxury_features)
```

### 5. God Observer

**Problem:** Observer does too much.

```python
# ❌ BAD: One observer handles everything
class MegaObserver:
    def on_ride_update(self, event):
        self.update_ui()
        self.send_notification()
        self.log_analytics()
        self.process_payment()

# ✅ GOOD: Single responsibility per observer
class UIObserver: ...
class NotificationObserver: ...
class AnalyticsObserver: ...
class PaymentObserver: ...
```

---

## Interview Cheat Sheet

### Quick Pattern Recognition

| See This... | Think This Pattern |
|-------------|-------------------|
| `if type == "A": ... elif type == "B":` | Factory |
| `if state == "X": ... elif state == "Y":` | State |
| `if algo == "1": ... elif algo == "2":` | Strategy |
| `notify_all()`, `subscribers.update()` | Observer |
| `handler.setNext(handler2)` | Chain of Responsibility |
| `execute()`, `undo()` | Command |
| `builder.setX().setY().build()` | Builder |
| `wrapper.operation()` delegates to `wrapped` | Decorator or Proxy |

### One-Liner Explanations

| Pattern | One-Liner |
|---------|-----------|
| Strategy | "Swap algorithms at runtime" |
| Factory | "Create objects without specifying class" |
| Singleton | "Ensure single instance" |
| Observer | "Notify many when one changes" |
| State | "Behavior changes with internal state" |
| Decorator | "Add features by wrapping" |
| Builder | "Build complex object step-by-step" |
| Command | "Encapsulate request as object" |
| Template Method | "Define skeleton, let subclasses fill steps" |
| Chain | "Pass request along handler chain" |
| Adapter | "Convert interface to another" |
| Facade | "Simplify complex subsystem" |
| Proxy | "Control access to object" |
| Composite | "Treat individuals and groups uniformly" |

### Interview Phrases

When you identify a pattern, say:

> "I see we have **[problem]**, so I'll use **[pattern]** because **[reason]**."

**Examples:**

- "I see we have multiple pricing algorithms, so I'll use **Strategy** because we can swap them at runtime without changing the Ride class."

- "I see the ride has different states with different valid operations, so I'll use **State** because it eliminates large conditionals and encapsulates state-specific behavior."

- "I see we need to notify multiple services when status changes, so I'll use **Observer** because it provides loose coupling - we can add/remove observers without changing the Ride class."

- "I see we have a chain of validations where any can reject, so I'll use **Chain of Responsibility** because each handler focuses on one concern and we can easily reorder them."

---

## Summary: The 5 Questions

When facing an LLD problem, ask these questions:

1. **What objects do I need to create?**
   - Complex creation → Factory, Builder, Singleton, Prototype

2. **How do objects behave?**
   - Varies by state → State
   - Varies by algorithm → Strategy
   - Needs undo/queue → Command

3. **How do objects communicate?**
   - One-to-many → Observer
   - Through chain → Chain of Responsibility
   - Through central hub → Mediator

4. **How do objects compose?**
   - Add features → Decorator
   - Tree structure → Composite
   - Simplify access → Facade

5. **How do interfaces connect?**
   - Incompatible → Adapter
   - Control access → Proxy

Master these questions, and you'll identify the right pattern every time!

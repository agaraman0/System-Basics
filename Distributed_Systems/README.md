# Distributed Systems & System Design

> Notes for high-level system design interviews.

---

## Files

| File | Description |
|------|-------------|
| [Distributed_Systems.md](Distributed_Systems.md) | Core distributed systems concepts |
| [Distributed_Systems_Complete_Notes.md](Distributed_Systems_Complete_Notes.md) | Comprehensive study notes |
| [FLPvsCAPvsPACELCvsByzantine.md](FLPvsCAPvsPACELCvsByzantine.md) | Theorem comparisons (FLP, CAP, PACELC, Byzantine) |

---

## Key Concepts Quick Reference

### CAP Theorem

| Property | Meaning |
|----------|---------|
| **C**onsistency | All nodes see same data |
| **A**vailability | System always responds |
| **P**artition Tolerance | Works despite network splits |

> Pick 2 of 3 during partition.

### Consistency Models

| Model | Guarantee |
|-------|-----------|
| Strong | All reads see latest write |
| Eventual | Eventually converges |
| Causal | Preserves cause-effect order |

### Common Patterns

| Pattern | Use Case |
|---------|----------|
| Replication | Fault tolerance, read scaling |
| Sharding | Write scaling, large datasets |
| Load Balancing | Distribute traffic |
| Caching | Reduce latency |
| Message Queues | Async processing |

---

## Study Order

1. Start with `Distributed_Systems.md` for foundations
2. Read `Distributed_Systems_Complete_Notes.md` for depth
3. Use `FLPvsCAPvsPACELCvsByzantine.md` for theorem clarity

---

*Back to [Main Index](../README.md)*

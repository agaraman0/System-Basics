Got it ✅ Let’s make a **one-page cheat sheet** right here (markdown style) that combines all the key **impossibility results in distributed systems**.

---

# 📘 Distributed Systems Impossibility Results – Cheat Sheet

---

## 🔴 Root Cause: Unreliable Networks

* **Messages can be delayed, lost, or reordered.**
* **Nodes can crash or act maliciously.**
* **No global clock → can’t distinguish “slow” from “failed.”**
  ➡️ This leads to **fundamental trade-offs.**

---

## ⚡ FLP Impossibility (1985)

* **Scope**: Consensus in asynchronous systems.
* **Statement**:
  In a fully asynchronous system, no deterministic algorithm can guarantee consensus if even one node may crash.
* **Trade-off**:

  * **Safety (agreement)** vs. **Liveness (progress)**.
* **Practical outcome**:
  Paxos, Raft guarantee **safety always**, **liveness eventually** (under partial synchrony).

---

## ⚡ CAP Theorem (2000)

* **Scope**: Data systems under partitions.
* **Statement**:
  In the presence of a partition, a system can provide at most 2 of:

  * **Consistency**: All nodes see the same data.
  * **Availability**: Every request gets a response.
  * **Partition Tolerance**: System continues despite message loss.
* **Trade-off**:

  * **CP**: Strong consistency, less availability (e.g., Spanner, Zookeeper).
  * **AP**: High availability, weaker consistency (e.g., Dynamo, Cassandra).
  * **CA**: Only possible if no partitions exist (idealized).

---

## ⚡ PACELC Theorem (2012)

* **Extension of CAP**: Describes trade-offs *when there is no partition*.
* **Statement**:

  * If **Partition (P)** → trade-off between **Availability (A)** and **Consistency (C)**.
  * Else (E) → trade-off between **Latency (L)** and **Consistency (C)**.
* **Example**:

  * Dynamo: **PA/EL** (AP under partition, favors latency otherwise).
  * Spanner: **PC/EC** (CP under partition, favors consistency otherwise).

---

## ⚡ Byzantine Generals Problem (1982)

* **Scope**: Consensus with malicious (Byzantine) faults.
* **Statement**:
  To reach agreement with Byzantine nodes, need **≥ 3f + 1 nodes to tolerate f faulty nodes**.
* **Trade-off**: Requires much higher replication & complexity.
* **Practical outcome**: Basis for **PBFT, Tendermint, Blockchain protocols**.

---

## 🧩 Summary Diagram (Mental Map)

```
Unreliable Networks
   ├── FLP → Safety vs. Liveness (Consensus)
   ├── CAP → Consistency vs. Availability (under Partition)
   ├── PACELC → Partition: CAP, Else: Latency vs. Consistency
   └── Byzantine → Agreement with malicious nodes (needs > 2/3 honest)
```

---

## 📝 Quick Recall Questions

1. What does FLP impossibility say about consensus?
2. During a partition, what does CAP force you to choose between?
3. What does PACELC add on top of CAP?
4. How many nodes are needed to tolerate f Byzantine faults?
5. Why can’t money fix latency the same way it fixes throughput?

---

# 📚 Distributed Systems - Complete Study Notes
*Comprehensive notes from "Distributed Systems for Fun and Profit" and related concepts*

---

## 📋 Table of Contents

1. [Chapter 1: Basics](#chapter-1-basics)
2. [Chapter 2: Up and Down the Level of Abstraction](#chapter-2-up-and-down-the-level-of-abstraction)
3. [Chapter 3: Time and Order](#chapter-3-time-and-order)
4. [Impossibility Results Cheat Sheet](#impossibility-results-cheat-sheet)
5. [Fallacies of Distributed Systems](#fallacies-of-distributed-systems)
6. [Quick Reference](#quick-reference)

---

## Chapter 1: Basics

### **1. Pre-Reading**
* **Theme of chapter**: Why distributed systems exist, core challenges, and key goals (scalability, performance, availability, fault tolerance).
* **Guiding Questions**:
  1. Why do we need distributed systems instead of just one big machine?
  2. What are the key trade-offs when scaling systems?
  3. What design techniques (partitioning, replication) are foundational?

### **2. First Pass (Big Picture)**
* Distributed systems = solving single-machine problems across multiple machines.
* Motivations: single-machine upgrades become impossible/too costly. Commodity hardware + fault-tolerant software is cheaper.
* Goals: **Scalability**, **Performance (esp. latency)**, **Availability (fault tolerance)**.
* Constraints: more nodes → more failures, more communication, more latency (speed of light).
* Design tools: **Partitioning** (divide data) + **Replication** (copy data).

### **3. Deep Dive (Active Notes)**

#### 🔑 Key Concepts
* **Distributed programming** = solving storage + computation across multiple machines.
* **Scalability** = handle growth in size, geography, and admin overhead without breaking.
* **Performance** = throughput + latency (latency limited by speed of light + hardware).
* **Availability** = uptime / (uptime + downtime), improved via redundancy.
* **Fault tolerance** = design for expected faults.
* **Abstractions/Models**:
  * System model (synchronous vs. asynchronous)
  * Failure model (crash, partition, Byzantine)
  * Consistency model (strong vs. eventual)

#### ✍️ My Explanation
* Distributed systems exist because **infinite single-node scaling isn't practical**.
* Every system design is a balance between **performance, availability, and consistency** under physical constraints.
* Partitioning and replication are the "divide & conquer" techniques at the heart of distributed system design.

#### 🖼 Diagram (mental map)
```
             ┌──────────┐
             │   Goals  │
             │ Scalability │
             │ Availability │
             │ Performance │
             └──────────┘
                   │
        ┌──────────┴──────────┐
   Partitioning          Replication
 (divide dataset)      (duplicate dataset)
```

### **4. Reinforcement (Recall Qs)**
1. Why can't we just keep upgrading single machines forever?
2. What are the three kinds of scalability discussed (size, geographic, administrative)?
3. How do partitioning and replication differ, and what trade-offs do they introduce?
4. Why is latency harder to solve with money than throughput?
5. What role do abstractions (system/failure/consistency models) play?

### **5. Application**
* **Real-world example**:
  * Amazon Dynamo → AP design, favors availability.
  * Google Spanner → CP design, favors consistency with TrueTime.
* **Limitation/assumption**: Network partitions and independent node failures are unavoidable → must pick trade-offs.
* **Own Example**:
  * A chat app → replicate messages across servers for low latency, but must handle message order inconsistencies.

---

## Chapter 2: Up and Down the Level of Abstraction

### **1. Pre-Reading**
* **Theme of chapter**: Abstractions in distributed systems, impossibility results (FLP & CAP), and consistency models.
* **Guiding Questions**:
  1. Why are abstractions necessary in distributed systems?
  2. What are the key impossibility results (FLP, CAP) and what do they imply?
  3. What are strong vs. weak consistency models, and why do they matter?

### **2. First Pass (Big Picture)**
* Abstractions make complex systems manageable, but they always ignore some reality.
* System models define assumptions about nodes, communication, and time.
* **Consensus problem** is central: all nodes must agree on one value.
* **FLP impossibility**: no consensus algorithm works under full asynchrony with even one crash.
* **CAP theorem**: can only have two of Consistency, Availability, Partition tolerance.
* Consistency isn't binary → many models exist beyond "strong consistency."

### **3. Deep Dive (Active Notes)**

#### 🔑 Key Concepts
* **System Model**:
  * Nodes run concurrently, local state only, independent failures.
  * Communication links may delay/drop messages.
  * Clocks unsynchronized → order is not global.

* **Consensus Problem** (Agreement, Integrity, Termination, Validity).

* **FLP Impossibility (1985)**: No deterministic consensus algorithm under asynchronous model with crash failures. → Tradeoff: can't guarantee both safety and liveness.

* **CAP Theorem (Brewer, 2000)**:
  * Consistency: all nodes see same data.
  * Availability: system continues serving.
  * Partition tolerance: system continues despite message loss.
  * Only two out of three at a time.

* **Consistency Models**:
  * **Strong**: Linearizable, Sequential.
  * **Weak**: Causal, Eventual, Client-centric.
  * "Consistency = contract between system and programmer."

#### ✍️ My Explanation
* Abstractions hide complexity but introduce trade-offs: too much hiding = inefficiency, too much exposure = confusion.
* FLP shows the *limits* of what's possible in asynchronous distributed systems.
* CAP highlights real-world trade-offs: during partitions, must choose between availability and strong consistency.
* "Consistency" is not one thing but a spectrum of models, each suited to different applications.

#### 🖼 Diagram (mental map)
```
Consensus → FLP (impossible under async+crash) 
CAP → Pick 2 out of {C, A, P}
   CA: Consistency + Availability (no partitions)
   CP: Consistency + Partition tolerance (lose some availability)
   AP: Availability + Partition tolerance (weaker consistency)
```

### **4. Reinforcement (Recall Qs)**
1. What does a system model define in distributed systems?
2. Why can't consensus be guaranteed in asynchronous systems (FLP)?
3. What does CAP theorem mean in practice for system designers?
4. Difference between linearizable and sequential consistency?
5. Why is "consistency" not a single well-defined property?

### **5. Application**
* **Real-world examples**:
  * **CA**: Two-phase commit in traditional databases.
  * **CP**: Paxos, Raft (majority quorum).
  * **AP**: Dynamo, Cassandra (accept divergence + reconcile later).
* **Limitation**: Strong consistency = high latency + reduced availability under partitions.
* **Own Example**: Social media feed: Eventual consistency works (you don't need strict ordering), but banking transactions demand strong consistency.

---

## Chapter 3: Time and Order

### **1. Pre-Reading**
* **Theme of chapter**: How distributed systems deal with time, ordering of events, and causality when there is no global clock.
* **Guiding Questions**:
  1. Why can't we rely on physical clocks in distributed systems?
  2. What are logical clocks, and how do they help?
  3. What's the difference between total order and causal order?
  4. How do vector clocks extend Lamport clocks?

### **2. First Pass (Big Picture)**
* Physical clocks drift → synchronization impossible across all nodes.
* Instead, distributed systems use **logical clocks** to capture event ordering.
* **Lamport clocks** provide a way to order events consistently, but not capture causality perfectly.
* **Vector clocks** capture causality more precisely but at higher overhead.
* Ordering is critical for consistency models and replication.

### **3. Deep Dive (Active Notes)**

#### 🔑 Key Concepts
* **Problem with physical time**:
  * Clocks drift → hard to keep synchronized.
  * Network delays make comparing timestamps unreliable.

* **Happens-Before Relation (→)**:
  * If event A happens before B in the same process, A → B.
  * If A is a message send and B is the receive, A → B.
  * Otherwise, events are concurrent.

* **Lamport Logical Clocks**:
  * Each process maintains a counter.
  * On each event, increment counter.
  * On message send, include counter. On receive, set local counter = max(local, received) + 1.
  * Provides a consistent total order, but doesn't capture concurrency explicitly.

* **Vector Clocks**:
  * Each process maintains a vector of counters (one per process).
  * Update rules:
    * On event: increment own counter.
    * On send: attach vector.
    * On receive: take element-wise max.
  * Captures causality: if V(A) < V(B), then A → B. If incomparable, events are concurrent.

* **Ordering Guarantees**:
  * **Total order** → all events ordered (may be artificial).
  * **Causal order** → respects causality but allows concurrency.

#### ✍️ My Explanation
* Physical time is unreliable in distributed systems → we shift focus from "when" to "what order."
* Lamport clocks give a **total order** but overapproximate causality.
* Vector clocks give **partial order** that exactly matches causality but cost more (O(n) storage).
* Choice depends on trade-off between **precision** and **efficiency**.

#### 🖼 Diagram (mental map)
```
Event Ordering
   ├── Physical clocks ❌ drift & delays
   ├── Logical clocks ✔
   │     ├── Lamport: total order (coarse)
   │     └── Vector: causal order (precise)
   └── Happens-before relation: defines causality
```

### **4. Reinforcement (Recall Qs)**
1. Why can't we rely on physical clocks for event ordering in distributed systems?
2. What is the "happens-before" relation?
3. How do Lamport clocks assign order to events?
4. What limitation do Lamport clocks have in terms of causality?
5. How do vector clocks improve on Lamport clocks?
6. When are two events considered concurrent in vector clocks?

### **5. Application**
* **Real-world examples**:
  * **Version control systems** (Git): use DAGs to track causality between commits.
  * **Distributed databases**: vector clocks used to detect conflicting updates (e.g., Dynamo).
* **Limitation**: Vector clocks scale poorly (require vector size = number of processes).
* **Own Example**: In a chat system, Lamport clocks could order all messages, but vector clocks can show which messages are replies and which are independent.

---

## Impossibility Results Cheat Sheet

### 🔴 Root Cause: Unreliable Networks
* **Messages can be delayed, lost, or reordered.**
* **Nodes can crash or act maliciously.**
* **No global clock → can't distinguish "slow" from "failed."**
  ➡️ This leads to **fundamental trade-offs.**

### ⚡ FLP Impossibility (1985)
* **Scope**: Consensus in asynchronous systems.
* **Statement**: In a fully asynchronous system, no deterministic algorithm can guarantee consensus if even one node may crash.
* **Trade-off**: **Safety (agreement)** vs. **Liveness (progress)**.
* **Practical outcome**: Paxos, Raft guarantee **safety always**, **liveness eventually** (under partial synchrony).

### ⚡ CAP Theorem (2000)
* **Scope**: Data systems under partitions.
* **Statement**: In the presence of a partition, a system can provide at most 2 of:
  * **Consistency**: All nodes see the same data.
  * **Availability**: Every request gets a response.
  * **Partition Tolerance**: System continues despite message loss.
* **Trade-off**:
  * **CP**: Strong consistency, less availability (e.g., Spanner, Zookeeper).
  * **AP**: High availability, weaker consistency (e.g., Dynamo, Cassandra).
  * **CA**: Only possible if no partitions exist (idealized).

### ⚡ PACELC Theorem (2012)
* **Extension of CAP**: Describes trade-offs *when there is no partition*.
* **Statement**:
  * If **Partition (P)** → trade-off between **Availability (A)** and **Consistency (C)**.
  * Else (E) → trade-off between **Latency (L)** and **Consistency (C)**.
* **Example**:
  * Dynamo: **PA/EL** (AP under partition, favors latency otherwise).
  * Spanner: **PC/EC** (CP under partition, favors consistency otherwise).

### ⚡ Byzantine Generals Problem (1982)
* **Scope**: Consensus with malicious (Byzantine) faults.
* **Statement**: To reach agreement with Byzantine nodes, need **≥ 3f + 1 nodes to tolerate f faulty nodes**.
* **Trade-off**: Requires much higher replication & complexity.
* **Practical outcome**: Basis for **PBFT, Tendermint, Blockchain protocols**.

### 🧩 Summary Diagram (Mental Map)
```
Unreliable Networks
   ├── FLP → Safety vs. Liveness (Consensus)
   ├── CAP → Consistency vs. Availability (under Partition)
   ├── PACELC → Partition: CAP, Else: Latency vs. Consistency
   └── Byzantine → Agreement with malicious nodes (needs > 2/3 honest)
```

---

## Fallacies of Distributed Systems

### The Fallacies
1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

### The Effects of the Fallacies
* **Network reliability**: Software applications are written with little error-handling on networking errors. During a network outage, such applications may stall or infinitely wait for an answer packet, permanently consuming memory or other resources. When the failed network becomes available, those applications may also fail to retry any stalled operations or require a (manual) restart.

* **Latency ignorance**: Ignorance of network latency, and of the packet loss it can cause, induces application- and transport-layer developers to allow unbounded traffic, greatly increasing dropped packets and wasting bandwidth.

* **Bandwidth limits**: Ignorance of bandwidth limits on the part of traffic senders can result in bottlenecks.

* **Security complacency**: Complacency regarding network security results in being blindsided by malicious users and programs that continually adapt to security measures.

* **Topology changes**: Changes in network topology can have effects on both bandwidth and latency issues, and therefore can have similar problems.

* **Multiple administrators**: Multiple administrators, as with subnets for rival companies, may institute conflicting policies of which senders of network traffic must be aware in order to complete their desired paths.

* **Transport costs**: The "hidden" costs of building and maintaining a network or subnet are non-negligible and must consequently be noted in budgets to avoid vast shortfalls.

* **Network homogeneity**: If a system assumes a homogeneous network, then it can lead to the same problems that result from the first three fallacies.

---

## Quick Reference

### 📝 Quick Recall Questions
1. What does FLP impossibility say about consensus?
2. During a partition, what does CAP force you to choose between?
3. What does PACELC add on top of CAP?
4. How many nodes are needed to tolerate f Byzantine faults?
5. Why can't money fix latency the same way it fixes throughput?

### 🎯 Key Design Patterns
- **Partitioning**: Divide data across nodes for scalability
- **Replication**: Copy data across nodes for availability
- **Consensus**: Agree on values despite failures
- **Logical Clocks**: Order events without global time
- **Vector Clocks**: Track causality precisely

### 🔧 System Design Trade-offs
- **Consistency vs Availability** (CAP)
- **Latency vs Consistency** (PACELC)
- **Safety vs Liveness** (FLP)
- **Precision vs Efficiency** (Lamport vs Vector clocks)

---

*Source: "Distributed Systems for Fun and Profit" by Mixu, Wikipedia, and various distributed systems literature*

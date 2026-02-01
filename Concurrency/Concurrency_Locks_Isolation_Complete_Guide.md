# Complete Guide: Concurrency, Locks, Isolation & Real-Time Systems

> A comprehensive deep-dive into database concurrency control, locking mechanisms, isolation levels, and real-time system design patterns.

---

## Table of Contents

1. [Kafka: Consumer vs Consumer Group](#1-kafka-consumer-vs-consumer-group)
2. [Real-Time Systems Tech Stack](#2-real-time-systems-tech-stack)
3. [Dealing with High Contention](#3-dealing-with-high-contention)
4. [Types of Locking Mechanisms](#4-types-of-locking-mechanisms)
5. [S-Lock vs X-Lock Deep Dive](#5-s-lock-vs-x-lock-deep-dive)
6. [Database Isolation Levels](#6-database-isolation-levels)
7. [How Locks Implement Isolation](#7-how-locks-implement-isolation)
8. [Putting It All Together](#8-putting-it-all-together)

---

# 1. Kafka: Consumer vs Consumer Group

## 1.1 Basic Concepts

### What is a Consumer?
A **consumer** is a single client application instance that reads (consumes) messages from Kafka topics. It's the basic unit that subscribes to topics and processes records.

```java
// A single Kafka consumer
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("my-topic"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        System.out.printf("offset = %d, key = %s, value = %s%n", 
            record.offset(), record.key(), record.value());
    }
}
```

### What is a Consumer Group?
A **consumer group** is a logical grouping of consumers that work together to consume messages from a topic. All consumers in a group share a common `group.id`.

```java
// Multiple consumers in the SAME group share the workload
props.put("group.id", "order-processing-group");  // This makes them part of a group
```

## 1.2 Key Differences

| Aspect | Single Consumer | Consumer Group |
|--------|-----------------|----------------|
| **Definition** | One client instance | Multiple instances with same `group.id` |
| **Partition Handling** | Reads all assigned partitions | Partitions distributed among members |
| **Parallelism** | Single-threaded consumption | Horizontal scaling |
| **Offset Tracking** | Manual or auto per consumer | Kafka tracks per group |
| **Fault Tolerance** | Single point of failure | Automatic rebalancing |
| **Use Case** | Simple apps, testing | Production workloads |

## 1.3 How Consumer Groups Work

### Partition Assignment

```
Topic: "orders" with 6 partitions (P0, P1, P2, P3, P4, P5)

┌─────────────────────────────────────────────────────────┐
│              CONSUMER GROUP: "order-processors"         │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Consumer 1  │  │  Consumer 2  │  │  Consumer 3  │  │
│  │   (P0, P1)   │  │   (P2, P3)   │  │   (P4, P5)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘

Each consumer processes 2 partitions = Load balanced!
```

### Multiple Consumer Groups (Pub/Sub Pattern)

```
Topic: "orders" (3 partitions)
         │
         ├───────────────────────────────────────┐
         │                                       │
         ▼                                       ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│  GROUP A: "analytics"   │      │  GROUP B: "billing"     │
│  ┌─────────┐ ┌─────────┐│      │  ┌─────────┐           │
│  │Consumer1│ │Consumer2││      │  │Consumer1│           │
│  │ (P0,P1) │ │  (P2)   ││      │  │(P0,P1,P2)│           │
│  └─────────┘ └─────────┘│      │  └─────────┘           │
└─────────────────────────┘      └─────────────────────────┘

Both groups receive ALL messages independently!
```

### The Golden Rules

1. **Within a group**: Each partition is consumed by **exactly one** consumer
2. **Across groups**: Each group gets its **own copy** of all messages
3. **Max parallelism**: `consumers in group ≤ partitions` (extra consumers are idle)

## 1.4 Rebalancing

When consumers join or leave a group, Kafka **rebalances** partition assignments.

```
BEFORE: 2 consumers, 4 partitions
┌──────────────┐  ┌──────────────┐
│  Consumer 1  │  │  Consumer 2  │
│  (P0, P1)    │  │  (P2, P3)    │
└──────────────┘  └──────────────┘

Consumer 2 crashes...

AFTER REBALANCE: 1 consumer, 4 partitions
┌────────────────────────────────┐
│          Consumer 1            │
│      (P0, P1, P2, P3)         │
└────────────────────────────────┘
```

### Rebalancing Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Range** | Assign consecutive partitions | Co-partitioned topics |
| **RoundRobin** | Distribute evenly | General purpose |
| **Sticky** | Minimize movement | Reduce rebalance impact |
| **CooperativeSticky** | Incremental rebalance | Zero downtime |

## 1.5 Complete Example

```java
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.*;

public class OrderConsumer {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processing-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, 
            "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, 
            "org.apache.kafka.common.serialization.StringDeserializer");
        
        // Auto commit offsets every 5 seconds
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "5000");
        
        // Start from earliest if no committed offset
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList("orders"));

        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf(
                        "Partition: %d, Offset: %d, Key: %s, Value: %s%n",
                        record.partition(), record.offset(), 
                        record.key(), record.value()
                    );
                    
                    // Process the order
                    processOrder(record.value());
                }
            }
        } finally {
            consumer.close();
        }
    }
    
    private static void processOrder(String orderJson) {
        // Business logic here
    }
}
```

## 1.6 When to Use What

| Scenario | Recommendation |
|----------|---------------|
| Development/testing | Single consumer |
| Low volume topic | Single consumer in a group |
| High throughput needed | Multiple consumers in a group |
| Multiple apps need same data | Multiple consumer groups |
| Event sourcing / replay | Consumer group with specific offset |

---

# 2. Real-Time Systems Tech Stack

## 2.1 Core Components Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    REAL-TIME SYSTEM LAYERS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Ingestion│───▶│Processing│───▶│ Storage  │───▶│ Serving  │  │
│  │  Layer   │    │  Layer   │    │  Layer   │    │  Layer   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                  │
│   • Kafka         • Flink        • Redis         • WebSocket    │
│   • Pulsar        • Spark        • Cassandra     • gRPC         │
│   • Kinesis       • Kafka        • ClickHouse    • REST         │
│                     Streams      • TimescaleDB                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Technology Deep Dive

### Message Brokers (Ingestion Layer)

| Technology | Throughput | Latency | Best For |
|------------|------------|---------|----------|
| **Kafka** | Millions/sec | 2-10ms | Event streaming, logs, replay |
| **Redis Streams** | 100K/sec | <1ms | Simple streaming, low latency |
| **Apache Pulsar** | Millions/sec | 5-10ms | Multi-tenancy, geo-replication |
| **AWS Kinesis** | 1M/sec | 70-200ms | AWS ecosystem |
| **RabbitMQ** | 50K/sec | 1-5ms | Task queues, routing |

### Stream Processing

| Technology | Model | Latency | Use Case |
|------------|-------|---------|----------|
| **Apache Flink** | True streaming | Milliseconds | Complex event processing |
| **Kafka Streams** | Streaming | Milliseconds | Kafka-native processing |
| **Spark Streaming** | Micro-batch | Seconds | Batch + stream unified |
| **Apache Storm** | True streaming | Milliseconds | Legacy, low-latency |

### Real-Time Databases

| Technology | Type | Latency | Best For |
|------------|------|---------|----------|
| **Redis** | In-memory KV | <1ms | Caching, sessions, counters |
| **ScyllaDB** | Wide-column | 1-5ms | High write throughput |
| **Cassandra** | Wide-column | 5-10ms | Time-series, write-heavy |
| **ClickHouse** | Column OLAP | 10-100ms | Real-time analytics |
| **Druid** | Column OLAP | 100-500ms | OLAP, slice-and-dice |

## 2.3 Architecture Patterns by Use Case

### Use Case 1: Live Comments (YouTube, Twitch)

**Requirements:**
- Sub-second delivery to viewers
- Handle millions of concurrent viewers
- Spam/moderation filtering
- Persistent storage for replay

```
┌─────────────────────────────────────────────────────────────────┐
│                   LIVE COMMENTS ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────┘

        User Posts Comment
               │
               ▼
┌─────────────────────────┐
│      API Gateway        │  ← Rate limiting (100 comments/user/min)
│    (Kong / Envoy)       │  ← Authentication
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│         Kafka           │  ← Topic: comments.raw
│   (Partitioned by       │  ← Partition key: room_id
│      room_id)           │  ← Retention: 7 days
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────────────┐
│  Flink  │   │  Flink (Async)  │
│ (Sync)  │   │                 │
│         │   │  • ML Spam      │
│ • Basic │   │    Detection    │
│   Filter│   │  • Sentiment    │
│ • Enrich│   │    Analysis     │
└────┬────┘   └────────┬────────┘
     │                 │
     ▼                 ▼
┌─────────────────────────┐
│    Kafka (Processed)    │  ← Topic: comments.processed
└───────────┬─────────────┘
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
┌───────┐ ┌─────┐ ┌──────────┐
│Redis  │ │Cass-│ │Centrifugo│
│Pub/Sub│ │andra│ │WebSocket │
└───┬───┘ └──┬──┘ └────┬─────┘
    │        │         │
    └────────┼─────────┘
             │
             ▼
        ┌─────────┐
        │ Viewers │
        └─────────┘
```

**Tech Stack:**
```yaml
ingestion:
  - api_gateway: Kong
  - message_broker: Kafka

processing:
  - stream_processor: Apache Flink
  - ml_inference: TensorFlow Serving (spam detection)

storage:
  - hot_cache: Redis (recent comments, viewer counts)
  - persistent: Cassandra (all comments)
  - search: Elasticsearch (comment search)

delivery:
  - websocket: Centrifugo
  - pubsub: Redis Pub/Sub (per-room fan-out)
```

**Code Example - Comment Processing with Flink:**

```java
public class CommentProcessor {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Kafka source
        KafkaSource<Comment> source = KafkaSource.<Comment>builder()
            .setBootstrapServers("localhost:9092")
            .setTopics("comments.raw")
            .setGroupId("comment-processor")
            .setValueOnlyDeserializer(new CommentDeserializer())
            .build();
        
        DataStream<Comment> comments = env.fromSource(source, 
            WatermarkStrategy.noWatermarks(), "Kafka Source");
        
        // Processing pipeline
        DataStream<ProcessedComment> processed = comments
            // Filter empty comments
            .filter(c -> c.getText() != null && !c.getText().isEmpty())
            // Basic profanity filter
            .filter(c -> !containsProfanity(c.getText()))
            // Enrich with user info
            .map(c -> enrichWithUserInfo(c))
            // Rate limit per user (max 10/minute)
            .keyBy(Comment::getUserId)
            .process(new RateLimitFunction(10, Duration.ofMinutes(1)));
        
        // Sink to processed topic
        processed.sinkTo(KafkaSink.<ProcessedComment>builder()
            .setBootstrapServers("localhost:9092")
            .setRecordSerializer(new ProcessedCommentSerializer())
            .build());
        
        env.execute("Comment Processing Job");
    }
}
```

### Use Case 2: Ad Clicks / Real-Time Analytics

**Requirements:**
- Handle 1M+ clicks/second
- Real-time fraud detection
- Sub-second aggregations for dashboards
- Accurate billing

```
┌─────────────────────────────────────────────────────────────────┐
│                   AD CLICK TRACKING ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────────┘

    Ad Click Event (Browser/Mobile)
               │
               ▼
┌─────────────────────────┐
│    CDN Edge (Fastly)    │  ← Log click at edge
│    Click Pixel/API      │  ← Return 1x1 pixel
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│         Kafka           │  ← Topic: ad.clicks.raw
│   (1000 partitions)     │  ← Partition by: advertiser_id
│                         │  ← Retention: 30 days (audit)
└───────────┬─────────────┘
            │
    ┌───────┴───────────────────┐
    │                           │
    ▼                           ▼
┌─────────────────┐      ┌─────────────────┐
│  Flink Job 1    │      │  Flink Job 2    │
│  (Enrichment)   │      │  (Fraud Detect) │
│                 │      │                 │
│ • IP → Geo      │      │ • Click patterns│
│ • User agent    │      │ • Bot detection │
│ • Campaign info │      │ • Anomaly score │
└────────┬────────┘      └────────┬────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  Kafka (Clean)  │      │ Redis (Flags)   │
│ ad.clicks.valid │      │ blocked_ips     │
└────────┬────────┘      └─────────────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌──────────────┐   ┌──────────────┐
│  ClickHouse  │   │    Redis     │
│  (Analytics) │   │  (Counters)  │
│              │   │              │
│ • Raw clicks │   │ • campaign:  │
│ • Aggregates │   │   clicks:123 │
│ • Dashboards │   │ • Real-time  │
└──────────────┘   │   counts     │
                   └──────────────┘
```

**ClickHouse Schema for Real-Time Analytics:**

```sql
-- Clicks table (MergeTree for fast inserts)
CREATE TABLE ad_clicks (
    click_id UUID,
    advertiser_id UInt32,
    campaign_id UInt32,
    creative_id UInt32,
    publisher_id UInt32,
    user_id String,
    ip_address IPv4,
    country String,
    device_type Enum('desktop', 'mobile', 'tablet'),
    click_timestamp DateTime64(3),
    fraud_score Float32,
    
    -- Materialized columns for fast filtering
    click_date Date MATERIALIZED toDate(click_timestamp),
    click_hour UInt8 MATERIALIZED toHour(click_timestamp)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(click_timestamp)
ORDER BY (advertiser_id, campaign_id, click_timestamp)
TTL click_timestamp + INTERVAL 90 DAY;

-- Pre-aggregated view (Materialized View)
CREATE MATERIALIZED VIEW ad_clicks_hourly_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(click_hour_start)
ORDER BY (advertiser_id, campaign_id, click_hour_start)
AS SELECT
    advertiser_id,
    campaign_id,
    toStartOfHour(click_timestamp) as click_hour_start,
    count() as click_count,
    countIf(fraud_score < 0.5) as valid_click_count,
    uniqExact(user_id) as unique_users
FROM ad_clicks
GROUP BY advertiser_id, campaign_id, click_hour_start;

-- Query: Real-time dashboard (sub-second response)
SELECT 
    campaign_id,
    sum(click_count) as total_clicks,
    sum(valid_click_count) as valid_clicks,
    sum(unique_users) as unique_users
FROM ad_clicks_hourly_mv
WHERE advertiser_id = 12345
  AND click_hour_start >= now() - INTERVAL 24 HOUR
GROUP BY campaign_id
ORDER BY total_clicks DESC;
```

### Use Case 3: Real-Time Notifications / Activity Feeds

```
┌─────────────────────────────────────────────────────────────────┐
│                 NOTIFICATION SYSTEM ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────────┘

   Event Source (Post, Like, Follow, etc.)
               │
               ▼
┌─────────────────────────┐
│         Kafka           │  ← Topic per event type
│  (events.posts,         │
│   events.likes, etc.)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Flink (Fan-out)      │  ← Lookup followers
│                         │  ← Generate notifications
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────────┐  ┌──────────────────┐
│    Redis    │  │  Push Service    │
│  Sorted Set │  │                  │
│  (per user) │  │ • FCM (Android)  │
│             │  │ • APNs (iOS)     │
│ feed:user:1 │  │ • WebSocket      │
│ feed:user:2 │  │ • Email (batch)  │
└─────────────┘  └──────────────────┘

```

**Redis Feed Implementation:**

```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0)

class FeedService:
    def __init__(self):
        self.feed_size_limit = 1000  # Keep last 1000 items
    
    def add_to_feed(self, user_id: str, activity: dict):
        """Add activity to user's feed (fan-out on write)"""
        feed_key = f"feed:{user_id}"
        
        # Score is timestamp for ordering
        score = time.time()
        
        # Add to sorted set
        r.zadd(feed_key, {json.dumps(activity): score})
        
        # Trim to keep only recent items
        r.zremrangebyrank(feed_key, 0, -self.feed_size_limit - 1)
        
        # Set TTL for inactive users
        r.expire(feed_key, 60 * 60 * 24 * 30)  # 30 days
    
    def get_feed(self, user_id: str, offset: int = 0, limit: int = 20):
        """Get paginated feed for user"""
        feed_key = f"feed:{user_id}"
        
        # Get items in reverse chronological order
        items = r.zrevrange(feed_key, offset, offset + limit - 1)
        
        return [json.loads(item) for item in items]
    
    def fan_out_post(self, author_id: str, post: dict):
        """Fan-out new post to all followers"""
        # Get followers (could be from DB or Redis set)
        follower_ids = self.get_followers(author_id)
        
        activity = {
            "type": "new_post",
            "actor_id": author_id,
            "post_id": post["id"],
            "preview": post["content"][:100],
            "timestamp": time.time()
        }
        
        # Fan-out to each follower (use pipeline for efficiency)
        pipe = r.pipeline()
        for follower_id in follower_ids:
            feed_key = f"feed:{follower_id}"
            pipe.zadd(feed_key, {json.dumps(activity): activity["timestamp"]})
            pipe.zremrangebyrank(feed_key, 0, -self.feed_size_limit - 1)
        
        pipe.execute()
```

## 2.4 Scale-Based Recommendations

| Scale | Recommended Stack |
|-------|-------------------|
| **Startup (<10K concurrent)** | Redis Pub/Sub + PostgreSQL + Socket.io + Single server |
| **Growth (10K-100K)** | Kafka + Redis + PostgreSQL + Centrifugo + 3-5 servers |
| **Scale (100K-1M)** | Kafka + Flink + Redis Cluster + Cassandra + ClickHouse |
| **Massive (1M+)** | Kafka/Pulsar + Flink + ScyllaDB + ClickHouse + Custom WS infra |

## 2.5 Latency Targets by Use Case

| Use Case | Target Latency | Acceptable Latency |
|----------|----------------|-------------------|
| Live comments | <100ms | <500ms |
| Ad click tracking | <50ms | <200ms |
| Real-time dashboard | <500ms | <2s |
| Push notifications | <1s | <5s |
| Payment processing | <100ms | <500ms |

---

# 3. Dealing with High Contention

## 3.1 Understanding Contention

**Contention** occurs when multiple processes/threads compete for the same resource simultaneously.

```
1000 Users → Last Concert Ticket
         ↓
Without proper handling:
  • Race conditions
  • Double-bookings  
  • Inconsistent state
  • Lost updates
```

### Real-World Contention Scenarios

| Scenario | Resource | Contention Level |
|----------|----------|------------------|
| Flash sale | Inventory counter | Extreme |
| Concert tickets | Seat availability | High |
| Bank transfer | Account balance | Medium |
| Shopping cart | Cart items | Low |
| Document editing | Document content | Variable |

## 3.2 Strategy 1: Pessimistic Locking

**Philosophy**: "Lock it before touching it. Everyone else waits."

```sql
-- Acquire exclusive lock BEFORE reading
BEGIN;

SELECT * FROM tickets 
WHERE id = 123 
FOR UPDATE;  -- X-lock acquired, others BLOCK here

-- Check if available
-- If yes, update
UPDATE tickets 
SET status = 'sold', buyer_id = 456 
WHERE id = 123;

COMMIT;  -- Lock released
```

### How It Works

```
Timeline:
═══════════════════════════════════════════════════════════▶

T1: BEGIN ─── SELECT FOR UPDATE ─── UPDATE ─── COMMIT
                    │                            │
                    │◄─────── Lock held ────────►│
                    │                            │
T2:         BEGIN ──┼── SELECT FOR UPDATE ───────┼─── continues...
                    │        (BLOCKED)           │
                    │◄─────── Waiting ──────────►│
```

### Complete Example

```python
import psycopg2
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = psycopg2.connect("postgresql://localhost/tickets")
    try:
        yield conn
    finally:
        conn.close()

def book_ticket_pessimistic(ticket_id: int, user_id: int) -> bool:
    """Book ticket using pessimistic locking"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Acquire lock and read in one statement
            cursor.execute("""
                SELECT id, status, price 
                FROM tickets 
                WHERE id = %s 
                FOR UPDATE  -- Exclusive lock
            """, (ticket_id,))
            
            ticket = cursor.fetchone()
            
            if not ticket:
                conn.rollback()
                return False, "Ticket not found"
            
            ticket_id, status, price = ticket
            
            if status != 'available':
                conn.rollback()
                return False, "Ticket already sold"
            
            # Update ticket
            cursor.execute("""
                UPDATE tickets 
                SET status = 'sold', buyer_id = %s, sold_at = NOW()
                WHERE id = %s
            """, (user_id, ticket_id))
            
            # Create booking record
            cursor.execute("""
                INSERT INTO bookings (ticket_id, user_id, amount)
                VALUES (%s, %s, %s)
            """, (ticket_id, user_id, price))
            
            conn.commit()
            return True, "Booking successful"
            
        except Exception as e:
            conn.rollback()
            return False, str(e)
```

### Pros and Cons

| Pros | Cons |
|------|------|
| Simple to understand | Blocks other transactions |
| Prevents all conflicts | Can cause deadlocks |
| Strong consistency | Poor scalability |
| No retry logic needed | High latency under contention |

### When to Use

- Low contention scenarios
- Critical operations (bank transfers)
- When conflicts are likely (>30% of transactions)
- Single database, no distribution needed

## 3.3 Strategy 2: Optimistic Locking

**Philosophy**: "Assume no conflict, verify on write. Retry if wrong."

```sql
-- Read with version
SELECT id, status, version FROM tickets WHERE id = 123;
-- Returns: id=123, status='available', version=5

-- Update only if version unchanged
UPDATE tickets 
SET status = 'sold', buyer_id = 456, version = version + 1
WHERE id = 123 AND version = 5;  -- Version check!

-- If rows_affected = 0, someone else updated → RETRY
```

### How It Works

```
Timeline:
═══════════════════════════════════════════════════════════▶

T1: Read (v=5) ─────────────────── Write (v=5→6) ✓
                                        │
T2:    Read (v=5) ────── Write (v=5→6) ─┼─ FAIL! (v is now 6)
                               │        │
                               │        └─► Retry: Read (v=6) → Write (v=6→7) ✓
                               │
                         Version mismatch!
```

### Complete Example

```python
import psycopg2
import time
from typing import Tuple

def book_ticket_optimistic(
    ticket_id: int, 
    user_id: int, 
    max_retries: int = 3,
    backoff_ms: int = 100
) -> Tuple[bool, str]:
    """Book ticket using optimistic locking with retries"""
    
    for attempt in range(max_retries):
        with get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Read current state (no lock)
                cursor.execute("""
                    SELECT id, status, price, version 
                    FROM tickets 
                    WHERE id = %s
                """, (ticket_id,))
                
                ticket = cursor.fetchone()
                
                if not ticket:
                    return False, "Ticket not found"
                
                ticket_id, status, price, version = ticket
                
                if status != 'available':
                    return False, "Ticket already sold"
                
                # Optimistic update with version check
                cursor.execute("""
                    UPDATE tickets 
                    SET status = 'sold', 
                        buyer_id = %s, 
                        sold_at = NOW(),
                        version = version + 1
                    WHERE id = %s AND version = %s
                """, (user_id, ticket_id, version))
                
                if cursor.rowcount == 0:
                    # Version mismatch - someone else updated
                    conn.rollback()
                    
                    # Exponential backoff before retry
                    if attempt < max_retries - 1:
                        sleep_time = backoff_ms * (2 ** attempt) / 1000
                        time.sleep(sleep_time)
                        continue
                    else:
                        return False, "Conflict after max retries"
                
                # Success - create booking
                cursor.execute("""
                    INSERT INTO bookings (ticket_id, user_id, amount)
                    VALUES (%s, %s, %s)
                """, (ticket_id, user_id, price))
                
                conn.commit()
                return True, "Booking successful"
                
            except Exception as e:
                conn.rollback()
                return False, str(e)
    
    return False, "Max retries exceeded"
```

### Pros and Cons

| Pros | Cons |
|------|------|
| No blocking | Retry storms under high contention |
| Higher throughput | Wasted work on conflicts |
| Works with read replicas | Application complexity (retry logic) |
| Good for read-heavy workloads | Poor when conflicts are frequent |

### When to Use

- Low to medium contention (<30% conflict rate)
- Read-heavy workloads
- Distributed systems
- When latency matters more than strict ordering

## 3.4 Strategy 3: Queue-Based Serialization

**Philosophy**: "Funnel everything through a queue, process one at a time."

```
1000 concurrent requests
         │
         ▼
    ┌─────────┐
    │  Kafka  │  ← Partition by ticket_id
    │  Queue  │  ← All requests for same ticket → same partition
    └────┬────┘
         │
         ▼ (sequential processing)
    ┌─────────┐
    │Consumer │  ← Processes one at a time
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │Database │  ← No contention!
    └─────────┘
```

### Complete Example

```python
# Producer (API Server)
from kafka import KafkaProducer
import json
import uuid

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8')
)

def request_booking(ticket_id: int, user_id: int) -> str:
    """Submit booking request to queue"""
    request_id = str(uuid.uuid4())
    
    booking_request = {
        "request_id": request_id,
        "ticket_id": ticket_id,
        "user_id": user_id,
        "timestamp": time.time()
    }
    
    # Key = ticket_id ensures all requests for same ticket
    # go to same partition (processed in order)
    producer.send(
        topic='booking-requests',
        key=str(ticket_id),  # Partition key
        value=booking_request
    )
    producer.flush()
    
    return request_id  # Client polls for result
```

```python
# Consumer (Booking Processor)
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'booking-requests',
    bootstrap_servers=['localhost:9092'],
    group_id='booking-processor',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=False  # Manual commit for exactly-once
)

def process_bookings():
    """Process booking requests sequentially per partition"""
    for message in consumer:
        request = message.value
        
        try:
            # Process booking (no contention - sequential per ticket)
            result = execute_booking(
                request['ticket_id'],
                request['user_id']
            )
            
            # Store result for client polling
            redis_client.setex(
                f"booking_result:{request['request_id']}",
                3600,  # 1 hour TTL
                json.dumps(result)
            )
            
            # Commit offset after successful processing
            consumer.commit()
            
        except Exception as e:
            # Handle error, maybe send to DLQ
            handle_error(request, e)

def execute_booking(ticket_id: int, user_id: int) -> dict:
    """Actual booking logic - no contention handling needed"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT status FROM tickets WHERE id = %s",
            (ticket_id,)
        )
        
        status = cursor.fetchone()[0]
        
        if status != 'available':
            return {"success": False, "error": "Ticket already sold"}
        
        cursor.execute("""
            UPDATE tickets SET status = 'sold', buyer_id = %s
            WHERE id = %s
        """, (user_id, ticket_id))
        
        conn.commit()
        return {"success": True, "message": "Booking confirmed"}
```

### Pros and Cons

| Pros | Cons |
|------|------|
| Eliminates DB contention | Added latency (async) |
| Predictable processing | More infrastructure |
| Scales per resource | Need async response pattern |
| Natural rate limiting | Complexity in error handling |

### When to Use

- Very high contention (flash sales)
- When you can tolerate async response
- Need to process in strict order
- Want to decouple request from processing

## 3.5 Strategy 4: Distributed Locks

**Philosophy**: "Acquire a distributed lock before critical section."

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTED LOCK FLOW                         │
└─────────────────────────────────────────────────────────────────┘

Service A                 Redis                    Service B
    │                       │                          │
    │── SETNX lock:123 ────▶│                          │
    │◀─────── OK ───────────│                          │
    │                       │◀── SETNX lock:123 ───────│
    │                       │─────── FAIL ────────────▶│
    │                       │                          │
    │   [Critical Section]  │                     [Waiting/Retry]
    │                       │                          │
    │── DEL lock:123 ──────▶│                          │
    │◀─────── OK ───────────│                          │
    │                       │◀── SETNX lock:123 ───────│
    │                       │─────── OK ──────────────▶│
```

### Redis Lock Implementation

```python
import redis
import uuid
import time
from contextlib import contextmanager

class RedisLock:
    def __init__(self, redis_client, lock_name: str, ttl_seconds: int = 30):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.ttl = ttl_seconds
        self.owner_id = str(uuid.uuid4())
    
    def acquire(self, timeout_seconds: int = 10) -> bool:
        """Try to acquire lock with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            # SETNX with TTL (atomic)
            acquired = self.redis.set(
                self.lock_name,
                self.owner_id,
                nx=True,  # Only set if not exists
                ex=self.ttl  # Expire after TTL (prevent deadlock)
            )
            
            if acquired:
                return True
            
            # Wait before retry
            time.sleep(0.1)
        
        return False
    
    def release(self) -> bool:
        """Release lock only if we own it (atomic with Lua)"""
        # Lua script ensures atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, self.lock_name, self.owner_id)
        return result == 1
    
    def extend(self, additional_seconds: int) -> bool:
        """Extend lock TTL if we still own it"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        
        result = self.redis.eval(
            lua_script, 1, 
            self.lock_name, self.owner_id, additional_seconds
        )
        return result == 1


@contextmanager
def distributed_lock(redis_client, resource_name: str, ttl: int = 30):
    """Context manager for distributed locking"""
    lock = RedisLock(redis_client, resource_name, ttl)
    
    if not lock.acquire():
        raise Exception(f"Could not acquire lock for {resource_name}")
    
    try:
        yield lock
    finally:
        lock.release()


# Usage
redis_client = redis.Redis(host='localhost', port=6379)

def book_ticket_distributed(ticket_id: int, user_id: int) -> Tuple[bool, str]:
    """Book ticket using distributed lock"""
    try:
        with distributed_lock(redis_client, f"ticket:{ticket_id}"):
            # Critical section - only one process here
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT status FROM tickets WHERE id = %s",
                    (ticket_id,)
                )
                status = cursor.fetchone()[0]
                
                if status != 'available':
                    return False, "Ticket already sold"
                
                cursor.execute("""
                    UPDATE tickets 
                    SET status = 'sold', buyer_id = %s
                    WHERE id = %s
                """, (user_id, ticket_id))
                
                conn.commit()
                return True, "Booking successful"
                
    except Exception as e:
        return False, str(e)
```

### Redlock Algorithm (Multi-Node)

For higher reliability, acquire lock on majority of Redis nodes:

```python
class Redlock:
    def __init__(self, redis_nodes: list, lock_name: str, ttl_ms: int = 30000):
        self.nodes = redis_nodes  # List of Redis connections
        self.lock_name = f"lock:{lock_name}"
        self.ttl_ms = ttl_ms
        self.owner_id = str(uuid.uuid4())
        self.quorum = len(redis_nodes) // 2 + 1
    
    def acquire(self) -> bool:
        """Acquire lock on majority of nodes"""
        start_time = time.time() * 1000  # ms
        
        locks_acquired = 0
        
        for node in self.nodes:
            try:
                acquired = node.set(
                    self.lock_name,
                    self.owner_id,
                    nx=True,
                    px=self.ttl_ms
                )
                if acquired:
                    locks_acquired += 1
            except Exception:
                pass  # Node unreachable
        
        # Check if we got quorum within drift time
        elapsed = time.time() * 1000 - start_time
        validity_time = self.ttl_ms - elapsed - (self.ttl_ms * 0.01)  # Clock drift
        
        if locks_acquired >= self.quorum and validity_time > 0:
            return True
        else:
            # Failed to get quorum - release all acquired locks
            self._release_all()
            return False
    
    def _release_all(self):
        """Release lock from all nodes"""
        for node in self.nodes:
            try:
                self._release_node(node)
            except Exception:
                pass
```

## 3.6 Strategy 5: Atomic Operations

**Philosophy**: "Use database's atomic operations, no explicit locks needed."

```sql
-- Atomic decrement with check (single statement = atomic)
UPDATE inventory 
SET quantity = quantity - 1 
WHERE product_id = 123 AND quantity > 0;

-- rows_affected: 0 = out of stock, 1 = success
```

### Redis Atomic Operations

```python
import redis

r = redis.Redis()

def claim_ticket_atomic(ticket_id: int, user_id: int) -> bool:
    """Claim ticket using atomic Redis operations"""
    
    # Atomic decrement
    remaining = r.decr(f'ticket:{ticket_id}:count')
    
    if remaining >= 0:
        # Successfully claimed!
        # Queue the actual DB update
        r.lpush('booking_queue', json.dumps({
            'ticket_id': ticket_id,
            'user_id': user_id
        }))
        return True
    else:
        # Over-claimed, restore counter
        r.incr(f'ticket:{ticket_id}:count')
        return False
```

### Lua Script for Complex Atomics

```python
def book_with_lua(ticket_id: int, user_id: int) -> bool:
    """Complex atomic operation with Lua script"""
    
    lua_script = """
    local ticket_key = KEYS[1]
    local bookings_key = KEYS[2]
    local user_id = ARGV[1]
    local timestamp = ARGV[2]
    
    -- Check if available
    local status = redis.call('HGET', ticket_key, 'status')
    if status ~= 'available' then
        return {0, 'Ticket not available'}
    end
    
    -- Book the ticket atomically
    redis.call('HSET', ticket_key, 'status', 'sold')
    redis.call('HSET', ticket_key, 'buyer_id', user_id)
    redis.call('HSET', ticket_key, 'sold_at', timestamp)
    
    -- Add to bookings list
    redis.call('ZADD', bookings_key, timestamp, user_id)
    
    return {1, 'Success'}
    """
    
    result = r.eval(
        lua_script, 
        2,  # Number of keys
        f'ticket:{ticket_id}',
        f'ticket:{ticket_id}:bookings',
        user_id,
        time.time()
    )
    
    return result[0] == 1
```

## 3.7 Strategy 6: Sharding Hot Resources

**Philosophy**: "Split the hot resource into multiple shards to distribute load."

```
Instead of:
  tickets_remaining = 1000 (single counter - HOT!)
  
Use sharded counters:
  shard_0: 100 tickets
  shard_1: 100 tickets
  ...
  shard_9: 100 tickets
  
10x less contention per shard!
```

### Implementation

```python
import random
import redis

class ShardedCounter:
    def __init__(self, redis_client, key: str, num_shards: int = 10):
        self.redis = redis_client
        self.key = key
        self.num_shards = num_shards
    
    def initialize(self, total_count: int):
        """Initialize sharded counter"""
        per_shard = total_count // self.num_shards
        remainder = total_count % self.num_shards
        
        pipe = self.redis.pipeline()
        for i in range(self.num_shards):
            count = per_shard + (1 if i < remainder else 0)
            pipe.set(f"{self.key}:shard:{i}", count)
        pipe.execute()
    
    def decrement(self) -> bool:
        """Try to decrement from a random shard"""
        # Try random shard first (load distribution)
        start_shard = random.randint(0, self.num_shards - 1)
        
        for i in range(self.num_shards):
            shard_idx = (start_shard + i) % self.num_shards
            shard_key = f"{self.key}:shard:{shard_idx}"
            
            # Atomic decrement only if > 0
            lua_script = """
            local current = tonumber(redis.call('GET', KEYS[1]) or 0)
            if current > 0 then
                redis.call('DECR', KEYS[1])
                return 1
            end
            return 0
            """
            
            result = self.redis.eval(lua_script, 1, shard_key)
            
            if result == 1:
                return True
        
        return False  # All shards exhausted
    
    def get_total(self) -> int:
        """Get total count across all shards"""
        pipe = self.redis.pipeline()
        for i in range(self.num_shards):
            pipe.get(f"{self.key}:shard:{i}")
        
        values = pipe.execute()
        return sum(int(v or 0) for v in values)


# Usage
counter = ShardedCounter(redis_client, "concert:taylor_swift:tickets", num_shards=100)
counter.initialize(10000)  # 10,000 tickets across 100 shards

# Each request
if counter.decrement():
    print("Got a ticket!")
else:
    print("Sold out!")
```

## 3.8 Complete Flash Sale Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLASH SALE SYSTEM                              │
└─────────────────────────────────────────────────────────────────┘

       100,000 Concurrent Users
              │
              ▼
┌─────────────────────────┐
│    Layer 1: CDN/Edge    │  Cache static content
│    (CloudFlare/Fastly)  │  Edge rate limiting
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 2: Load Balancer │  Distribute load
│     (Nginx/HAProxy)     │  Health checks
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 3: Rate Limiter  │  Redis token bucket
│      (Per user/IP)      │  10 requests/sec/user
│                         │  
│  if rate_limit_exceeded:│
│     return 429          │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 4: Stock Check   │  Redis sharded counter
│     (Fast rejection)    │  
│                         │
│  if stock <= 0:         │
│     return "Sold Out"   │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 5: Queue         │  Kafka partitioned by item_id
│     (Serialize)         │  Decouple request from processing
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 6: Consumer      │  Sequential processing
│     (Process order)     │  Exactly-once semantics
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Layer 7: Database      │  PostgreSQL with optimistic lock
│     (Source of truth)   │  Final consistency check
└─────────────────────────┘
```

---

# 4. Types of Locking Mechanisms

## 4.1 Classification Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCKING MECHANISMS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  By Strategy          By Scope           By Implementation       │
│  ────────────         ─────────          ─────────────────       │
│  • Pessimistic        • Row Lock         • Mutex                 │
│  • Optimistic         • Page Lock        • Semaphore             │
│  • Hybrid             • Table Lock       • RWLock                │
│                       • Database Lock    • Spin Lock             │
│                       • Advisory Lock    • Distributed Lock      │
│                                                                  │
│  By Mode              By Duration        By Granularity          │
│  ─────────            ───────────        ─────────────           │
│  • Shared (S)         • Short-term       • Fine-grained          │
│  • Exclusive (X)      • Long-term        • Coarse-grained        │
│  • Update (U)         • Session-level                            │
│  • Intent (IS/IX)                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4.2 Mutex (Mutual Exclusion)

**Definition**: Binary lock allowing only one thread at a time.

```python
import threading

# Create mutex
mutex = threading.Lock()

counter = 0

def increment():
    global counter
    
    # Acquire lock (blocking)
    mutex.acquire()
    try:
        # Critical section - only one thread here
        temp = counter
        temp += 1
        counter = temp
    finally:
        # Always release!
        mutex.release()

# Or use context manager
def increment_safe():
    global counter
    
    with mutex:  # Auto acquire/release
        counter += 1
```

### Reentrant Mutex (RLock)

Same thread can acquire multiple times:

```python
import threading

rlock = threading.RLock()

def outer():
    with rlock:
        print("Outer acquired")
        inner()  # Same thread can reacquire

def inner():
    with rlock:  # Would deadlock with regular Lock!
        print("Inner acquired")
```

## 4.3 Semaphore

**Definition**: Allows N concurrent accesses (generalized mutex).

```python
import threading

# Allow 5 concurrent database connections
connection_pool = threading.Semaphore(5)

def query_database(sql):
    with connection_pool:  # Blocks if 5 already acquired
        # At most 5 threads here simultaneously
        connection = get_connection()
        try:
            return connection.execute(sql)
        finally:
            release_connection(connection)

# Bounded semaphore (can't release more than acquired)
bounded = threading.BoundedSemaphore(5)
```

### Use Cases

| Semaphore Value | Use Case |
|-----------------|----------|
| 1 (binary) | Same as mutex |
| N (counting) | Connection pools, rate limiting |
| 0 (initial) | Signaling between threads |

## 4.4 Read-Write Lock (RWLock)

**Definition**: Multiple readers OR single writer, not both.

```python
import threading

class RWLock:
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0
        self._writers_waiting = 0
        self._writer_active = False
    
    def acquire_read(self):
        with self._read_ready:
            while self._writer_active or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1
    
    def release_read(self):
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()
    
    def acquire_write(self):
        with self._read_ready:
            self._writers_waiting += 1
            while self._readers > 0 or self._writer_active:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writer_active = True
    
    def release_write(self):
        with self._read_ready:
            self._writer_active = False
            self._read_ready.notify_all()


# Usage
cache_lock = RWLock()
cache = {}

def read_cache(key):
    cache_lock.acquire_read()
    try:
        return cache.get(key)
    finally:
        cache_lock.release_read()

def write_cache(key, value):
    cache_lock.acquire_write()
    try:
        cache[key] = value
    finally:
        cache_lock.release_write()
```

### Behavior Matrix

```
Current State         │ Read Request    │ Write Request
──────────────────────┼─────────────────┼───────────────
No locks held         │ ✓ Granted       │ ✓ Granted
Read lock(s) held     │ ✓ Granted       │ ✗ Wait
Write lock held       │ ✗ Wait          │ ✗ Wait
```

## 4.5 Spin Lock

**Definition**: Busy-wait instead of blocking (for very short critical sections).

```c
// C implementation
typedef struct {
    volatile int locked;
} spinlock_t;

void spin_lock(spinlock_t *lock) {
    while (__sync_lock_test_and_set(&lock->locked, 1)) {
        // Spin (busy wait)
        while (lock->locked) {
            // CPU hint: we're spinning
            __builtin_ia32_pause();
        }
    }
}

void spin_unlock(spinlock_t *lock) {
    __sync_lock_release(&lock->locked);
}
```

```python
# Python simulation (not recommended for production)
import threading
import time

class SpinLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._locked = False
    
    def acquire(self):
        while True:
            if self._lock.acquire(blocking=False):
                if not self._locked:
                    self._locked = True
                    self._lock.release()
                    return
                self._lock.release()
            # Spin (bad for Python due to GIL)
            time.sleep(0)  # Yield to other threads
    
    def release(self):
        with self._lock:
            self._locked = False
```

### When to Use Spin Locks

| Use Spin Lock | Use Blocking Lock |
|---------------|-------------------|
| Critical section < 1μs | Critical section > 1μs |
| Low contention | High contention |
| Kernel/driver code | Application code |
| Multi-core guaranteed | Single core possible |

## 4.6 Database Locks

### Row-Level Locks

```sql
-- PostgreSQL
SELECT * FROM orders WHERE id = 1 FOR UPDATE;        -- X-lock
SELECT * FROM orders WHERE id = 1 FOR SHARE;         -- S-lock
SELECT * FROM orders WHERE id = 1 FOR NO KEY UPDATE; -- Weaker X (allows FK)
SELECT * FROM orders WHERE id = 1 FOR KEY SHARE;     -- Weakest (FK only)

-- MySQL
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
SELECT * FROM orders WHERE id = 1 LOCK IN SHARE MODE; -- Old syntax
SELECT * FROM orders WHERE id = 1 FOR SHARE;          -- MySQL 8.0+
```

### Table-Level Locks

```sql
-- PostgreSQL table locks (from weakest to strongest)
LOCK TABLE orders IN ACCESS SHARE MODE;         -- SELECT
LOCK TABLE orders IN ROW SHARE MODE;            -- SELECT FOR UPDATE
LOCK TABLE orders IN ROW EXCLUSIVE MODE;        -- UPDATE, DELETE
LOCK TABLE orders IN SHARE UPDATE EXCLUSIVE MODE; -- VACUUM
LOCK TABLE orders IN SHARE MODE;                -- CREATE INDEX
LOCK TABLE orders IN SHARE ROW EXCLUSIVE MODE;  -- Exclusive reads
LOCK TABLE orders IN EXCLUSIVE MODE;            -- Blocks all except SELECT
LOCK TABLE orders IN ACCESS EXCLUSIVE MODE;     -- Blocks everything

-- MySQL
LOCK TABLES orders WRITE;  -- Exclusive
LOCK TABLES orders READ;   -- Shared
UNLOCK TABLES;
```

### Advisory Locks (Application-Defined)

```sql
-- PostgreSQL advisory locks
-- Session-level (held until released or session ends)
SELECT pg_advisory_lock(12345);         -- Blocking
SELECT pg_try_advisory_lock(12345);     -- Non-blocking, returns bool
SELECT pg_advisory_unlock(12345);       -- Release

-- Transaction-level (auto-released on commit/rollback)
SELECT pg_advisory_xact_lock(12345);

-- Two-argument form (more specific)
SELECT pg_advisory_lock(classid, objid);  -- e.g., (1, 123) for order #123
```

```python
def process_order_with_advisory_lock(order_id: int):
    """Use advisory lock for application-level locking"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Try to acquire advisory lock (non-blocking)
        cursor.execute(
            "SELECT pg_try_advisory_lock(%s)",
            (order_id,)
        )
        acquired = cursor.fetchone()[0]
        
        if not acquired:
            return "Order being processed by another worker"
        
        try:
            # Process order (we have exclusive access)
            process_order(order_id)
            conn.commit()
            return "Order processed"
        finally:
            # Release advisory lock
            cursor.execute(
                "SELECT pg_advisory_unlock(%s)",
                (order_id,)
            )
```

### Gap Locks (MySQL/InnoDB)

Prevents phantom reads by locking "gaps" between index values:

```sql
-- Existing rows: id = 10, 20, 30

SELECT * FROM t WHERE id BETWEEN 15 AND 25 FOR UPDATE;

-- Locks acquired:
-- 1. Row lock on id=20
-- 2. Gap lock on (10, 20) - prevents INSERT of id=15
-- 3. Gap lock on (20, 30) - prevents INSERT of id=25
```

```
Index:     10 ─────── 20 ─────── 30
             │        │         │
Gap locks:   └─(gap)──┴──(gap)──┘
```

## 4.7 Distributed Locks Comparison

| Lock Type | Consistency | Availability | Best For |
|-----------|-------------|--------------|----------|
| **Redis SETNX** | Weak | High | Simple cases |
| **Redlock** | Medium | Medium | Multi-node Redis |
| **ZooKeeper** | Strong | Medium | Leader election |
| **etcd** | Strong | Medium | Kubernetes environments |
| **Consul** | Strong | Medium | Service mesh |

### ZooKeeper Lock Implementation

```java
// ZooKeeper distributed lock using ephemeral sequential nodes
public class ZooKeeperLock {
    private ZooKeeper zk;
    private String lockPath;
    private String myNode;
    
    public void lock() throws Exception {
        // Create ephemeral sequential node
        myNode = zk.create(
            lockPath + "/lock-",
            new byte[0],
            ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.EPHEMERAL_SEQUENTIAL
        );
        
        while (true) {
            // Get all children
            List<String> children = zk.getChildren(lockPath, false);
            Collections.sort(children);
            
            // Check if we're the smallest (first in line)
            String smallest = lockPath + "/" + children.get(0);
            if (myNode.equals(smallest)) {
                // We have the lock!
                return;
            }
            
            // Find the node just before us
            int myIndex = children.indexOf(myNode.substring(lockPath.length() + 1));
            String predecessor = lockPath + "/" + children.get(myIndex - 1);
            
            // Watch the predecessor
            final CountDownLatch latch = new CountDownLatch(1);
            Stat stat = zk.exists(predecessor, event -> latch.countDown());
            
            if (stat != null) {
                // Wait for predecessor to be deleted
                latch.await();
            }
            // Loop and check again
        }
    }
    
    public void unlock() throws Exception {
        zk.delete(myNode, -1);
    }
}
```

---

# 5. S-Lock vs X-Lock Deep Dive

## 5.1 Definitions

| Lock Type | Full Name | Purpose | Concurrent Holders |
|-----------|-----------|---------|-------------------|
| **S-Lock** | Shared Lock / Read Lock | Protect data during reads | Multiple allowed |
| **X-Lock** | Exclusive Lock / Write Lock | Protect data during writes | Only one |

## 5.2 Compatibility Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCK COMPATIBILITY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│              │    S-Lock Held    │    X-Lock Held    │          │
│   Request    │                   │                   │          │
│   ──────────────────────────────────────────────────            │
│   S-Lock     │     ✓ GRANT       │     ✗ WAIT        │          │
│   X-Lock     │     ✗ WAIT        │     ✗ WAIT        │          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Key:
  S + S = ✓ (Multiple readers allowed)
  S + X = ✗ (Can't write while reading)
  X + S = ✗ (Can't read while writing)
  X + X = ✗ (Can't have two writers)
```

## 5.3 Visual Timeline

```
Resource: Account Balance
═════════════════════════════════════════════════════════════════▶ Time

T1: ────[S-lock]────────────────────────[release]
             │
T2:     ────[S-lock]────────[release]        (OK: S+S compatible)
             │         │
T3:          └─────────┴── [X-lock] ──────   (BLOCKED until T1,T2 release)
                             │
T4:                          └── [S-lock] ── (BLOCKED until T3 releases)
```

## 5.4 SQL Syntax

### PostgreSQL

```sql
-- S-Lock (Shared/Read)
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- X-Lock (Exclusive/Write)
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- Variants
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;  -- Weaker X
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;      -- Weaker S

-- Behavior options
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;      -- Error if locked
SELECT * FROM accounts WHERE id = 1 FOR UPDATE SKIP LOCKED; -- Skip locked rows
```

### MySQL/InnoDB

```sql
-- S-Lock
SELECT * FROM accounts WHERE id = 1 FOR SHARE;           -- MySQL 8.0+
SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE;  -- Older versions

-- X-Lock
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- NOWAIT and SKIP LOCKED (MySQL 8.0+)
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE SKIP LOCKED;
```

## 5.5 Implicit vs Explicit Locks

| Operation | Lock Type | Implicit/Explicit |
|-----------|-----------|-------------------|
| `SELECT` | None (MVCC) | N/A |
| `SELECT ... FOR SHARE` | S-Lock | Explicit |
| `SELECT ... FOR UPDATE` | X-Lock | Explicit |
| `UPDATE` | X-Lock | Implicit |
| `DELETE` | X-Lock | Implicit |
| `INSERT` | X-Lock (on new row) | Implicit |

## 5.6 Lock Upgrade Problem

```sql
-- DANGEROUS: Lock upgrade can cause deadlock!

-- T1                              -- T2
BEGIN;                             BEGIN;
SELECT * FROM t                    SELECT * FROM t 
  WHERE id=1 FOR SHARE; -- S       WHERE id=1 FOR SHARE; -- S
                                   
UPDATE t SET x=1                   UPDATE t SET x=2
  WHERE id=1;                        WHERE id=1;
-- Wants X, blocked by T2's S      -- Wants X, blocked by T1's S
                                   
-- DEADLOCK! Neither can proceed
```

**Solution**: Use `FOR UPDATE` from the start if you plan to write.

```sql
-- SAFE: Get X-lock immediately if planning to write
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- X-lock
-- Now safe to update
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

## 5.7 Lock Duration by Isolation Level

```
Isolation Level      │ S-Lock Duration        │ X-Lock Duration
─────────────────────┼────────────────────────┼─────────────────────
READ UNCOMMITTED     │ None                   │ Until write completes
READ COMMITTED       │ Released after read    │ Until commit
REPEATABLE READ      │ Until commit           │ Until commit
SERIALIZABLE         │ Until commit           │ Until commit
```

---

# 6. Database Isolation Levels

## 6.1 The Anomalies (Problems)

### Dirty Read
Reading uncommitted data from another transaction.

```
T1: UPDATE account SET balance = 0 WHERE id = 1;
                                    T2: SELECT balance FROM account WHERE id = 1;
                                        → Returns 0 (uncommitted!)
T1: ROLLBACK;
                                    T2: (Used invalid data!)
```

### Non-Repeatable Read
Same query returns different results within a transaction.

```
T1: SELECT balance FROM account WHERE id = 1;  → 100
                                    T2: UPDATE account SET balance = 50 WHERE id = 1;
                                    T2: COMMIT;
T1: SELECT balance FROM account WHERE id = 1;  → 50 (different!)
```

### Phantom Read
New rows appear in repeated queries.

```
T1: SELECT COUNT(*) FROM orders WHERE status = 'pending';  → 5
                                    T2: INSERT INTO orders (status) VALUES ('pending');
                                    T2: COMMIT;
T1: SELECT COUNT(*) FROM orders WHERE status = 'pending';  → 6 (phantom!)
```

### Lost Update
Concurrent updates overwrite each other.

```
T1: SELECT balance FROM account WHERE id = 1;  → 100
T2: SELECT balance FROM account WHERE id = 1;  → 100
T1: UPDATE account SET balance = 100 + 10 WHERE id = 1;  -- 110
T2: UPDATE account SET balance = 100 + 20 WHERE id = 1;  -- 120
-- Final: 120 (T1's update lost!)
-- Expected: 130
```

### Write Skew
Constraint violated across multiple rows.

```
-- Constraint: At least one doctor must be on-call

T1: SELECT COUNT(*) FROM doctors WHERE on_call = true;  → 2 (Alice, Bob)
T2: SELECT COUNT(*) FROM doctors WHERE on_call = true;  → 2 (Alice, Bob)
T1: UPDATE doctors SET on_call = false WHERE name = 'Alice';  -- OK, Bob still on
T2: UPDATE doctors SET on_call = false WHERE name = 'Bob';    -- OK, Alice still on
-- Both commit: No one on call! Constraint violated.
```

## 6.2 The Four Standard Isolation Levels

### Level 1: READ UNCOMMITTED

**Behavior**: Can see uncommitted changes (dirty reads allowed).

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

BEGIN;
SELECT * FROM accounts;  -- Can see uncommitted changes from other transactions
COMMIT;
```

| Prevents | Allows |
|----------|--------|
| Nothing | Dirty reads, Non-repeatable reads, Phantoms |

**Use case**: Almost never. Only for rough statistics where accuracy doesn't matter.

### Level 2: READ COMMITTED (Default in PostgreSQL, Oracle)

**Behavior**: Only sees committed changes, but can see new commits mid-transaction.

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 100
-- Another transaction commits: balance = 50
SELECT balance FROM accounts WHERE id = 1;  -- 50 (sees new committed value)
COMMIT;
```

| Prevents | Allows |
|----------|--------|
| Dirty reads | Non-repeatable reads, Phantoms |

**Use case**: Most OLTP applications. Default choice for web applications.

### Level 3: REPEATABLE READ (Default in MySQL)

**Behavior**: Sees snapshot from transaction start. Same query = same results.

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 100
-- Another transaction commits: balance = 50
SELECT balance FROM accounts WHERE id = 1;  -- 100 (still sees original!)
COMMIT;
```

| Prevents | Allows |
|----------|--------|
| Dirty reads, Non-repeatable reads | Phantoms (SQL standard), Write skew |

**Note**: MySQL's REPEATABLE READ also prevents phantoms via gap locks.

**Use case**: Financial reports, any operation needing consistent view of data.

### Level 4: SERIALIZABLE

**Behavior**: Transactions execute as if run serially (one after another).

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN;
SELECT * FROM orders WHERE status = 'pending';  -- Locks the predicate
-- Another transaction trying to INSERT a 'pending' order will BLOCK
COMMIT;
```

| Prevents | Allows |
|----------|--------|
| All anomalies | Nothing |

**Use case**: Critical financial operations, strict inventory management.

## 6.3 Summary Matrix

| Isolation Level | Dirty Read | Non-Repeatable | Phantom | Lost Update | Write Skew |
|-----------------|------------|----------------|---------|-------------|------------|
| READ UNCOMMITTED | Possible | Possible | Possible | Possible | Possible |
| READ COMMITTED | Prevented | Possible | Possible | Possible | Possible |
| REPEATABLE READ | Prevented | Prevented | Possible* | Prevented | Possible |
| SERIALIZABLE | Prevented | Prevented | Prevented | Prevented | Prevented |

*MySQL prevents phantoms at REPEATABLE READ; PostgreSQL doesn't.

## 6.4 Database-Specific Behavior

### PostgreSQL (MVCC)

```sql
-- Set for session
SET default_transaction_isolation = 'repeatable read';

-- Set for single transaction
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- work...
COMMIT;

-- Check current level
SHOW transaction_isolation;
```

**PostgreSQL Serializable (SSI)**:
- Uses Serializable Snapshot Isolation
- Detects conflicts at commit time
- No predicate locks (optimistic)
- Aborts one transaction on conflict

```sql
-- PostgreSQL SERIALIZABLE example
-- T1
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM doctors WHERE on_call = true;  -- Alice, Bob
UPDATE doctors SET on_call = false WHERE name = 'Alice';
COMMIT;  -- Success

-- T2 (concurrent)
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT * FROM doctors WHERE on_call = true;  -- Alice, Bob (snapshot)
UPDATE doctors SET on_call = false WHERE name = 'Bob';
COMMIT;  -- ERROR: could not serialize access
```

### MySQL/InnoDB (Locking)

```sql
-- Set for session
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Set for next transaction only
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
-- work...
COMMIT;

-- Check current level
SELECT @@transaction_isolation;
```

**MySQL locking behavior**:
- REPEATABLE READ uses gap locks (prevents phantoms)
- SERIALIZABLE adds shared locks on all reads

### SQL Server

```sql
-- Has additional SNAPSHOT isolation
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
```

**SNAPSHOT** isolation:
- MVCC-based (like PostgreSQL)
- Row versioning in tempdb
- Readers don't block writers

## 6.5 Choosing the Right Level

| Scenario | Recommended | Why |
|----------|-------------|-----|
| General web app | READ COMMITTED | Good balance |
| Reporting queries | REPEATABLE READ | Consistent snapshot |
| Financial transactions | SERIALIZABLE | No anomalies |
| High-throughput, can retry | READ COMMITTED + app logic | Performance |
| Audit-critical operations | SERIALIZABLE | Compliance |

## 6.6 Performance Impact

```
READ UNCOMMITTED   ████████████████████████████████  Fastest
READ COMMITTED     ████████████████████████████      Fast
REPEATABLE READ    ████████████████████████          Medium
SERIALIZABLE       ████████████████                  Slowest

More isolation = More locking/conflict detection = Lower throughput
```

---

# 7. How Locks Implement Isolation

## 7.1 Two Approaches

```
┌─────────────────────────────────────────────────────────────────┐
│                 ISOLATION IMPLEMENTATION                         │
├────────────────────────────┬────────────────────────────────────┤
│      TWO-PHASE LOCKING     │              MVCC                  │
│         (2PL)              │  (Multi-Version Concurrency)       │
├────────────────────────────┼────────────────────────────────────┤
│ • SQL Server               │ • PostgreSQL                       │
│ • MySQL (writes)           │ • Oracle                           │
│ • DB2                      │ • MySQL (reads)                    │
├────────────────────────────┼────────────────────────────────────┤
│ Readers BLOCK writers      │ Readers DON'T block writers        │
│ Writers BLOCK readers      │ Each sees own snapshot             │
│ Deadlocks common           │ Deadlocks rare                     │
│ No version storage         │ Stores multiple versions           │
└────────────────────────────┴────────────────────────────────────┘
```

## 7.2 Locking Implementation (2PL)

### Two-Phase Locking Protocol

```
Phase 1: GROWING (Acquiring locks)
  - Transaction acquires all locks needed
  - Cannot release any lock

Phase 2: SHRINKING (Releasing locks)
  - Transaction releases locks
  - Cannot acquire new locks

                    Lock Point
                        │
    Growing Phase       │     Shrinking Phase
    ─────────────────►  │  ◄─────────────────
                        │
    S S S X S X        COMMIT        release all
```

### READ UNCOMMITTED Implementation

```sql
-- No read locks, minimal write locks
T1: UPDATE accounts SET balance = 0 WHERE id = 1;
    -- Acquires X-lock, releases immediately after write (before commit)
    
T2: SELECT balance FROM accounts WHERE id = 1;
    -- No lock, reads current value (even if uncommitted)
```

### READ COMMITTED Implementation

```sql
-- Short-term S-locks, X-locks until commit
T1: BEGIN;
T1: SELECT balance FROM accounts WHERE id = 1;
    -- Acquire S-lock → Read → Release S-lock immediately
    -- Value: 100

                    T2: BEGIN;
                    T2: UPDATE accounts SET balance = 50 WHERE id = 1;
                        -- Acquire X-lock (no conflict, S already released)
                    T2: COMMIT;
                        -- Release X-lock

T1: SELECT balance FROM accounts WHERE id = 1;
    -- Acquire S-lock → Read → Release S-lock
    -- Value: 50 (sees committed change - non-repeatable read!)
T1: COMMIT;
```

### REPEATABLE READ Implementation

```sql
-- S-locks held until commit
T1: BEGIN;
T1: SELECT balance FROM accounts WHERE id = 1;
    -- Acquire S-lock → HOLD IT
    -- Value: 100

                    T2: BEGIN;
                    T2: UPDATE accounts SET balance = 50 WHERE id = 1;
                        -- Wants X-lock, BLOCKED (T1 holds S)
                        -- ... waiting ...

T1: SELECT balance FROM accounts WHERE id = 1;
    -- Value: 100 (still has lock, consistent read)
T1: COMMIT;
    -- Release S-lock

                    T2: -- Now acquires X-lock, proceeds
                    T2: UPDATE accounts SET balance = 50 WHERE id = 1;
                    T2: COMMIT;
```

### SERIALIZABLE Implementation

```sql
-- S-locks + Range/Predicate locks
T1: BEGIN;
T1: SELECT * FROM orders WHERE status = 'pending';
    -- Acquires S-locks on matching rows
    -- Acquires RANGE LOCK on "status = 'pending'" predicate
    -- Returns 5 orders

                    T2: BEGIN;
                    T2: INSERT INTO orders (status) VALUES ('pending');
                        -- Wants to insert into locked range
                        -- BLOCKED!

T1: SELECT * FROM orders WHERE status = 'pending';
    -- Still returns 5 orders (no phantom)
T1: COMMIT;
    -- Release all locks

                    T2: -- Now proceeds with insert
```

## 7.3 MVCC Implementation

### How MVCC Works

```
Each row stores:
┌────────────────────────────────────────────────────────┐
│  xmin  │  xmax  │  data...                            │
├────────┼────────┼─────────────────────────────────────┤
│  100   │  105   │  balance = 100  (old version)      │
│  105   │  null  │  balance = 50   (current version)  │
└────────┴────────┴─────────────────────────────────────┘

xmin = Transaction ID that created this version
xmax = Transaction ID that deleted/updated this version (null if current)
```

### Visibility Rules

```python
def is_visible(row, my_transaction_id, my_snapshot):
    """Check if a row version is visible to this transaction"""
    
    # Row must be created by a committed transaction before my snapshot
    if row.xmin >= my_snapshot.xmin:
        return False  # Created after my snapshot started
    
    if row.xmin not in my_snapshot.committed_transactions:
        return False  # Created by uncommitted transaction
    
    # Row must not be deleted/updated by any committed transaction in my view
    if row.xmax is None:
        return True  # Not deleted/updated
    
    if row.xmax >= my_snapshot.xmin:
        return True  # Deleted after my snapshot, still visible to me
    
    if row.xmax not in my_snapshot.committed_transactions:
        return True  # Deleted by uncommitted transaction, still visible
    
    return False  # Deleted by committed transaction before my snapshot
```

### READ COMMITTED with MVCC

```
T1 starts (snapshot at time=100)
T2 commits UPDATE (time=105)
T1 runs SELECT (takes NEW snapshot at time=110)
  → Sees T2's changes (each statement gets fresh snapshot)
```

### REPEATABLE READ with MVCC

```
T1 starts (snapshot at time=100, HELD for entire transaction)
T2 commits UPDATE (time=105)
T1 runs SELECT (uses ORIGINAL snapshot from time=100)
  → Does NOT see T2's changes (uses same snapshot)
```

### PostgreSQL SSI (Serializable Snapshot Isolation)

```
Instead of predicate locks, PostgreSQL:
1. Tracks read/write dependencies between transactions
2. Detects potential serialization anomalies
3. Aborts one transaction if anomaly detected

┌─────────────────────────────────────────────────────────────────┐
│                      SSI CONFLICT DETECTION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  T1: reads X    ─────┐                                          │
│                      │    rw-dependency                          │
│  T2: writes X   ◄────┘                                          │
│  T2: reads Y    ─────┐                                          │
│                      │    rw-dependency                          │
│  T1: writes Y   ◄────┘                                          │
│                                                                  │
│  Cycle detected! T1 → T2 → T1                                    │
│  One transaction must abort.                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 7.4 Lock Duration Comparison

```
                         Transaction Timeline
                    BEGIN ────────────────────── COMMIT

Locking-based:

READ UNCOMMITTED:   [no read locks]
                    [X-lock short]

READ COMMITTED:     [S]    [S]    [S]    (release after each read)
                    [─────── X ────────] (until commit)

REPEATABLE READ:    [─────── S ────────] (until commit)
                    [─────── X ────────] (until commit)

SERIALIZABLE:       [─────── S ────────] (until commit)
                    [─────── X ────────] (until commit)
                    [── Range Locks ───] (until commit)

MVCC-based:

All levels:         [no read locks - just snapshot visibility]
                    [─────── X ────────] (write locks until commit)
```

## 7.5 Practical Comparison

| Aspect | Locking (2PL) | MVCC |
|--------|---------------|------|
| **Readers vs Writers** | Block each other | Don't block |
| **Deadlocks** | Common | Rare (write-write only) |
| **Storage** | No overhead | Version chain overhead |
| **Rollback** | Undo log | Keep old versions |
| **Long transactions** | Block many others | Only use more space |
| **Conflict handling** | Wait/block | Abort on conflict |
| **Best for** | Write-heavy, low contention | Read-heavy, high concurrency |

---

# 8. Putting It All Together

## 8.1 Decision Framework

```
┌─────────────────────────────────────────────────────────────────┐
│               CHOOSING THE RIGHT APPROACH                        │
└─────────────────────────────────────────────────────────────────┘

Start here: What's your contention level?

                    LOW                          HIGH
                     │                            │
                     ▼                            ▼
           Optimistic Locking            Queue Serialization
           or READ COMMITTED             or Distributed Locks
                     │                            │
                     ▼                            ▼
              Need ACID?                 Need real-time?
                 │    │                      │    │
                Yes   No                   Yes   No
                 │     │                    │     │
                 ▼     ▼                    ▼     ▼
           SERIALIZABLE  Redis         Redis     Kafka
                       Atomics         Lock      Queue
```

## 8.2 Common Patterns

### Pattern 1: E-Commerce Checkout

```python
# Low contention: Optimistic locking
def checkout(cart_id, user_id):
    # 1. Get cart with version
    cart = db.query("SELECT * FROM carts WHERE id = ? FOR UPDATE", cart_id)
    
    # 2. Validate inventory (READ COMMITTED is fine)
    for item in cart.items:
        stock = db.query("SELECT quantity FROM inventory WHERE product_id = ?", item.product_id)
        if stock < item.quantity:
            raise OutOfStockError()
    
    # 3. Deduct inventory atomically
    for item in cart.items:
        result = db.execute("""
            UPDATE inventory 
            SET quantity = quantity - ?
            WHERE product_id = ? AND quantity >= ?
        """, item.quantity, item.product_id, item.quantity)
        
        if result.rows_affected == 0:
            raise OutOfStockError()
    
    # 4. Create order
    db.execute("INSERT INTO orders ...")
    db.commit()
```

### Pattern 2: Flash Sale (Extreme Contention)

```python
# High contention: Sharded counter + Queue
class FlashSale:
    def __init__(self, product_id, total_stock, num_shards=100):
        self.product_id = product_id
        self.counter = ShardedCounter(f"flash:{product_id}", num_shards)
        self.counter.initialize(total_stock)
    
    def try_purchase(self, user_id):
        # 1. Rate limit
        if not rate_limiter.allow(user_id):
            return "Rate limited"
        
        # 2. Quick stock check (sharded counter)
        if not self.counter.decrement():
            return "Sold out"
        
        # 3. Queue for actual processing
        kafka.send(
            topic='flash-sale-orders',
            key=str(self.product_id),
            value={'user_id': user_id, 'product_id': self.product_id}
        )
        
        return "Order queued"
```

### Pattern 3: Bank Transfer (Strong Consistency)

```python
# Critical operation: SERIALIZABLE + FOR UPDATE
def transfer(from_account, to_account, amount):
    with db.transaction(isolation='SERIALIZABLE'):
        # Lock both accounts (consistent ordering to prevent deadlock)
        accounts = sorted([from_account, to_account])
        
        for acc_id in accounts:
            db.execute("SELECT * FROM accounts WHERE id = ? FOR UPDATE", acc_id)
        
        # Check balance
        from_balance = db.query("SELECT balance FROM accounts WHERE id = ?", from_account)
        if from_balance < amount:
            raise InsufficientFundsError()
        
        # Transfer
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, from_account)
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, to_account)
        
        # Audit log
        db.execute("INSERT INTO transfers (from_id, to_id, amount, timestamp) VALUES ...")
        
        db.commit()
```

## 8.3 Quick Reference Card

| Scenario | Isolation Level | Lock Type | Strategy |
|----------|-----------------|-----------|----------|
| Read-only reporting | REPEATABLE READ | None (MVCC) | Snapshot |
| Simple CRUD | READ COMMITTED | Row locks | Optimistic |
| Financial transfer | SERIALIZABLE | FOR UPDATE | Pessimistic |
| Flash sale | READ COMMITTED | Distributed | Queue + Sharding |
| Document editing | READ COMMITTED | Advisory | Optimistic + Lock |
| Inventory reservation | REPEATABLE READ | FOR UPDATE | Pessimistic |
| Leaderboard updates | None | Redis atomic | Atomic ops |

## 8.4 Interview Checklist

When discussing concurrency in system design:

1. **Identify contention points**: "The bottleneck is the inventory counter..."

2. **Choose isolation level**: "We need REPEATABLE READ because..."

3. **Select locking strategy**: "Optimistic locking works here because conflict rate is low..."

4. **Consider distribution**: "For distributed systems, we need Redis locks or queue serialization..."

5. **Handle failures**: "If the lock holder dies, TTL ensures lock release..."

6. **Discuss trade-offs**: "Higher isolation means more blocking, lower throughput..."

7. **Know the limits**: "Optimistic locking falls apart above 30% conflict rate..."

---

## References

- PostgreSQL Documentation: Transaction Isolation
- MySQL Reference Manual: InnoDB Locking
- Designing Data-Intensive Applications - Martin Kleppmann
- Database Internals - Alex Petrov
- Kafka: The Definitive Guide
- Redis in Action

---

*Last updated: January 2025*

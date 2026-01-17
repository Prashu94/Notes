# Matching Engine - Deep Dive

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Matching Algorithms](#matching-algorithms)
4. [Order Book Implementation](#order-book-implementation)
5. [Performance Optimization](#performance-optimization)
6. [FPGA Implementation](#fpga-implementation)
7. [Failover and Recovery](#failover-and-recovery)
8. [Testing and Validation](#testing-and-validation)

## Introduction

The matching engine is the **heart of the stock exchange system**. It is responsible for matching buy and sell orders, maintaining the order book, and generating trades. The matching engine must operate with:

- **Ultra-low latency**: < 500 microseconds (ideally < 1 microsecond with FPGA)
- **High throughput**: 10M+ orders per second
- **Deterministic behavior**: Same input always produces same output
- **Zero data loss**: All orders and trades must be persisted
- **Fairness**: Price-time priority must be strictly enforced

### Key Requirements

1. **Latency**: End-to-end order-to-trade < 1ms (p99)
2. **Throughput**: 10M orders/sec, 1M trades/sec
3. **Availability**: 99.999% (5 minutes downtime/year)
4. **Consistency**: ACID compliance, no duplicate trades
5. **Fairness**: Strict price-time priority
6. **Auditability**: Complete order/trade history

## Architecture

### Matching Engine Components

```
┌──────────────────────────────────────────────────────────────┐
│                     MATCHING ENGINE                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐      ┌────────────────┐                 │
│  │ Order Receiver │      │ Order Validator│                 │
│  │ (10G NIC)      │─────►│ (Syntax Check) │                 │
│  └────────────────┘      └────────┬───────┘                 │
│                                    │                          │
│                                    ▼                          │
│                          ┌────────────────┐                  │
│                          │ Order Sequencer│                  │
│                          │ (Timestamping) │                  │
│                          └────────┬───────┘                  │
│                                    │                          │
│         ┌──────────────────────────┴───────────────┐         │
│         │                                           │         │
│         ▼                                           ▼         │
│  ┌─────────────┐                           ┌─────────────┐  │
│  │ Order Book  │                           │ Order Book  │  │
│  │   AAPL      │                           │   GOOGL     │  │
│  │ (In-Memory) │                           │ (In-Memory) │  │
│  └──────┬──────┘                           └──────┬──────┘  │
│         │                                           │         │
│         │          ┌────────────────┐              │         │
│         └─────────►│ Match Algorithm│◄─────────────┘         │
│                    │ (Price-Time)   │                        │
│                    └────────┬───────┘                        │
│                             │                                 │
│                    ┌────────▼───────┐                        │
│                    │ Trade Generator│                        │
│                    │ (Atomic Exec)  │                        │
│                    └────────┬───────┘                        │
│                             │                                 │
│              ┌──────────────┼──────────────┐                │
│              │              │              │                │
│              ▼              ▼              ▼                │
│    ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│    │ Trade Log  │  │ Market Data│  │ Order ACK  │         │
│    │ (Persist)  │  │ Publisher  │  │ Publisher  │         │
│    └────────────┘  └────────────┘  └────────────┘         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Deployment Options

#### Option 1: Software-based (C++/Rust on High-Performance Servers)
```yaml
Hardware:
  CPU: Intel Xeon Platinum 8380 (40 cores, 2.3GHz)
  RAM: 512GB DDR4-3200 ECC
  Network: Mellanox ConnectX-6 (100Gbps, RDMA)
  Storage: Intel Optane P5800X (NVMe, 1.6TB)
  
Optimizations:
  - Kernel bypass (DPDK)
  - CPU pinning (isolcpus)
  - NUMA optimization
  - Huge pages (2MB/1GB)
  - Polling mode (no interrupts)
  - Lock-free data structures
  
Performance:
  Latency: 10-50 microseconds
  Throughput: 5M orders/sec
  Cost: ~$50K per server
```

#### Option 2: FPGA-based (Ultra-Low Latency)
```yaml
Hardware:
  FPGA: Xilinx Ultrascale+ VU9P
  RAM: 128GB DDR4 + 8GB HBM2
  Network: 100Gbps Ethernet (10x 10Gbps)
  Host: Intel Xeon for control plane
  
Features:
  - Hardware order book
  - Pipelined matching logic
  - Parallel order processing
  - Deterministic latency
  
Performance:
  Latency: 200-500 nanoseconds
  Throughput: 10M+ orders/sec
  Cost: ~$200K per FPGA card
```

#### Option 3: Hybrid (FPGA + Software)
- FPGA for hot symbols (top 100 stocks)
- Software for long-tail symbols
- Automatic failover between modes

## Matching Algorithms

### 1. Price-Time Priority (FIFO)

The most common algorithm used in stock exchanges worldwide.

**Rules**:
1. Best price gets priority (lowest for sell, highest for buy)
2. At same price level, earliest order gets priority (FIFO)
3. Incoming order matches against best opposite side
4. Continue matching until order is filled or no match available

**Example**:
```
Order Book (AAPL):
BUY ORDERS:               SELL ORDERS:
$100.00: 500 shares       $100.05: 300 shares (10:00:01)
         200 shares       $100.05: 200 shares (10:00:05)
$ 99.95: 1000 shares      $100.10: 1000 shares

Incoming Order: SELL 400 @ Market
Match 1: 400 shares @ $100.00 (matched with first buy order)

Resulting Book:
BUY ORDERS:               SELL ORDERS:
$100.00: 100 shares       $100.05: 300 shares
         200 shares       $100.05: 200 shares
$ 99.95: 1000 shares      $100.10: 1000 shares
```

**Implementation (Simplified)**:
```rust
struct Order {
    id: u64,
    symbol: String,
    side: Side,
    price: Option<f64>,  // None for market orders
    quantity: u64,
    timestamp: u64,
}

struct OrderBook {
    buy_orders: BTreeMap<OrderedFloat<f64>, VecDeque<Order>>,  // Max heap
    sell_orders: BTreeMap<OrderedFloat<f64>, VecDeque<Order>>, // Min heap
}

impl OrderBook {
    fn match_order(&mut self, order: Order) -> Vec<Trade> {
        let mut trades = Vec::new();
        let mut remaining_qty = order.quantity;
        
        while remaining_qty > 0 {
            let best_opposite = match order.side {
                Side::Buy => self.sell_orders.first_entry(),
                Side::Sell => self.buy_orders.last_entry(),
            };
            
            let Some(mut opposite_entry) = best_opposite else {
                break; // No match available
            };
            
            // Check if price matches
            if !self.prices_match(&order, opposite_entry.key()) {
                break;
            }
            
            let opposite_orders = opposite_entry.get_mut();
            let opposite_order = opposite_orders.front_mut().unwrap();
            
            // Calculate trade quantity
            let trade_qty = min(remaining_qty, opposite_order.quantity);
            let trade_price = opposite_order.price.unwrap();
            
            // Generate trade
            trades.push(Trade {
                id: generate_trade_id(),
                symbol: order.symbol.clone(),
                buy_order_id: if order.side == Side::Buy { 
                    order.id 
                } else { 
                    opposite_order.id 
                },
                sell_order_id: if order.side == Side::Sell { 
                    order.id 
                } else { 
                    opposite_order.id 
                },
                price: trade_price,
                quantity: trade_qty,
                timestamp: current_timestamp(),
            });
            
            // Update quantities
            remaining_qty -= trade_qty;
            opposite_order.quantity -= trade_qty;
            
            // Remove filled order
            if opposite_order.quantity == 0 {
                opposite_orders.pop_front();
                if opposite_orders.is_empty() {
                    opposite_entry.remove();
                }
            }
        }
        
        // Add remaining quantity to book
        if remaining_qty > 0 {
            self.add_to_book(order, remaining_qty);
        }
        
        trades
    }
    
    fn prices_match(&self, order: &Order, book_price: &OrderedFloat<f64>) -> bool {
        match (order.side, order.price) {
            (Side::Buy, Some(limit)) => limit >= **book_price,
            (Side::Sell, Some(limit)) => limit <= **book_price,
            (_, None) => true, // Market order always matches
        }
    }
}
```

### 2. Pro-Rata Matching

Orders at the same price level are filled proportionally based on their size.

**Rules**:
1. Best price still has priority
2. At same price, fills are allocated proportionally
3. Minimum allocation (e.g., 1 lot) to avoid tiny fills

**Example**:
```
Order Book (ES Futures):
BUY ORDERS:
$4000.00: Order A - 1000 contracts
          Order B - 500 contracts
          Order C - 500 contracts
          Total: 2000 contracts

Incoming Order: SELL 1000 @ $4000.00

Pro-Rata Allocation:
Order A: 1000/2000 * 1000 = 500 contracts
Order B: 500/2000 * 1000 = 250 contracts
Order C: 500/2000 * 1000 = 250 contracts
```

**Implementation**:
```rust
fn match_pro_rata(&mut self, order: Order) -> Vec<Trade> {
    let mut trades = Vec::new();
    let mut remaining_qty = order.quantity;
    
    while remaining_qty > 0 {
        let best_level = self.get_best_opposite_level(&order.side);
        if best_level.is_none() || !self.prices_match(&order, best_level.unwrap().0) {
            break;
        }
        
        let (price, orders) = best_level.unwrap();
        let total_qty: u64 = orders.iter().map(|o| o.quantity).sum();
        
        for opposite_order in orders.iter_mut() {
            let allocation = (opposite_order.quantity as f64 / total_qty as f64 
                             * remaining_qty as f64) as u64;
            let trade_qty = min(allocation, opposite_order.quantity);
            
            if trade_qty >= MIN_ALLOCATION {
                trades.push(create_trade(&order, opposite_order, trade_qty, *price));
                opposite_order.quantity -= trade_qty;
                remaining_qty -= trade_qty;
            }
        }
        
        // Remove filled orders
        orders.retain(|o| o.quantity > 0);
        if orders.is_empty() {
            self.remove_price_level(*price, order.side);
        }
    }
    
    trades
}
```

### 3. Size Pro-Rata

Larger orders get priority at the same price level.

**Implementation**:
```rust
fn match_size_pro_rata(&mut self, order: Order) -> Vec<Trade> {
    // Sort orders at same price by size (descending)
    let best_level = self.get_best_opposite_level(&order.side);
    if let Some((price, orders)) = best_level {
        orders.sort_by(|a, b| b.quantity.cmp(&a.quantity));
        // Then apply pro-rata logic
    }
    // ... rest of matching logic
}
```

### 4. Time Pro-Rata

Hybrid approach: allocate a percentage (e.g., 50%) by time priority, remainder pro-rata.

```rust
fn match_time_pro_rata(&mut self, order: Order, time_allocation: f64) -> Vec<Trade> {
    let time_qty = (order.quantity as f64 * time_allocation) as u64;
    let pro_rata_qty = order.quantity - time_qty;
    
    let mut trades = Vec::new();
    
    // First, allocate by time priority (FIFO)
    trades.extend(self.match_fifo(order.clone(), time_qty));
    
    // Then, allocate remainder pro-rata
    trades.extend(self.match_pro_rata(order, pro_rata_qty));
    
    trades
}
```

## Order Book Implementation

### In-Memory Order Book Structure

```rust
use std::collections::{BTreeMap, VecDeque, HashMap};
use std::sync::Arc;
use parking_lot::RwLock;

pub struct OrderBook {
    symbol: String,
    
    // Price levels (BTreeMap for sorted prices)
    buy_levels: BTreeMap<OrderedFloat<f64>, PriceLevel>,  // Descending
    sell_levels: BTreeMap<OrderedFloat<f64>, PriceLevel>, // Ascending
    
    // Quick lookup by order ID
    order_index: HashMap<u64, OrderInfo>,
    
    // Best bid/offer cache
    bbo: BBO,
    
    // Statistics
    last_trade: Option<Trade>,
    total_volume: u64,
    trade_count: u64,
}

struct PriceLevel {
    price: f64,
    total_quantity: u64,
    orders: VecDeque<Order>, // FIFO queue
    order_count: u32,
}

struct OrderInfo {
    price: f64,
    side: Side,
    index: usize, // Index in the VecDeque
}

struct BBO {
    best_bid: Option<f64>,
    best_bid_qty: u64,
    best_ask: Option<f64>,
    best_ask_qty: u64,
    last_update: u64,
}

impl OrderBook {
    pub fn new(symbol: String) -> Self {
        OrderBook {
            symbol,
            buy_levels: BTreeMap::new(),
            sell_levels: BTreeMap::new(),
            order_index: HashMap::new(),
            bbo: BBO::default(),
            last_trade: None,
            total_volume: 0,
            trade_count: 0,
        }
    }
    
    pub fn add_order(&mut self, order: Order) {
        let levels = match order.side {
            Side::Buy => &mut self.buy_levels,
            Side::Sell => &mut self.sell_levels,
        };
        
        let price = OrderedFloat(order.price.unwrap());
        let level = levels.entry(price).or_insert_with(|| PriceLevel {
            price: order.price.unwrap(),
            total_quantity: 0,
            orders: VecDeque::new(),
            order_count: 0,
        });
        
        let index = level.orders.len();
        level.orders.push_back(order.clone());
        level.total_quantity += order.quantity;
        level.order_count += 1;
        
        self.order_index.insert(order.id, OrderInfo {
            price: order.price.unwrap(),
            side: order.side,
            index,
        });
        
        self.update_bbo();
    }
    
    pub fn cancel_order(&mut self, order_id: u64) -> Result<(), String> {
        let order_info = self.order_index.remove(&order_id)
            .ok_or("Order not found")?;
        
        let levels = match order_info.side {
            Side::Buy => &mut self.buy_levels,
            Side::Sell => &mut self.sell_levels,
        };
        
        let price = OrderedFloat(order_info.price);
        let level = levels.get_mut(&price)
            .ok_or("Price level not found")?;
        
        let order = level.orders.remove(order_info.index)
            .ok_or("Order not in queue")?;
        
        level.total_quantity -= order.quantity;
        level.order_count -= 1;
        
        if level.orders.is_empty() {
            levels.remove(&price);
        }
        
        self.update_bbo();
        Ok(())
    }
    
    pub fn modify_order(&mut self, order_id: u64, new_quantity: u64) -> Result<(), String> {
        // For price modifications, we cancel and re-add to maintain time priority
        let order_info = self.order_index.get(&order_id)
            .ok_or("Order not found")?;
        
        let levels = match order_info.side {
            Side::Buy => &mut self.buy_levels,
            Side::Sell => &mut self.sell_levels,
        };
        
        let price = OrderedFloat(order_info.price);
        let level = levels.get_mut(&price)
            .ok_or("Price level not found")?;
        
        let order = &mut level.orders[order_info.index];
        let old_quantity = order.quantity;
        order.quantity = new_quantity;
        
        level.total_quantity = level.total_quantity - old_quantity + new_quantity;
        
        self.update_bbo();
        Ok(())
    }
    
    fn update_bbo(&mut self) {
        self.bbo.best_bid = self.buy_levels.last_key_value()
            .map(|(price, _)| price.0);
        self.bbo.best_bid_qty = self.buy_levels.last_key_value()
            .map(|(_, level)| level.total_quantity)
            .unwrap_or(0);
        
        self.bbo.best_ask = self.sell_levels.first_key_value()
            .map(|(price, _)| price.0);
        self.bbo.best_ask_qty = self.sell_levels.first_key_value()
            .map(|(_, level)| level.total_quantity)
            .unwrap_or(0);
        
        self.bbo.last_update = current_timestamp();
    }
    
    pub fn get_depth(&self, levels: usize) -> OrderBookDepth {
        let bids: Vec<_> = self.buy_levels.iter()
            .rev()
            .take(levels)
            .map(|(price, level)| PricePoint {
                price: price.0,
                quantity: level.total_quantity,
                order_count: level.order_count,
            })
            .collect();
        
        let asks: Vec<_> = self.sell_levels.iter()
            .take(levels)
            .map(|(price, level)| PricePoint {
                price: price.0,
                quantity: level.total_quantity,
                order_count: level.order_count,
            })
            .collect();
        
        OrderBookDepth { bids, asks }
    }
}
```

### Lock-Free Order Book (Advanced)

For maximum performance, use lock-free data structures:

```rust
use crossbeam::queue::SegQueue;
use std::sync::atomic::{AtomicU64, Ordering};

pub struct LockFreeOrderBook {
    symbol: String,
    
    // Lock-free queues for each price level
    price_levels: DashMap<OrderedFloat<f64>, Arc<PriceLevel>>,
    
    // Atomic counters
    total_volume: AtomicU64,
    trade_count: AtomicU64,
}

struct PriceLevel {
    price: f64,
    orders: SegQueue<Order>, // Lock-free queue
    total_quantity: AtomicU64,
}

impl LockFreeOrderBook {
    pub fn add_order(&self, order: Order) {
        let price = OrderedFloat(order.price.unwrap());
        let level = self.price_levels.entry(price)
            .or_insert_with(|| Arc::new(PriceLevel {
                price: order.price.unwrap(),
                orders: SegQueue::new(),
                total_quantity: AtomicU64::new(0),
            }));
        
        level.total_quantity.fetch_add(order.quantity, Ordering::SeqCst);
        level.orders.push(order);
    }
}
```

## Performance Optimization

### 1. Memory Optimization

**Huge Pages**:
```bash
# Enable 1GB huge pages
echo 8 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# Mount hugetlbfs
mount -t hugetlbfs -o pagesize=1G none /mnt/huge

# In application
mmap(..., MAP_HUGETLB | MAP_HUGE_1GB, ...)
```

**Memory Pool**:
```rust
use std::alloc::{alloc, dealloc, Layout};

struct OrderPool {
    pool: Vec<*mut Order>,
    capacity: usize,
    layout: Layout,
}

impl OrderPool {
    fn new(capacity: usize) -> Self {
        let layout = Layout::new::<Order>();
        let mut pool = Vec::with_capacity(capacity);
        
        for _ in 0..capacity {
            unsafe {
                let ptr = alloc(layout) as *mut Order;
                pool.push(ptr);
            }
        }
        
        OrderPool { pool, capacity, layout }
    }
    
    fn allocate(&mut self) -> Option<*mut Order> {
        self.pool.pop()
    }
    
    fn deallocate(&mut self, ptr: *mut Order) {
        self.pool.push(ptr);
    }
}
```

### 2. CPU Optimization

**CPU Pinning**:
```rust
use core_affinity::CoreId;

fn pin_to_core(core_id: usize) {
    let core = CoreId { id: core_id };
    core_affinity::set_for_current(core);
}

// Pin matching engine to dedicated cores
fn main() {
    pin_to_core(0); // Core 0 for order receiver
    std::thread::spawn(|| {
        pin_to_core(1); // Core 1 for matching logic
        matching_engine_loop();
    });
}
```

**NUMA Awareness**:
```rust
use numa::{NodeId, NumaPolicy};

fn allocate_numa_memory(size: usize, node: NodeId) -> *mut u8 {
    numa::allocate(size, NumaPolicy::Bind(node))
}
```

### 3. Network Optimization

**Kernel Bypass (DPDK)**:
```c
#include <rte_eal.h>
#include <rte_ethdev.h>

int main(int argc, char **argv) {
    // Initialize DPDK
    int ret = rte_eal_init(argc, argv);
    
    // Configure ports for zero-copy packet processing
    struct rte_eth_conf port_conf = {
        .rxmode = {
            .mq_mode = RTE_ETH_MQ_RX_RSS,
            .offloads = RTE_ETH_RX_OFFLOAD_CHECKSUM,
        },
    };
    
    rte_eth_dev_configure(port_id, nb_rx_queues, nb_tx_queues, &port_conf);
    
    // Poll packets without kernel overhead
    while (1) {
        struct rte_mbuf *bufs[BURST_SIZE];
        uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, bufs, BURST_SIZE);
        
        for (int i = 0; i < nb_rx; i++) {
            process_order(bufs[i]);
        }
    }
}
```

**RDMA (Remote Direct Memory Access)**:
```c
#include <infiniband/verbs.h>

// Zero-copy network transfer
struct ibv_qp *qp = create_qp(context);
struct ibv_mr *mr = ibv_reg_mr(pd, buffer, size, 
                                IBV_ACCESS_LOCAL_WRITE | 
                                IBV_ACCESS_REMOTE_WRITE);

// Post receive work request
struct ibv_sge sge = {
    .addr = (uint64_t)buffer,
    .length = size,
    .lkey = mr->lkey,
};

struct ibv_recv_wr wr = {
    .sg_list = &sge,
    .num_sge = 1,
};

ibv_post_recv(qp, &wr, &bad_wr);
```

### 4. Time Synchronization

**PTP (Precision Time Protocol)**:
```bash
# Install linuxptp
apt-get install linuxptp

# Configure PTP
cat > /etc/linuxptp/ptp4l.conf <<EOF
[global]
slaveOnly 1
priority1 128
priority2 128
clockClass 248
clockAccuracy 0xFE
offsetScaledLogVariance 0xFFFF
[eth0]
delay_mechanism E2E
network_transport UDPv4
EOF

# Start PTP daemon
ptp4l -f /etc/linuxptp/ptp4l.conf -i eth0 -m

# Synchronize system clock
phc2sys -s eth0 -c CLOCK_REALTIME -w -m
```

## FPGA Implementation

### High-Level Architecture

```
┌────────────────────────────────────────────────────┐
│                 FPGA MATCHING ENGINE                │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐       ┌──────────────┐          │
│  │ 100G Network │──────►│ Parser       │          │
│  │ Interface    │       │ (Order Decode│          │
│  └──────────────┘       └──────┬───────┘          │
│                                 │                   │
│                                 ▼                   │
│                        ┌─────────────────┐         │
│                        │ Order Validator │         │
│                        │ (Syntax, Range) │         │
│                        └────────┬────────┘         │
│                                 │                   │
│                 ┌───────────────┴───────────────┐  │
│                 │                               │  │
│                 ▼                               ▼  │
│       ┌──────────────────┐          ┌──────────────────┐
│       │ Order Book (BUY) │          │ Order Book (SELL)│
│       │ - BRAM/HBM       │          │ - BRAM/HBM       │
│       │ - Sorted Tree    │          │ - Sorted Tree    │
│       └────────┬─────────┘          └─────────┬────────┘
│                │                              │         │
│                └──────────┬───────────────────┘         │
│                           │                             │
│                           ▼                             │
│                  ┌─────────────────┐                   │
│                  │ Match Logic     │                   │
│                  │ (Pipelined)     │                   │
│                  └────────┬────────┘                   │
│                           │                             │
│              ┌────────────┼────────────┐               │
│              │            │            │               │
│              ▼            ▼            ▼               │
│       ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│       │ Trade Gen │ │ Book Update│ │ ACK Gen   │      │
│       │ (Atomic)  │ │ (Parallel) │ │ (Fast)    │      │
│       └─────┬─────┘ └─────┬─────┘ └─────┬─────┘      │
│             │             │             │             │
│             └─────────────┼─────────────┘             │
│                           │                           │
│                           ▼                           │
│                  ┌─────────────────┐                  │
│                  │ Output Formatter│                  │
│                  │ & DMA Engine    │                  │
│                  └────────┬────────┘                  │
│                           │                           │
└───────────────────────────┼───────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Host CPU        │
                   │ (Control Plane) │
                   └─────────────────┘
```

### FPGA Order Book (Verilog/VHDL Pseudocode)

```verilog
module matching_engine (
    input wire clk,
    input wire rst,
    input wire [511:0] order_in,
    input wire order_valid,
    output reg [511:0] trade_out,
    output reg trade_valid
);

// Order book storage (BRAM)
reg [63:0] buy_prices [0:1023];   // Price levels
reg [31:0] buy_quantities [0:1023];
reg [63:0] buy_timestamps [0:1023];
reg [10:0] buy_head, buy_tail;

reg [63:0] sell_prices [0:1023];
reg [31:0] sell_quantities [0:1023];
reg [63:0] sell_timestamps [0:1023];
reg [10:0] sell_head, sell_tail;

// Pipeline stages
reg [2:0] state;
parameter IDLE = 3'b000;
parameter PARSE = 3'b001;
parameter MATCH = 3'b010;
parameter TRADE = 3'b011;
parameter UPDATE = 3'b100;

always @(posedge clk) begin
    if (rst) begin
        state <= IDLE;
        buy_head <= 0;
        sell_head <= 0;
    end else begin
        case (state)
            IDLE: begin
                if (order_valid) begin
                    state <= PARSE;
                end
            end
            
            PARSE: begin
                // Parse incoming order
                order_id <= order_in[63:0];
                order_side <= order_in[64];
                order_price <= order_in[127:65];
                order_qty <= order_in[159:128];
                state <= MATCH;
            end
            
            MATCH: begin
                // Check for match
                if (order_side == BUY) begin
                    if (sell_head != sell_tail && 
                        order_price >= sell_prices[sell_head]) begin
                        state <= TRADE;
                    end else begin
                        state <= UPDATE;
                    end
                end else begin
                    if (buy_head != buy_tail && 
                        order_price <= buy_prices[buy_head]) begin
                        state <= TRADE;
                    end else begin
                        state <= UPDATE;
                    end
                end
            end
            
            TRADE: begin
                // Generate trade
                trade_qty <= min(order_qty, 
                                order_side == BUY ? 
                                sell_quantities[sell_head] : 
                                buy_quantities[buy_head]);
                trade_price <= order_side == BUY ? 
                              sell_prices[sell_head] : 
                              buy_prices[buy_head];
                trade_valid <= 1;
                state <= UPDATE;
            end
            
            UPDATE: begin
                // Update order book
                if (order_qty > 0) begin
                    if (order_side == BUY) begin
                        buy_prices[buy_tail] <= order_price;
                        buy_quantities[buy_tail] <= order_qty;
                        buy_timestamps[buy_tail] <= current_time;
                        buy_tail <= buy_tail + 1;
                    end else begin
                        sell_prices[sell_tail] <= order_price;
                        sell_quantities[sell_tail] <= order_qty;
                        sell_timestamps[sell_tail] <= current_time;
                        sell_tail <= sell_tail + 1;
                    end
                end
                state <= IDLE;
            end
        endcase
    end
end

endmodule
```

### FPGA Performance Characteristics

```yaml
Latency Breakdown (nanoseconds):
  Network RX: 50ns
  Parse: 20ns
  Lookup: 30ns
  Match: 50ns
  Trade Gen: 30ns
  Book Update: 40ns
  Network TX: 50ns
  Total: 270ns (0.27 microseconds)

Throughput:
  Orders/sec: 10,000,000
  Trades/sec: 1,000,000
  Symbols: 1000 concurrent

Resource Utilization (Xilinx VU9P):
  LUTs: 450K / 1.2M (38%)
  FFs: 600K / 2.5M (24%)
  BRAM: 1200 / 2160 (56%)
  DSPs: 200 / 6840 (3%)
```

## Failover and Recovery

### Hot-Hot Failover

```
┌──────────────────┐          ┌──────────────────┐
│ Primary FPGA     │          │ Secondary FPGA   │
│ - Active         │◄────────►│ - Active         │
│ - Processing     │ Sync     │ - Processing     │
│ - Order Book A   │          │ - Order Book B   │
└────────┬─────────┘          └─────────┬────────┘
         │                              │
         └──────────┬───────────────────┘
                    │
            ┌───────▼────────┐
            │ Arbiter        │
            │ (Trade Verify) │
            └────────────────┘
```

**Trade Verification**:
```rust
fn verify_trades(trade1: &Trade, trade2: &Trade) -> bool {
    trade1.id == trade2.id &&
    trade1.price == trade2.price &&
    trade1.quantity == trade2.quantity &&
    trade1.buy_order_id == trade2.buy_order_id &&
    trade1.sell_order_id == trade2.sell_order_id
}

fn arbiter_loop() {
    loop {
        let trade1 = fpga1_channel.recv();
        let trade2 = fpga2_channel.recv();
        
        if verify_trades(&trade1, &trade2) {
            publish_trade(trade1);
        } else {
            // Divergence detected!
            handle_divergence(trade1, trade2);
        }
    }
}
```

### Recovery from Crash

```rust
struct RecoveryManager {
    wal: WriteAheadLog,
    snapshot: SnapshotManager,
}

impl RecoveryManager {
    fn recover(&self) -> OrderBook {
        // Load latest snapshot
        let mut order_book = self.snapshot.load_latest();
        
        // Replay WAL from snapshot point
        let wal_entries = self.wal.read_from(order_book.last_sequence);
        
        for entry in wal_entries {
            match entry {
                WALEntry::NewOrder(order) => order_book.add_order(order),
                WALEntry::CancelOrder(id) => order_book.cancel_order(id),
                WALEntry::Trade(trade) => order_book.apply_trade(trade),
            }
        }
        
        order_book
    }
}

// Write-Ahead Log
struct WriteAheadLog {
    file: File,
    buffer: Vec<WALEntry>,
    sequence: AtomicU64,
}

impl WriteAheadLog {
    fn append(&mut self, entry: WALEntry) {
        let seq = self.sequence.fetch_add(1, Ordering::SeqCst);
        entry.sequence = seq;
        
        // Write to buffer
        self.buffer.push(entry.clone());
        
        // Flush if buffer full
        if self.buffer.len() >= BUFFER_SIZE {
            self.flush();
        }
    }
    
    fn flush(&mut self) {
        // Write buffer to disk (with O_DIRECT for durability)
        let data = bincode::serialize(&self.buffer).unwrap();
        self.file.write_all(&data).unwrap();
        self.file.sync_all().unwrap();
        self.buffer.clear();
    }
}
```

## Testing and Validation

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_price_time_priority() {
        let mut book = OrderBook::new("AAPL".to_string());
        
        // Add buy orders
        book.add_order(Order {
            id: 1,
            side: Side::Buy,
            price: Some(100.0),
            quantity: 500,
            timestamp: 1000,
        });
        
        book.add_order(Order {
            id: 2,
            side: Side::Buy,
            price: Some(100.0),
            quantity: 300,
            timestamp: 2000,
        });
        
        // Incoming sell order should match first buy order first
        let trades = book.match_order(Order {
            id: 3,
            side: Side::Sell,
            price: Some(100.0),
            quantity: 400,
        });
        
        assert_eq!(trades.len(), 1);
        assert_eq!(trades[0].buy_order_id, 1);
        assert_eq!(trades[0].quantity, 400);
        
        // Verify remaining book
        let depth = book.get_depth(1);
        assert_eq!(depth.bids[0].quantity, 100); // Order 1 remainder
    }
    
    #[test]
    fn test_market_order_matching() {
        let mut book = OrderBook::new("GOOGL".to_string());
        
        book.add_order(Order {
            id: 1,
            side: Side::Sell,
            price: Some(2800.0),
            quantity: 100,
            timestamp: 1000,
        });
        
        let trades = book.match_order(Order {
            id: 2,
            side: Side::Buy,
            price: None, // Market order
            quantity: 50,
        });
        
        assert_eq!(trades.len(), 1);
        assert_eq!(trades[0].price, 2800.0);
        assert_eq!(trades[0].quantity, 50);
    }
}
```

### Load Testing

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_matching(c: &mut Criterion) {
    let mut book = OrderBook::new("AAPL".to_string());
    
    // Pre-populate order book
    for i in 0..10000 {
        book.add_order(Order {
            id: i,
            side: if i % 2 == 0 { Side::Buy } else { Side::Sell },
            price: Some(100.0 + (i % 100) as f64 * 0.01),
            quantity: 100,
            timestamp: i as u64,
        });
    }
    
    c.bench_function("match_order", |b| {
        b.iter(|| {
            book.match_order(black_box(Order {
                id: 100000,
                side: Side::Buy,
                price: Some(100.50),
                quantity: 100,
                timestamp: 100000,
            }))
        })
    });
}

criterion_group!(benches, benchmark_matching);
criterion_main!(benches);
```

### Latency Testing

```rust
use hdrhistogram::Histogram;
use std::time::Instant;

fn latency_test() {
    let mut histogram = Histogram::<u64>::new(5).unwrap();
    let mut book = OrderBook::new("AAPL".to_string());
    
    for i in 0..1_000_000 {
        let order = generate_random_order(i);
        
        let start = Instant::now();
        book.match_order(order);
        let elapsed = start.elapsed().as_nanos() as u64;
        
        histogram.record(elapsed).unwrap();
    }
    
    println!("Latency Statistics:");
    println!("  Min: {} ns", histogram.min());
    println!("  p50: {} ns", histogram.value_at_quantile(0.50));
    println!("  p95: {} ns", histogram.value_at_quantile(0.95));
    println!("  p99: {} ns", histogram.value_at_quantile(0.99));
    println!("  p99.9: {} ns", histogram.value_at_quantile(0.999));
    println!("  Max: {} ns", histogram.max());
}
```

---

**Document Version**: 1.0  
**Last Updated**: January 15, 2026  
**Status**: Draft

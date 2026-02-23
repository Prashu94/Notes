# MicroGPT Deep Dive — Code, Architecture & Mathematics

> **Author's note**: This document is a comprehensive study guide for Andrej Karpathy's `microgpt.py` — the most minimal, dependency-free implementation of a GPT (Generative Pre-trained Transformer) in pure Python. It covers the code architecture line-by-line, the mathematics behind every operation, and a structured learning path to master each concept.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Code Walkthrough](#3-code-walkthrough)
   - [3.1 Dataset & Tokenizer](#31-dataset--tokenizer)
   - [3.2 Automatic Differentiation (Autograd)](#32-automatic-differentiation-autograd)
   - [3.3 Model Parameters Initialization](#33-model-parameters-initialization)
   - [3.4 Model Architecture (The GPT Forward Pass)](#34-model-architecture-the-gpt-forward-pass)
   - [3.5 Training Loop](#35-training-loop)
   - [3.6 Inference (Text Generation)](#36-inference-text-generation)
4. [Mathematics Deep Dive](#4-mathematics-deep-dive)
   - [4.1 Chain Rule & Backpropagation](#41-chain-rule--backpropagation)
   - [4.2 Linear Transformation](#42-linear-transformation)
   - [4.3 Softmax Function](#43-softmax-function)
   - [4.4 RMSNorm (Root Mean Square Normalization)](#44-rmsnorm-root-mean-square-normalization)
   - [4.5 Scaled Dot-Product Attention](#45-scaled-dot-product-attention)
   - [4.6 Multi-Head Attention](#46-multi-head-attention)
   - [4.7 Cross-Entropy Loss](#47-cross-entropy-loss)
   - [4.8 Adam Optimizer](#48-adam-optimizer)
   - [4.9 Residual Connections](#49-residual-connections)
   - [4.10 Embeddings (Token & Positional)](#410-embeddings-token--positional)
   - [4.11 Temperature Scaling](#411-temperature-scaling)
5. [How All the Pieces Fit Together](#5-how-all-the-pieces-fit-together)
6. [Learning Path — Mathematics Prerequisites](#6-learning-path--mathematics-prerequisites)
7. [Recommended Resources](#7-recommended-resources)
8. [Exercises to Solidify Understanding](#8-exercises-to-solidify-understanding)

---

## 1. High-Level Overview

`microgpt.py` implements a complete GPT from scratch in ~150 lines of pure Python (no PyTorch, no NumPy). It has **five** major parts:

| # | Component | Purpose |
|---|-----------|---------|
| 1 | **Dataset & Tokenizer** | Loads a text file of names, converts characters to integer tokens |
| 2 | **Autograd Engine** (`Value` class) | Tracks computations and computes gradients via backpropagation |
| 3 | **Model Parameters** | Weight matrices randomly initialized — this is the "knowledge" |
| 4 | **GPT Forward Pass** | Transformer architecture: embeddings → RMSNorm → Multi-Head Attention → MLP → logits |
| 5 | **Training Loop + Inference** | Adam optimizer trains the model; temperature-scaled sampling generates new names |

The dataset is a list of ~32K human names. The model learns to predict the next character given previous characters, then generates new, plausible-sounding names.

---

## 2. Architecture Diagram

```
Input: token_id, pos_id
        │
        ▼
┌───────────────────────┐
│  Token Embedding (wte) │──► lookup row from (vocab_size × n_embd) matrix
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Position Embedding(wpe)│──► lookup row from (block_size × n_embd) matrix
└───────────┬───────────┘
            │
            ▼
      x = tok_emb + pos_emb       ◄── Element-wise addition
            │
            ▼
      ┌─────────────┐
      │   RMSNorm    │
      └──────┬──────┘
             │
    ╔════════╧════════════════════════════════════════════╗
    ║         TRANSFORMER BLOCK (repeated n_layer times)  ║
    ║                                                     ║
    ║  ┌────────────────────────────────────────┐        ║
    ║  │ 1. Multi-Head Causal Self-Attention     │        ║
    ║  │    ┌──────────┐                         │        ║
    ║  │    │ RMSNorm  │                         │        ║
    ║  │    └────┬─────┘                         │        ║
    ║  │         ▼                               │        ║
    ║  │   Q = linear(x, W_q)                    │        ║
    ║  │   K = linear(x, W_k)                    │        ║
    ║  │   V = linear(x, W_v)                    │        ║
    ║  │         │                               │        ║
    ║  │    Split into n_head heads               │        ║
    ║  │         │                               │        ║
    ║  │    For each head h:                     │        ║
    ║  │      attn_logits = Q_h · K_h^T / √d_k  │        ║
    ║  │      attn_weights = softmax(attn_logits)│        ║
    ║  │      head_out = attn_weights · V_h      │        ║
    ║  │         │                               │        ║
    ║  │    Concat all heads                     │        ║
    ║  │    x_attn = linear(concat, W_o)         │        ║
    ║  │         │                               │        ║
    ║  │    x = x_attn + x_residual  ◄─ Residual │        ║
    ║  └────────────────────────────────────────┘        ║
    ║                                                     ║
    ║  ┌────────────────────────────────────────┐        ║
    ║  │ 2. Feed-Forward MLP Block               │        ║
    ║  │    ┌──────────┐                         │        ║
    ║  │    │ RMSNorm  │                         │        ║
    ║  │    └────┬─────┘                         │        ║
    ║  │         ▼                               │        ║
    ║  │    x = linear(x, W_fc1)   (expand 4×)  │        ║
    ║  │    x = ReLU(x)                          │        ║
    ║  │    x = linear(x, W_fc2)   (project back)│        ║
    ║  │         │                               │        ║
    ║  │    x = x + x_residual     ◄─ Residual   │        ║
    ║  └────────────────────────────────────────┘        ║
    ╚════════════════════════════════════════════════════╝
             │
             ▼
      ┌──────────────┐
      │ Linear (lm_head)│──► project to vocab_size logits
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │   Softmax     │──► probabilities over next token
      └──────┬───────┘
             │
             ▼
      Output: probability distribution over vocabulary
```

### Hyperparameter Summary

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `n_layer` | 1 | Number of transformer blocks |
| `n_embd` | 16 | Embedding dimension (width of the network) |
| `block_size` | 16 | Maximum context length (attention window) |
| `n_head` | 4 | Number of attention heads |
| `head_dim` | 4 | Dimension per head ( = n_embd / n_head) |
| `vocab_size` | 27 | 26 lowercase letters + 1 BOS token |

---

## 3. Code Walkthrough

### 3.1 Dataset & Tokenizer

```python
docs = [line.strip() for line in open('input.txt') if line.strip()]
random.shuffle(docs)
```

**What it does**: Downloads a file of ~32K human names. Each name is a "document."

```python
uchars = sorted(set(''.join(docs)))  # unique chars → ['a','b',...,'z']
BOS = len(uchars)                     # BOS token id = 26
vocab_size = len(uchars) + 1          # 27 total tokens
```

**Tokenizer**: This is a character-level tokenizer. Each unique character gets an integer ID (a=0, b=1, ..., z=25). A special **BOS** (Beginning of Sequence) token (id=26) marks the start and end of each name.

**Example**: The name "ada" → `[26, 0, 3, 0, 26]` (BOS, a, d, a, BOS)

**Why BOS at both ends?** The leading BOS tells the model "a new name starts here." The trailing BOS tells the model "the name ends here." During generation, producing BOS means "stop."

---

### 3.2 Automatic Differentiation (Autograd)

This is the **heart** of the training machinery — a scalar-level autograd engine.

```python
class Value:
    __slots__ = ('data', 'grad', '_children', '_local_grads')
```

Each `Value` object stores:
- **`data`**: The scalar numerical value (forward pass result)
- **`grad`**: The gradient of the final loss with respect to this value (filled during backward pass)
- **`_children`**: Parent nodes in the computation graph
- **`_local_grads`**: The local partial derivatives (how this node's output changes w.r.t. each child)

#### Supported Operations and Their Derivatives

| Operation | Forward: `f(a, b)` | Local Grad w.r.t. `a` | Local Grad w.r.t. `b` |
|-----------|--------------------|-----------------------|-----------------------|
| `a + b` | `a.data + b.data` | `1` | `1` |
| `a * b` | `a.data * b.data` | `b.data` | `a.data` |
| `a ** n` | `a.data ** n` | `n * a.data^(n-1)` | — (n is constant) |
| `log(a)` | `ln(a.data)` | `1 / a.data` | — |
| `exp(a)` | `e^(a.data)` | `e^(a.data)` | — |
| `relu(a)` | `max(0, a.data)` | `1 if a.data > 0 else 0` | — |

#### Backward Pass (Backpropagation)

```python
def backward(self):
    topo = []
    visited = set()
    def build_topo(v):      # Topological sort of the computation graph
        if v not in visited:
            visited.add(v)
            for child in v._children:
                build_topo(child)
            topo.append(v)
    build_topo(self)
    self.grad = 1           # d(loss)/d(loss) = 1
    for v in reversed(topo):
        for child, local_grad in zip(v._children, v._local_grads):
            child.grad += local_grad * v.grad   # Chain rule!
```

**Algorithm**:
1. Build a **topological ordering** of the computation graph (children before parents)
2. Set the gradient of the loss node to 1
3. Walk backwards: for each node, propagate gradients to children using the **chain rule**

**The Chain Rule in action**: If `loss = f(g(x))`, then:

$$\frac{\partial \text{loss}}{\partial x} = \frac{\partial \text{loss}}{\partial g} \cdot \frac{\partial g}{\partial x}$$

In code: `child.grad += local_grad * v.grad` — the local gradient times the upstream gradient.

---

### 3.3 Model Parameters Initialization

```python
matrix = lambda nout, nin, std=0.08: [[Value(random.gauss(0, std)) for _ in range(nin)] for _ in range(nout)]
```

All weight matrices are initialized with **small random Gaussian values** (mean=0, std=0.08). This is crucial — starting too large causes exploding gradients, starting at zero gives symmetry problems.

**State dictionary** (all learnable parameters):

| Parameter | Shape | Purpose |
|-----------|-------|---------|
| `wte` | (27, 16) | Token embedding matrix |
| `wpe` | (16, 16) | Position embedding matrix |
| `lm_head` | (27, 16) | Final projection to vocab logits |
| `attn_wq` | (16, 16) | Query projection |
| `attn_wk` | (16, 16) | Key projection |
| `attn_wv` | (16, 16) | Value projection |
| `attn_wo` | (16, 16) | Output projection |
| `mlp_fc1` | (64, 16) | MLP expand (16 → 64, 4× expansion) |
| `mlp_fc2` | (16, 64) | MLP contract (64 → 16) |

**Total parameters**: All flattened into a single list for the optimizer.

---

### 3.4 Model Architecture (The GPT Forward Pass)

#### Helper Functions

**`linear(x, w)`** — Matrix-vector multiplication:
```python
def linear(x, w):
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]
```
For a weight matrix $W$ of shape $(n_{out}, n_{in})$ and input vector $x$ of length $n_{in}$:

$$y_j = \sum_{i=0}^{n_{in}-1} W_{j,i} \cdot x_i$$

**`softmax(logits)`** — Converts raw scores to probabilities:
```python
def softmax(logits):
    max_val = max(val.data for val in logits)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]
```

$$\text{softmax}(z_i) = \frac{e^{z_i - z_{max}}}{\sum_j e^{z_j - z_{max}}}$$

Subtracting `max_val` is for **numerical stability** (prevents overflow in `exp`).

**`rmsnorm(x)`** — Root Mean Square Layer Normalization:
```python
def rmsnorm(x):
    ms = sum(xi * xi for xi in x) / len(x)
    scale = (ms + 1e-5) ** -0.5
    return [xi * scale for xi in x]
```

$$\text{RMSNorm}(x_i) = \frac{x_i}{\sqrt{\frac{1}{n}\sum_{j=1}^{n} x_j^2 + \epsilon}}$$

This normalizes the vector to have a roughly unit RMS (root mean square), stabilizing training. The $\epsilon = 10^{-5}$ prevents division by zero.

#### The `gpt()` Function — Main Forward Pass

**Step 1: Embedding Lookup**
```python
tok_emb = state_dict['wte'][token_id]   # shape: (n_embd,)
pos_emb = state_dict['wpe'][pos_id]     # shape: (n_embd,)
x = [t + p for t, p in zip(tok_emb, pos_emb)]
x = rmsnorm(x)
```

The input token and its position are each mapped to a 16-dimensional vector, then added. This gives the model both **what** the token is and **where** it appears.

**Step 2: Multi-Head Causal Self-Attention**

```python
q = linear(x, state_dict[f'layer{li}.attn_wq'])  # Query
k = linear(x, state_dict[f'layer{li}.attn_wk'])  # Key
v = linear(x, state_dict[f'layer{li}.attn_wv'])  # Value
keys[li].append(k)
values[li].append(v)
```

For each **head** $h$ (of 4 total):
1. Slice Q, K, V into head-sized chunks (4 dimensions each)
2. Compute attention scores: $\text{score}(t) = \frac{Q_h \cdot K_h^{(t)}}{\sqrt{d_k}}$
3. Apply softmax to get attention weights
4. Weighted sum of values: $\text{out}_j = \sum_t \alpha_t \cdot V_h^{(t)}_j$

The **KV cache** (`keys[li].append(k)`) stores all previous keys and values. This is how the model "remembers" earlier tokens — it can attend to all previous positions, making this **causal** (autoregressive) attention.

**Step 3: MLP (Feed-Forward) Block**
```python
x = linear(x, state_dict[f'layer{li}.mlp_fc1'])  # expand: 16 → 64
x = [xi.relu() for xi in x]                        # non-linearity
x = linear(x, state_dict[f'layer{li}.mlp_fc2'])  # contract: 64 → 16
```

The MLP first expands the representation to 4× the size, applies ReLU non-linearity, then projects back. This gives the model capacity to learn complex non-linear transformations.

Both attention and MLP blocks use **residual connections**: `x = x_attn + x_residual`. This helps gradient flow and enables deeper networks.

**Step 4: Final Projection**
```python
logits = linear(x, state_dict['lm_head'])  # shape: (vocab_size,)
```

Projects the final hidden state to vocab_size logits — one score per possible next token.

---

### 3.5 Training Loop

```python
for step in range(num_steps):
    # Tokenize one name
    doc = docs[step % len(docs)]
    tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
```

For each training step:

1. **Forward Pass**: Process each token position sequentially, compute logits, then compute **cross-entropy loss**:

```python
probs = softmax(logits)
loss_t = -probs[target_id].log()
```

$$\mathcal{L}_t = -\log P(\text{target}_t)$$

This is the **negative log-likelihood** — it measures how far the model's predicted probability for the correct next token is from 1.0. If the model is confident and correct, loss is low.

2. **Average loss** over all positions in the sequence:

$$\mathcal{L} = \frac{1}{n} \sum_{t=1}^{n} \mathcal{L}_t$$

3. **Backward Pass**: `loss.backward()` propagates gradients through the entire computation graph.

4. **Adam Optimizer Update**:

```python
lr_t = learning_rate * (1 - step / num_steps)    # linear LR decay
m[i] = β₁ * m[i] + (1 - β₁) * grad              # 1st moment (mean)
v[i] = β₂ * v[i] + (1 - β₂) * grad²             # 2nd moment (variance)
m̂ = m[i] / (1 - β₁^(step+1))                    # bias correction
v̂ = v[i] / (1 - β₂^(step+1))                    # bias correction
p.data -= lr_t * m̂ / (√v̂ + ε)                   # parameter update
p.grad = 0                                         # zero gradients
```

---

### 3.6 Inference (Text Generation)

```python
temperature = 0.5
logits = gpt(token_id, pos_id, keys, values)
probs = softmax([l / temperature for l in logits])
token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
```

1. Start with BOS token
2. Run the model forward to get logits
3. Divide logits by **temperature** (0.5 makes the distribution sharper / more confident)
4. Sample from the resulting probability distribution
5. Repeat until BOS is produced (end of name) or max length reached

---

## 4. Mathematics Deep Dive

### 4.1 Chain Rule & Backpropagation

**The Foundation**: If $y = f(g(x))$, then:

$$\frac{dy}{dx} = \frac{dy}{dg} \cdot \frac{dg}{dx}$$

For a computation graph with many nodes, backpropagation efficiently computes all gradients in a single backward pass by applying the chain rule at each node.

**Multivariate chain rule**: If a variable $x$ contributes to the loss through multiple paths, gradients are **summed** (that's why the code uses `+=`):

$$\frac{\partial L}{\partial x} = \sum_{\text{paths}} \frac{\partial L}{\partial y_i} \cdot \frac{\partial y_i}{\partial x}$$

**Each operation's local derivative**:

| Forward | Derivative w.r.t. input(s) |
|---------|-|
| $y = a + b$ | $\frac{\partial y}{\partial a} = 1, \quad \frac{\partial y}{\partial b} = 1$ |
| $y = a \cdot b$ | $\frac{\partial y}{\partial a} = b, \quad \frac{\partial y}{\partial b} = a$ |
| $y = a^n$ | $\frac{\partial y}{\partial a} = n \cdot a^{n-1}$ |
| $y = \ln(a)$ | $\frac{\partial y}{\partial a} = \frac{1}{a}$ |
| $y = e^a$ | $\frac{\partial y}{\partial a} = e^a$ |
| $y = \text{ReLU}(a)$ | $\frac{\partial y}{\partial a} = \begin{cases} 1 & \text{if } a > 0 \\ 0 & \text{otherwise}\end{cases}$ |

---

### 4.2 Linear Transformation

A linear transformation is a **matrix-vector multiplication** (no bias in this implementation):

$$\mathbf{y} = W\mathbf{x}$$

Where $W \in \mathbb{R}^{m \times n}$, $\mathbf{x} \in \mathbb{R}^n$, $\mathbf{y} \in \mathbb{R}^m$.

Each output is a **dot product**:

$$y_j = \sum_{i=1}^{n} W_{j,i} \cdot x_i = \mathbf{w}_j^T \mathbf{x}$$

**Why it matters**: Linear layers are the basic building block. Every projection (Q, K, V, output, MLP layers) is a linear transformation.

**Gradient**: If $\frac{\partial L}{\partial \mathbf{y}}$ is known, then:

$$\frac{\partial L}{\partial x_i} = \sum_j W_{j,i} \cdot \frac{\partial L}{\partial y_j}, \qquad \frac{\partial L}{\partial W_{j,i}} = x_i \cdot \frac{\partial L}{\partial y_j}$$

---

### 4.3 Softmax Function

Softmax converts a vector of raw scores (logits) into a probability distribution:

$$\sigma(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}$$

**Properties**:
- All outputs are in $(0, 1)$
- Outputs sum to 1
- Larger logits → higher probability
- **Shift invariance**: $\sigma(z_i - c) = \sigma(z_i)$ for any constant $c$ (used for numerical stability)

**Why subtract max?** Computing $e^{z_i}$ can overflow for large $z_i$. Subtracting the maximum value keeps the largest exponent at $e^0 = 1$.

---

### 4.4 RMSNorm (Root Mean Square Normalization)

$$\text{RMSNorm}(\mathbf{x})_i = \frac{x_i}{\text{RMS}(\mathbf{x})} = \frac{x_i}{\sqrt{\frac{1}{n}\sum_{j=1}^{n} x_j^2 + \epsilon}}$$

**Why normalize?** During training, activations can grow or shrink dramatically across layers. Normalization keeps values in a stable range, preventing:
- Vanishing gradients (values → 0)
- Exploding gradients (values → very large)

**RMSNorm vs LayerNorm**:
- **LayerNorm**: subtracts mean, divides by standard deviation, has learned scale/shift
- **RMSNorm**: only divides by RMS (no mean subtraction, no learned parameters here)
- RMSNorm is simpler and nearly as effective — chosen here for minimality

---

### 4.5 Scaled Dot-Product Attention

For a single head, the attention score between the current query and the key at position $t$ is:

$$\text{score}(t) = \frac{\mathbf{q} \cdot \mathbf{k}^{(t)}}{\sqrt{d_k}}$$

Where $d_k$ is the head dimension (4 in this code).

**Why scale by $\sqrt{d_k}$?** The dot product $\mathbf{q} \cdot \mathbf{k}$ grows proportionally with dimension $d_k$. If we have $d_k$ terms, each ~ $\mathcal{N}(0, 1)$, the sum has variance $\approx d_k$. Dividing by $\sqrt{d_k}$ normalizes the variance back to 1, keeping softmax inputs in a reasonable range.

After softmax, the attention weights are:

$$\alpha_t = \frac{e^{\text{score}(t)}}{\sum_{t'} e^{\text{score}(t')}}$$

The output is a weighted sum of values:

$$\text{head\_out}_j = \sum_t \alpha_t \cdot V^{(t)}_j$$

**Intuition**: Attention is a **soft lookup**. The query says "I'm looking for X." Each key says "I have Y." The dot product measures compatibility. The value is "what I contribute if selected."

---

### 4.6 Multi-Head Attention

Instead of one attention with $d_{model}$ dimensions, we use $h$ heads, each operating on $d_k = d_{model} / h$ dimensions:

$$\text{MultiHead}(Q, K, V) = W_O \cdot \text{Concat}(\text{head}_1, \text{head}_2, \ldots, \text{head}_h)$$

**Why multiple heads?** Each head can learn to attend to different types of information:
- Head 1 might learn to focus on the previous character
- Head 2 might learn to focus on vowel patterns
- Head 3 might learn positional patterns
- etc.

In this code: 4 heads × 4 dimensions each = 16 total dimensions.

---

### 4.7 Cross-Entropy Loss

The loss for a single prediction is:

$$\mathcal{L} = -\log P(\text{correct token})$$

If the model assigns probability $p$ to the correct next token:
- $p → 1.0$: $\mathcal{L} = -\log(1) = 0$ (perfect prediction)
- $p → 0.5$: $\mathcal{L} = -\log(0.5) = 0.693$ (coin flip)
- $p → 0.01$: $\mathcal{L} = -\log(0.01) = 4.605$ (very wrong)

Averaged over the sequence of length $n$:

$$\mathcal{L}_{\text{avg}} = \frac{1}{n}\sum_{t=1}^{n} -\log P(\text{target}_t | \text{context}_{<t})$$

**Relationship to information theory**: This is equivalent to measuring the number of **bits** (actually nats, since we use $\ln$) needed to encode the target under the model's distribution. Lower = better.

---

### 4.8 Adam Optimizer

Adam (Adaptive Moment Estimation) maintains two running averages for each parameter:

**First moment** (exponential moving average of gradients — estimates the mean):

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$

**Second moment** (exponential moving average of squared gradients — estimates the variance):

$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$

**Bias correction** (since $m$ and $v$ are initialized at 0, they're biased toward 0 early on):

$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$

**Parameter update**:

$$\theta_t = \theta_{t-1} - \eta_t \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

Where:
- $\eta_t = \eta_0 \cdot (1 - t/T)$ is the linearly decayed learning rate
- $\beta_1 = 0.85$ (momentum decay, typically 0.9)
- $\beta_2 = 0.99$ (variance decay, typically 0.999)
- $\epsilon = 10^{-8}$ (prevents division by zero)

**Intuition**: 
- The first moment gives **momentum** — if gradients consistently point one direction, keep going
- The second moment provides **adaptive learning rates** — parameters with large gradients get smaller updates
- Result: fast, stable convergence

---

### 4.9 Residual Connections

```python
x = [a + b for a, b in zip(x_processed, x_residual)]
```

$$\mathbf{x}_{\text{out}} = f(\mathbf{x}_{\text{in}}) + \mathbf{x}_{\text{in}}$$

**Why?** During backpropagation, the gradient flowing through a residual connection is:

$$\frac{\partial \mathcal{L}}{\partial \mathbf{x}_{in}} = \frac{\partial \mathcal{L}}{\partial \mathbf{x}_{out}} \cdot \left(\frac{\partial f}{\partial \mathbf{x}_{in}} + \mathbf{I}\right)$$

The $+\mathbf{I}$ (identity) term means gradients can flow directly through without being diminished. This is the key innovation from ResNets (2015) that enables training very deep networks.

---

### 4.10 Embeddings (Token & Positional)

**Token Embedding**: A lookup table $E \in \mathbb{R}^{V \times d}$ where row $i$ is the learned vector representation of token $i$.

$$\mathbf{e}_{\text{tok}} = E[\text{token\_id}]$$

**Positional Embedding**: A lookup table $P \in \mathbb{R}^{T \times d}$ where row $j$ is the learned vector for position $j$.

$$\mathbf{e}_{\text{pos}} = P[\text{pos\_id}]$$

**Combined**:

$$\mathbf{x}_0 = \mathbf{e}_{\text{tok}} + \mathbf{e}_{\text{pos}}$$

The addition means the model must learn to disentangle "what" from "where." This is a **learned** positional embedding (as opposed to sinusoidal fixed encodings in the original Transformer paper).

---

### 4.11 Temperature Scaling

During inference, logits are divided by temperature $\tau \in (0, 1]$:

$$P(i) = \frac{e^{z_i / \tau}}{\sum_j e^{z_j / \tau}}$$

| Temperature | Effect |
|-------------|--------|
| $\tau \to 0^+$ | Argmax (deterministic, always pick highest probability) |
| $\tau = 0.5$ | Sharper distribution (more confident, less random) |
| $\tau = 1.0$ | Original model distribution |
| $\tau > 1.0$ | Flatter distribution (more random, more "creative") |

**Math**: Dividing by a small $\tau$ amplifies the differences between logits, making the softmax more peaked. Dividing by a large $\tau$ compresses differences, making the distribution more uniform.

---

## 5. How All the Pieces Fit Together

Here's the complete **data flow** for training on the name "ada":

```
Tokens: [BOS=26, a=0, d=3, a=0, BOS=26]

Step 1: Input=BOS(26), Target=a(0)
  ├── Embed token 26 → 16-dim vector
  ├── Embed position 0 → 16-dim vector
  ├── Add them → x (16-dim)
  ├── RMSNorm → x
  ├── Attention: Q, K, V from x. Only 1 position to attend to.
  ├── MLP: expand to 64-dim → ReLU → project back to 16-dim
  ├── lm_head: project to 27 logits
  ├── Softmax → 27 probabilities
  └── Loss = -log(prob[0])    ← how well did we predict 'a'?

Step 2: Input=a(0), Target=d(3)
  ├── Embed token 0 → 16-dim vector
  ├── Embed position 1 → 16-dim vector
  ├── Add them → x (16-dim)
  ├── Attention: can now attend to position 0 AND position 1
  │   (uses cached keys/values from step 1)
  ├── MLP ...
  ├── lm_head → 27 logits
  └── Loss = -log(prob[3])    ← how well did we predict 'd'?

Step 3: Input=d(3), Target=a(0)    ...same pattern
Step 4: Input=a(0), Target=BOS(26) ...predicts end of name

Final Loss = average of all 4 position losses
Backward: compute gradients for ALL parameters
Adam: update ALL parameters slightly to reduce this loss
```

Over 1000 training steps with 1000 different names, the model gradually learns patterns like:
- After 'a', 'd' is somewhat likely
- Names often end after 3-6 characters
- Certain character combinations are common in English names

---

## 6. Learning Path — Mathematics Prerequisites

### Level 1: Foundations (Start Here)

| Topic | Why You Need It | Recommended Time |
|-------|----------------|------------------|
| **Basic Calculus** — derivatives, chain rule, partial derivatives | Backpropagation IS the chain rule | 2-3 weeks |
| **Linear Algebra Basics** — vectors, matrices, dot products, matrix multiplication | Every layer is a matrix operation | 2-3 weeks |
| **Probability & Statistics** — probability distributions, Bayes' rule, expectation, variance | Softmax, loss functions, sampling | 1-2 weeks |

**Key formulas to master**:
- $\frac{d}{dx} e^x = e^x$, $\frac{d}{dx} \ln x = \frac{1}{x}$, $\frac{d}{dx} x^n = nx^{n-1}$
- Chain rule: $\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}$
- $\mathbf{y} = W\mathbf{x}$ where $y_i = \sum_j W_{ij} x_j$
- $P(x) = \frac{e^{z_x}}{\sum_k e^{z_k}}$ (softmax)

### Level 2: Intermediate

| Topic | Why You Need It |
|-------|----------------|
| **Multivariable Calculus** — Jacobians, vector-valued function derivatives | Understanding gradients of vectors and matrices |
| **Optimization** — gradient descent, convexity, learning rates | Adam and training dynamics |
| **Information Theory** — entropy, cross-entropy, KL divergence | Understanding loss functions deeply |

### Level 3: Advanced (For Deeper Understanding)

| Topic | Why You Need It |
|-------|----------------|
| **Numerical Linear Algebra** — matrix decompositions, numerical stability | Why RMSNorm works, why we subtract max in softmax |
| **Stochastic Optimization** — Adam, AdamW, convergence theory | Understanding optimizer behavior |
| **Attention as Kernel Methods** — softmax attention = soft dictionary lookup | Theoretical foundations of attention |

### Suggested Study Order

```
Week 1-2:  Derivatives & Chain Rule → implement from scratch
Week 3-4:  Vectors, Matrices, Dot Products → implement from scratch
Week 5:    Probability: softmax, log-likelihood
Week 6:    Put it all together: re-derive every gradient in this code by hand
Week 7-8:  Code a micrograd engine from scratch (value, forward, backward)
Week 9-10: Add the GPT architecture on top
Week 11+:  Experiment: change hyperparameters, add layers, try new datasets
```

---

## 7. Recommended Resources

### Books
| Resource | Level | Focus |
|----------|-------|-------|
| *3Blue1Brown — Essence of Linear Algebra* (YouTube) | Beginner | Beautiful visual intuition for vectors/matrices |
| *3Blue1Brown — Essence of Calculus* (YouTube) | Beginner | Visual understanding of derivatives |
| *3Blue1Brown — Neural Networks* (YouTube) | Beginner | Backpropagation explained visually |
| *Mathematics for Machine Learning* (Deisenroth et al.) | Intermediate | Comprehensive math for ML — free PDF online |
| *Deep Learning* (Goodfellow, Bengio, Courville) | Advanced | The "bible" of deep learning theory |
| *Pattern Recognition and Machine Learning* (Bishop) | Advanced | Rigorous probabilistic ML |

### Karpathy's Own Materials (Highly Recommended)
| Resource | Description |
|----------|-------------|
| [micrograd](https://github.com/karpathy/micrograd) | Autograd engine (the `Value` class expanded) |
| [makemore](https://github.com/karpathy/makemore) | Character-level language models, progressively more complex |
| [nanoGPT](https://github.com/karpathy/nanoGPT) | Full GPT training in PyTorch |
| [Neural Networks: Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) | YouTube series building everything from scratch |
| [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) | 2-hour video building GPT from scratch |

### Online Courses
| Course | Platform |
|--------|----------|
| Stanford CS231n — CNNs for Visual Recognition | YouTube (backprop lectures are gold) |
| Stanford CS224n — NLP with Deep Learning | YouTube (transformer/attention lectures) |
| fast.ai — Practical Deep Learning | free online (code-first approach) |

### Papers
| Paper | Why Read It |
|-------|-------------|
| *Attention Is All You Need* (Vaswani et al., 2017) | The original Transformer paper |
| *Language Models are Unsupervised Multitask Learners* (GPT-2, Radford et al., 2019) | The architecture this code follows |
| *Adam: A Method for Stochastic Optimization* (Kingma & Ba, 2014) | The optimizer used here |
| *Root Mean Square Layer Normalization* (Zhang & Sennrich, 2019) | RMSNorm paper |

---

## 8. Exercises to Solidify Understanding

### Exercise Set 1: Autograd
1. **By hand**: Compute the gradient of $f(x) = (x^2 + 3x).log()$ at $x = 2$ using the chain rule. Verify with the `Value` class.
2. **Extend**: Add `tanh()` to the `Value` class. What is the local gradient? ($\text{tanh}'(x) = 1 - \text{tanh}^2(x)$)
3. **Debug**: Why does the backward pass use `+=` for gradients? Construct a simple graph where a node has two paths to the loss and show that `=` would give wrong gradients.

### Exercise Set 2: Forward Pass
4. **Trace**: For the input token "a" at position 0, manually trace all dimensions through the forward pass and verify the output shape is `(27,)`.
5. **Modify**: Change `n_head` from 4 to 2. What changes in the code? What is the new `head_dim`?
6. **Experiment**: What happens if you remove RMSNorm? Train both versions and compare loss curves.

### Exercise Set 3: Training
7. **Plot**: Modify the training loop to record losses and plot the training curve. Does it converge?
8. **Ablation**: Remove residual connections. Can the model still train? How does the loss change?
9. **Hyperparameters**: Try `n_embd=32, n_head=8, n_layer=2`. Does the model generate better names?

### Exercise Set 4: Math Derivations
10. **Derive**: Starting from $L = -\log(\text{softmax}(z)_k)$, derive $\frac{\partial L}{\partial z_i}$ for all $i$.
    - Answer: $\frac{\partial L}{\partial z_i} = p_i - \mathbb{1}_{i=k}$ (softmax output minus one-hot target)
11. **Derive**: For $y = W x$, derive $\frac{\partial L}{\partial W}$ and $\frac{\partial L}{\partial x}$ given $\frac{\partial L}{\partial y}$.
12. **Derive**: Show that RMSNorm gradient involves both the direct scaling and a correction term from the norm itself.

### Exercise Set 5: Extensions
13. **Bigger model**: Scale up to `n_layer=4, n_embd=64, n_head=8, block_size=32` and train on a larger text corpus
14. **Add biases**: Modify the linear function to include bias terms: $y = Wx + b$
15. **Add LayerNorm**: Replace RMSNorm with full LayerNorm (subtract mean, divide by std, learn scale and shift)
16. **Add dropout**: Implement dropout for regularization during training

---

## Appendix: Complete Mathematical Notation Reference

| Symbol | Meaning |
|--------|---------|
| $x, \mathbf{x}$ | Scalar, vector |
| $W$ | Weight matrix |
| $d_k$ | Dimension of each attention head |
| $d_{model}$ | Model embedding dimension (`n_embd`) |
| $V$ | Vocabulary size |
| $T$ | Maximum sequence length (`block_size`) |
| $h$ | Number of attention heads |
| $L$ | Number of transformer layers |
| $\sigma(\cdot)$ | Softmax function |
| $\mathcal{L}$ | Loss function value |
| $\eta$ | Learning rate |
| $\beta_1, \beta_2$ | Adam momentum coefficients |
| $\epsilon$ | Small constant for numerical stability |
| $\tau$ | Temperature for sampling |
| $\nabla_\theta \mathcal{L}$ | Gradient of loss w.r.t. parameters |
| $\odot$ | Element-wise multiplication |

---

*This guide prepared as a starting point for deep-diving into Transformers and language models. The single most important thing: **implement everything from scratch**. Reading is not enough — the math clicks when you compute gradients by hand and debug why your values don't match.*

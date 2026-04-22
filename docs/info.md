<!---
Generated for: Binary Neural Network Inference Engine
Author: HIMANSHU PAL
-->

## How it works

This project implements a fully combinational Binary Neural Network (BNN) inference engine on silicon. It classifies a 6-bit input feature vector into one of two output classes using a 2-layer architecture.

**Layer 1 — Hidden Layer (4 neurons, 6-bit inputs):**  
Each neuron computes XNOR between the 6-bit input and a fixed 6-bit weight vector. The XNOR output replaces multiplication — a match (1) represents +1 and a mismatch (0) represents -1. A popcount then sums the matches, and a threshold of ≥ 3 activates the neuron.

**Layer 2 — Output Layer (2 neurons, 4-bit inputs):**  
The 4 hidden neuron outputs are fed into two output neurons using the same XNOR + popcount approach, with a threshold of ≥ 2. Each output neuron represents one class.

**Confidence:**  
The LSB of the popcount for each output neuron is exposed as a confidence indicator on `uo[2]` and `uo[3]`.

**Debug:**  
The hidden layer outputs are mirrored on `uo[7:4]` for observability.

## How to test

1. Apply a 6-bit input pattern on `ui[5:0]` (leave `ui[7:6]` as 0).
2. Read the output immediately — the design is fully combinational, no clock needed.
3. Check `uo[0]` for Class 0 and `uo[1]` for Class 1.
4. A high output on `uo[0]` means the input is classified as Class 0; high on `uo[1]` means Class 1.
5. `uo[2]` and `uo[3]` give the confidence LSB for each class.
6. `uo[7:4]` shows the hidden neuron activations for debugging.

**Example inputs to try:**

| Input (`ui[5:0]`) | Expected Class |
|---|---|
| `101011` | Class 0 (`uo[0]` = 1) |
| `110001` | Class 0 (`uo[0]` = 1) |
| `011010` | Class 1 (`uo[1]` = 1) |

## External hardware

No external hardware required. The design is fully self-contained and combinational.

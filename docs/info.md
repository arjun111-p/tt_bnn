<!---
This file is used to generate your project datasheet. Please fill in the information below and delete any unused sections.
You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project is a fully combinational Binary Neural Network (BNN) inference engine implemented in Verilog. It classifies a 6-bit  input feature vector into one of two output classes using a two-layer architecture with fixed binary weights.

**Layer 1 — Hidden Layer (4 neurons):** Each neuron receives the full 6-bit input and computes an XNOR operation with a fixed 6-bit weight vector. XNOR replaces multiplication — a matching bit contributes +1, a mismatching bit contributes -1. A popcount then tallies the number of matches, and a threshold of 3 or more activates the neuron output to 1.

**Layer 2 — Output Layer (2 neurons):** The four hidden neuron outputs form a 4-bit vector that feeds into two output neurons using the same XNOR and popcount approach, with a threshold of 2 or more. Each output neuron represents one class.

**Confidence:** The LSB of each output neuron's popcount is exposed on bits 2 and 3 of the output bus as a simple confidence indicator.

**Debug visibility:** The raw hidden layer outputs are mirrored on output bits 7 to 4, making it easy to inspect internal activations during testing.

## How to test

The design is fully combinational — no clock or reset is needed for normal operation. To test it, apply a 6-bit pattern on `ui[5:0]` (leave `ui[7:6]` as 0), then immediately read the output from `uo_out`.

- `uo[0]` = 1 means the input is classified as Class 0
- `uo[1]` = 1 means the input is classified as Class 1
- `uo[2]` = confidence LSB for Class 0
- `uo[3]` = confidence LSB for Class 1
- `uo[7:4]` = hidden neuron activation values (for debugging)

Example inputs to try:

| `ui[5:0]` (binary) | Decimal | Expected result |
|---|---|---|
| `101011` | 43 | Class 0 active (`uo[0]` = 1) |
| `110001` | 49 | Class 0 active (`uo[0]` = 1) |
| `011010` | 26 | Class 1 active (`uo[1]` = 1) |

## External hardware

No external hardware is required. The design is self-contained and fully combinational.

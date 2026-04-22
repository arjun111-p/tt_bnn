import cocotb
from cocotb.triggers import Timer

# -------------------------------------------------------
# Python mirror of the BNN hardware logic
# -------------------------------------------------------

def bnn_neuron6(x, w):
    """XNOR + popcount + threshold>=3"""
    xnor = (~(x ^ w)) & 0x3F
    return 1 if bin(xnor).count('1') >= 3 else 0

def bnn_neuron4(x, w):
    """XNOR + popcount + threshold>=2"""
    xnor = (~(x ^ w)) & 0xF
    return 1 if bin(xnor).count('1') >= 2 else 0

def compute_expected(ui_in):
    """Compute expected uo_out[7:0] for a given 6-bit input"""
    x = ui_in & 0x3F

    # Layer 1 weights (matches project.v exactly)
    W1 = [0b101011, 0b110001, 0b011010, 0b111100]
    h = [bnn_neuron6(x, w) for w in W1]

    # hidden = {h3, h2, h1, h0}
    hidden = (h[3] << 3) | (h[2] << 2) | (h[1] << 1) | h[0]

    # Layer 2 weights
    W2_0 = 0b1011
    W2_1 = 0b0110

    o0 = bnn_neuron4(hidden, W2_0)
    o1 = bnn_neuron4(hidden, W2_1)

    # Confidence: LSB of popcount
    pop_o0 = bin((~(hidden ^ W2_0)) & 0xF).count('1')
    pop_o1 = bin((~(hidden ^ W2_1)) & 0xF).count('1')

    # Build uo_out exactly as project.v does
    uo = 0
    uo |= (o0)              # bit 0: class 0
    uo |= (o1 << 1)         # bit 1: class 1
    uo |= ((pop_o0 & 1) << 2)  # bit 2: confidence class 0 LSB
    uo |= ((pop_o1 & 1) << 3)  # bit 3: confidence class 1 LSB
    uo |= (hidden << 4)     # bits 7:4: hidden layer debug

    return uo & 0xFF

# ---

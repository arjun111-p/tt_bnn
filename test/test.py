# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

# -------------------------------------------------------
# Python mirror of BNN hardware logic
# These MUST be defined BEFORE the test function
# -------------------------------------------------------

def bnn_neuron6(x, w):
    """XNOR + popcount, threshold >= 3"""
    xnor = (~(x ^ w)) & 0x3F
    return 1 if bin(xnor).count('1') >= 3 else 0

def bnn_neuron4(x, w):
    """XNOR + popcount, threshold >= 2"""
    xnor = (~(x ^ w)) & 0xF
    return 1 if bin(xnor).count('1') >= 2 else 0

def compute_expected(ui_in):
    """Compute expected uo_out for a given 6-bit input, mirrors project.v exactly"""
    x = ui_in & 0x3F

    # Layer 1 weights — must exactly match project.v
    W1 = [0b101011, 0b110001, 0b011010, 0b111100]
    h = [bnn_neuron6(x, w) for w in W1]

    # hidden = {h3, h2, h1, h0}
    hidden = (h[3] << 3) | (h[2] << 2) | (h[1] << 1) | h[0]

    # Layer 2 weights — must exactly match project.v
    W2_0 = 0b1011
    W2_1 = 0b0110

    o0 = bnn_neuron4(hidden, W2_0)
    o1 = bnn_neuron4(hidden, W2_1)

    # Confidence LSB of popcount
    pop_o0 = bin((~(hidden ^ W2_0)) & 0xF).count('1')
    pop_o1 = bin((~(hidden ^ W2_1)) & 0xF).count('1')

    # Build expected uo_out — mirrors assign statements in project.v
    uo = 0
    uo |= (o0)                   # bit 0: class 0
    uo |= (o1 << 1)              # bit 1: class 1
    uo |= ((pop_o0 & 1) << 2)   # bit 2: confidence class 0 LSB
    uo |= ((pop_o1 & 1) << 3)   # bit 3: confidence class 1 LSB
    uo |= (hidden << 4)          # bits 7:4: hidden layer debug

    return uo & 0xFF

# -------------------------------------------------------
# Cocotb test — MUST be a standalone async function
# -------------------------------------------------------

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Start clock (10 us period = 100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 2)

    dut._log.info("Testing all 64 input combinations")

    # Test all 64 valid 6-bit inputs
    for i in range(64):
        dut.ui_in.value  = i
        dut.uio_in.value = 0

        # Combinational design — just wait for signals to settle
        await Timer(10, units="ns")

        expected = compute_expected(i)
        actual   = int(dut.uo_out.value)

        assert actual == expected, (
            f"FAIL input={i:06b} ({i}): "
            f"expected uo_out={expected:#010b} ({expected}), "
            f"got {actual:#010b} ({actual})"
        )
        dut._log.info(f"PASS input={i:06b} → uo_out={actual:#010b}")

    dut._log.info("All 64 inputs passed ✓")

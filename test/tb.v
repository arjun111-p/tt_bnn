`default_nettype none

// ============================================================
// Popcount4
// ============================================================
module popcount4 (
    input  [3:0] in,
    output [2:0] count
);
    assign count = in[0] + in[1] + in[2] + in[3];
endmodule

// ============================================================
// 4-bit BNN Neuron (output layer, threshold=2)
// ============================================================
module bnn_neuron4 (
    input  [3:0] x,
    input  [3:0] w,
    output out
);
    wire [3:0] xnor_out;
    assign xnor_out = ~(x ^ w);

    wire [2:0] count;
    assign count = xnor_out[0] + xnor_out[1] + xnor_out[2] + xnor_out[3];

    assign out = (count >= 2);
endmodule

// ============================================================
// 6-bit BNN Neuron (hidden layer, threshold=3)
// ============================================================
module bnn_neuron6 (
    input  [5:0] x,
    input  [5:0] w,
    output out
);
    wire [5:0] xnor_out;
    assign xnor_out = ~(x ^ w);

    wire [2:0] count;
    assign count = xnor_out[0] + xnor_out[1] + xnor_out[2] +
                   xnor_out[3] + xnor_out[4] + xnor_out[5];

    assign out = (count >= 3);
endmodule

// ============================================================
// TinyTapeout Top Module — MUST be named tt_um_*
// MUST have ALL 8 standard TinyTapeout ports
// ============================================================
module tt_um_bnn_himanshu (
    input  wire [7:0] ui_in,    // Dedicated inputs  (only [5:0] used)
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path   (unused)
    output wire [7:0] uio_out,  // IOs: Output path  (tied to 0)
    output wire [7:0] uio_oe,   // IOs: Enable path  (tied to 0 = all inputs)
    input  wire       ena,      // Always 1 — ignore
    input  wire       clk,      // Clock             (unused, combinational)
    input  wire       rst_n     // Reset             (unused, combinational)
);

    // Tie off unused bidirectional pins
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // --------------------------------------------------------
    // Hidden layer weights
    // --------------------------------------------------------
    wire [5:0] W1_0 = 6'b101011;
    wire [5:0] W1_1 = 6'b110001;
    wire [5:0] W1_2 = 6'b011010;
    wire [5:0] W1_3 = 6'b111100;

    // --------------------------------------------------------
    // Hidden layer neurons
    // --------------------------------------------------------
    wire h0, h1, h2, h3;
    bnn_neuron6 H0 (.x(ui_in[5:0]), .w(W1_0), .out(h0));
    bnn_neuron6 H1 (.x(ui_in[5:0]), .w(W1_1), .out(h1));
    bnn_neuron6 H2 (.x(ui_in[5:0]), .w(W1_2), .out(h2));
    bnn_neuron6 H3 (.x(ui_in[5:0]), .w(W1_3), .out(h3));

    wire [3:0] hidden = {h3, h2, h1, h0};

    // --------------------------------------------------------
    // Output layer weights
    // --------------------------------------------------------
    wire [3:0] W2_0 = 4'b1011;
    wire [3:0] W2_1 = 4'b0110;

    // --------------------------------------------------------
    // Output neurons
    // --------------------------------------------------------
    wire o0, o1;
    bnn_neuron4 O0 (.x(hidden), .w(W2_0), .out(o0));
    bnn_neuron4 O1 (.x(hidden), .w(W2_1), .out(o1));

    // --------------------------------------------------------
    // Confidence (popcount)
    // --------------------------------------------------------
    wire [2:0] pop_o0, pop_o1;
    popcount4 PC0 (.in(~(hidden ^ W2_0)), .count(pop_o0));
    popcount4 PC1 (.in(~(hidden ^ W2_1)), .count(pop_o1));

    // --------------------------------------------------------
    // Output mapping
    // --------------------------------------------------------
    assign uo_out[0] = o0;          // Class 0
    assign uo_out[1] = o1;          // Class 1
    assign uo_out[2] = pop_o0[0];   // Confidence bit (class 0)
    assign uo_out[3] = pop_o1[0];   // Confidence bit (class 1)
    assign uo_out[7:4] = hidden;    // Hidden layer (debug)

    // Suppress unused input warnings
    wire _unused = &{ena, clk, rst_n, ui_in[7:6], uio_in, 1'b0};

endmodule

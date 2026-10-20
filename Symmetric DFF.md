# Symmetric DFF
## 4.1.1 Circuit Schematic
### Figure 4.1 shows the schematic of the symmetric DFF-PUF. The circuit works as a normal D flip-flop in normal mode. In PUF mode, the extra balancing transistors make both sides of the slave latch equal.
<img width="903" height="358" alt="image" src="https://github.com/user-attachments/assets/f6ef4e28-e06d-426e-add3-2c1dfdb1dcb2" />
## Transient Behaviour
### The general waveform in Figure 4.2 shows the circuit working as a normal D flip-flop. The Qbar takes a weak 1 (around 1.5V) and later becomes strong 1 (1.8V) after CLK becomes 0 is because of the effect of nmos pass transistor M8. Figure 4.3 shows the metastable state. When CLK and PUF are both 1, the two output nodes are forced to the same voltage, and the latch enters the metastable state. Figure 4.4 shows the PUF behaviour. When CLK and PUF both go to 0, process variation decides which side wins, and the output Q settles to 0 or 1.
<img width="903" height="384" alt="image" src="https://github.com/user-attachments/assets/6255d576-7b25-40ec-b41a-3514a5c15ed5" />
<img width="903" height="403" alt="image" src="https://github.com/user-attachments/assets/ef87b1e0-83c9-4891-a4c4-13a2a464e1d6" />
<img width="903" height="406" alt="image" src="https://github.com/user-attachments/assets/e7475fb0-7717-4e30-b577-0c71eaa55c0e" />
<img width="903" height="397" alt="image" src="https://github.com/user-attachments/assets/b6cc4773-dae3-48ea-952d-c8a9e424668c" />
<img width="903" height="403" alt="image" src="https://github.com/user-attachments/assets/20d0700b-1257-4bdd-945a-2d0611be1dcc" />





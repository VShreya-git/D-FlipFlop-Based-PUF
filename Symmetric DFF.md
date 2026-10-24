# Symmetric DFF

## 4.1.1 Circuit Schematic

Figure 4.1 shows the schematic of the symmetric DFF-PUF. The circuit works as a normal D flip-flop in normal mode. In PUF mode, the extra balancing transistors make both sides of the slave latch equal.

<img width="903" height="358" alt="image" src="https://github.com/user-attachments/assets/f6ef4e28-e06d-426e-add3-2c1dfdb1dcb2" />

Figure 4.1: Schematic of the symmetric DFF-PUF

## Transient Behaviour

The general waveform in Figure 4.2 shows the circuit working as a normal D flip-flop. The Qbar takes a weak 1 (around 1.5V) and later becomes strong 1 (1.8V) after CLK becomes 0 is because of the effect of nmos pass transistor M8. Figure 4.3 shows the metastable state. When CLK and PUF are both 1, the two output nodes are forced to the same voltage, and the latch enters the metastable state. Figure 4.4 shows the PUF behaviour. When CLK and PUF both go to 0, process variation decides which side wins, and the output Q settles to 0 or 1.

<img width="903" height="384" alt="image" src="https://github.com/user-attachments/assets/6255d576-7b25-40ec-b41a-3514a5c15ed5" />

Figure 4.4: Transient Analysis of the symmetric DFF-PUF

<img width="903" height="397" alt="image" src="https://github.com/user-attachments/assets/b6cc4773-dae3-48ea-952d-c8a9e424668c" />

Figure 4.5: Monte Carlo output of the symmetric DFF-PUF 

<img width="903" height="403" alt="image" src="https://github.com/user-attachments/assets/20d0700b-1257-4bdd-945a-2d0611be1dcc" />

Figure 4.6: PVT simulation output of the symmetric DFF-PUF

<img width="306" height="166" alt="image" src="https://github.com/user-attachments/assets/30e944ed-6289-478d-b589-9fbdad4a6ba5" />

PUF metrics of the symmetric DFF-PUF for an 8-bit response

<img width="246" height="143" alt="image" src="https://github.com/user-attachments/assets/33008938-9e8b-4076-be60-1314b58f5da6" />



PUF metrics of the symmetric DFF-PUF for an 8-bit response

<img width="245" height="139" alt="image" src="https://github.com/user-attachments/assets/f3ff4d8e-fdd2-4324-8675-01cc42a535f4" />


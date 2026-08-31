# BB84
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer, AerSimulator
from qiskit import transpile

# classical channel
n_qubits = 20

# bits that Alice sends to Bob
alice_bits = []
for b in range (n_qubits):
    bit = random.randint(0,1) 
    alice_bits.append(bit)

# Alice's basis
alice_bases = []
for n in range (n_qubits):
    base = random.choice(['Z', 'X']) 
    alice_bases.append(base)

# Bob's measurement bases
bob_bases = []
for n in range (n_qubits):
    base = random.choice(['Z', 'X']) 
    bob_bases.append(base)

# quantum channel
backend = Aer.get_backend('qasm_simulator')

bob_results = []

eve_results = []

# Eve sneaks into the channel
Eve = input("Do you want to add an intruder Eve? ")
if Eve != 'yes' and Eve != 'no':
    print('ATTENTION! The only accepted answers are \'yes\' or \'no\'')
    Eve = input("Do you want to add an intruder Eve? ")

for i in range(n_qubits):

    qc = QuantumCircuit(1,1) # definition of the quantum channel having 1 bit and 1 qbit
    
    # Alice sends the qbits
    if alice_bases[i] == 'Z': # computational base
        if alice_bits[i] == 1:
            qc.x(0)
    else: # diagonal base
        if alice_bits[i] == 0:
            qc.h(0)
        else:
            qc.x(0)
            qc.h(0)

    # Eve is inside the quantum channel
    if Eve == 'yes': # Eve performs the same measurements as Bob 
        qc.measure(0,0) # Eve measures the qbit sends by Alice
        new_cirq = transpile(qc, backend) 
        job = backend.run(new_cirq) 
        counts = job.result().get_counts() 
        if len(list(counts.values())) == 2:
            if list(counts.values())[0] >= list(counts.values())[1]:
                measured_bit = int(list(counts.keys())[0])
            else:
                measured_bit = int(list(counts.keys())[1])
        else:
            measured_bit = int(list(counts.keys())[0])
        eve_results.append(measured_bit)
        # Eve sends a new qubit to Bob, pretending to be Alice
        eve_base = random.choice(['Z', 'X'])
        if eve_base == 'X': 
            if eve_results[i] == 0:            
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        else: 
            if eve_results[i] == 1:
                qc.x(0)

    # Bob performs the measurements
    if bob_bases[i] == 'X':
        qc.h(0)

    qc.measure(0,0)

    new_cirq = transpile(qc, backend) 
    job = backend.run(new_cirq) 

    counts = job.result().get_counts() 

    if len(list(counts.values())) == 2:
        if list(counts.values())[0] >= list(counts.values())[1]:
            measured_bit = int(list(counts.keys())[0])
        else:
            measured_bit = int(list(counts.keys())[1])
    else:
        measured_bit = int(list(counts.keys())[0])

    bob_results.append(measured_bit) 

# classical channel
# Alice and Bob compare the bases chosen for the measurements
shifted_key = [] 
alice_key = []
bob_key = []
for i in range(n_qubits):
  if alice_bases[i] == bob_bases[i]: 
    shifted_key.append(alice_bits[i]) 
    alice_key.append(alice_bits[i])
    bob_key.append(bob_results[i]) 
    print(f"Qubit {i}: Basis match ({alice_bases[i]}). Alice's bit: {alice_bits[i]}, Bob's measurement: {bob_results[i]}")
  else:
    print(f"Qubit {i}: Basis mismatch ({alice_bases[i]}). Alice's bit: {alice_bits[i]}, Bob's measurement: {bob_results[i]}")
  
print("\nFinal sifted key:", shifted_key) 

# Alice and Bob compare 40% (appropriately rounded) of the shared key bits to check for Eve's presence 
if len(shifted_key) % 5 < 3:
    num_bit = len(shifted_key) // 5 * 2 
else:
    num_bit = len(shifted_key) // 5 * 2 + 1 

wrong_bit = 0
for i in range(num_bit):
    if alice_key[i] != bob_key[i]:
        wrong_bit += 1

QBER = wrong_bit / num_bit
print("QBER is:", QBER)

# If at least one of the compared bits does not match, 
# the channel has been compromised and a new key exchange has to be performed
if QBER >= 0:
    print("WARNING: The channel has been compromised!")

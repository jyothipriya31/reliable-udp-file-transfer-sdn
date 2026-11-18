# Reliable UDP File Transfer using Software-Defined Networking (SDN)

## Project Overview

This project implements a reliable file transfer application using **UDP sockets integrated with Software-Defined Networking (SDN)**.

UDP provides fast communication but does not guarantee packet delivery, ordering or retransmission. To address these limitations, a reliability mechanism is implemented at the application layer using sequence numbers, acknowledgements (ACKs), timeouts and retransmissions.

The network is simulated using **Mininet**, while a **POX SDN controller** manages forwarding paths and responds to inter-switch link failures.

## Objectives

- Implement reliable file transfer using UDP sockets.
- Handle packet loss, duplicate packets and out-of-order delivery.
- Implement acknowledgements and timeout-based retransmissions.
- Integrate the socket application with an SDN-controlled network.
- Detect inter-switch link failures and switch to an alternate path.
- Verify file integrity using SHA-256 checksums.

## Technologies Used

- Python – Socket programming and reliability protocol
- UDP – Data transmission
- Mininet – Network topology emulation
- POX – SDN controller
- OpenFlow 1.0 – Communication between switches and controller
- Linux / Ubuntu – Development and execution environment

## Network Architecture

The project uses a diamond-shaped Mininet topology consisting of two hosts and four OpenFlow switches.

**Primary path:**

`h1 → s1 → s2 → s4 → h2`

**Backup path:**

`h1 → s1 → s3 → s4 → h2`

The POX controller monitors inter-switch link status and updates forwarding rules when a failure is detected.

## Project Structure

```text
udp_sdn_project/
│
├── topology.py
├── sender.py
├── receiver.py
├── protocol.py
│
└── pox_ext/
    └── reliable_paths.py
```

| File | Description |
|---|---|
| `topology.py` | Defines the Mininet diamond topology. |
| `sender.py` | Sends files using UDP. |
| `receiver.py` | Receives and reconstructs files. |
| `protocol.py` | Implements communication protocol functionality. |
| `reliable_paths.py` | POX controller logic for path management and link failure handling. |

## Key Features

### 1. Reliable UDP Communication
- Sequence numbers identify individual data packets.
- ACKs confirm successful packet reception.
- Timeouts trigger retransmissions.
- Duplicate packets are detected and handled.
- Out-of-order packets can be identified.

### 2. SDN-Based Path Management
- POX manages forwarding paths through OpenFlow.
- The controller monitors inter-switch link failures.
- Traffic is redirected through an alternate path when the primary path becomes unavailable.

### 3. File Integrity Verification
- SHA-256 checksums are calculated for file verification.
- The sender and receiver hashes are compared to verify successful file transfer.

## Setup and Execution

**Prerequisites**

- Ubuntu Linux
- Python 3
- Mininet
- POX controller
- Open vSwitch

### Step 1: Start the POX Controller

Navigate to the POX directory:

```bash
cd ~/pox
```

Start the controller:

```bash
python3 pox.py log.level --DEBUG openflow.of_01 --port=6633 reliable_paths
```

### Step 2: Start the Mininet Topology

Open another terminal and navigate to the project directory:

```bash
cd ~/udp_sdn_project/udp_sdn_project
```

Start Mininet:

```bash
sudo python3 topology.py
```

### Step 3: Start the Receiver

Inside the Mininet CLI:

```bash
h2 python3 receiver.py
```

### Step 4: Start the Sender

In another terminal, enter the Mininet CLI:

```bash
sudo mn
```

Alternatively, use the existing Mininet session and execute:

```bash
h1 python3 sender.py
```

*Ensure the sender and receiver use matching file paths and configuration arguments.*

## Testing and Evaluation

The following scenarios were used to evaluate the implementation:

| Test Scenario | Expected Result |
|---|---|
| Normal file transfer | File transferred successfully. |
| Data packet loss | Missing packets retransmitted. |
| ACK loss | Duplicate packet detected and acknowledged again. |
| Out-of-order delivery | Out-of-order packet detected. |
| Large file transfer | File transferred and integrity verified. |
| Primary link failure | Controller switches traffic to backup path. |
| Link restoration | Primary path can be restored according to controller logic. |

File integrity is verified using:

```bash
sha256sum <filename>
```

Matching SHA-256 hashes indicate that the received file matches the original.

## Limitations

- The controller is designed for the specific diamond topology and its predefined port layout.
- Host-to-switch link failure recovery is not implemented.
- The current implementation uses UDP rather than TCP.
- The controller does not implement general-purpose topology discovery.

## Future Enhancements

- Implement host-to-switch link failure recovery using dual-homed hosts.
- Introduce dynamic topology discovery.
- Improve path selection using network performance metrics.
- Evaluate throughput, latency and packet loss under different network conditions.

## Conclusion

This project demonstrates how application-layer reliability mechanisms can improve UDP-based file transfer when combined with SDN-based network control.

By integrating UDP socket programming, Mininet and the POX controller, the implementation supports reliable file delivery and recovery from inter-switch link failures.


# GITCRUSHERS Logistics AI - Technical Documentation

## Table of Contents
1. [Conceptual Overview](#conceptual-overview)
2. [System Architecture](#system-architecture)
3. [Frontend Implementation](#frontend-implementation)
4. [Backend Integration](#backend-integration)
5. [Data Models & Types](#data-models--types)
6. [Component Architecture](#component-architecture)
7. [Real-time Features](#real-time-features)
8. [API Specifications](#api-specifications)
9. [Development Setup](#development-setup)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)

---

## Conceptual Overview

### Problem Statement Analysis

The GITCRUSHERS Logistics AI system addresses a fundamental challenge in modern logistics: **static decision-making in a dynamic environment**. Traditional logistics systems make decisions once at the beginning of a journey and stick to them, regardless of changing conditions.

#### Core Problems Identified:
1. **Static Planning**: Routes and loads decided once, never adapted
2. **Dynamic Reality**: Traffic, fuel prices, delays, new requests constantly change
3. **Mid-Journey Decisions**: Critical decisions needed while trucks are moving
4. **System-wide Impact**: Individual truck decisions affect entire fleet efficiency
5. **Multi-stakeholder Complexity**: Drivers and fleet operators have different but connected needs

### Solution Philosophy

Our solution implements a **Continuous Decision Loop** that:
- **Observes** real-world conditions continuously
- **Reasons** about future outcomes before acting
- **Balances** multiple constraints (profit, time, capacity, fuel)
- **Acts** and immediately re-evaluates in an endless cycle

This transforms logistics from a static planning problem into a **dynamic, adaptive system**.

### Core Innovation: The OODA Loop for Logistics

We implement a modified OODA (Observe-Orient-Decide-Act) loop specifically designed for logistics:

1. **OBSERVE**: Continuous monitoring of truck positions, traffic, loads, fuel prices
2. **ORIENT**: Process and contextualize observations with business rules
3. **DECIDE**: AI-powered decision making with multi-constraint optimization
4. **ACT**: Execute decisions and immediately return to observation

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  AI Control     │  │  Fleet Mgmt     │  │  Analytics   │ │
│  │  Dashboard      │  │  & Maps         │  │  & Reports   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────
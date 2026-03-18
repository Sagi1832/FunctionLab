# FunctionLab Engine

The FunctionLab Engine is the computation core of the FunctionLab platform.

It is responsible for receiving mathematical input, normalizing it into a SymPy-compatible expression, performing symbolic analysis, and returning a structured result that can later be transformed into a more user-friendly response.

## Responsibilities

The engine is designed to handle the mathematical and processing logic of the platform, including:

- free-text mathematical input normalization using an LLM
- symbolic expression parsing with SymPy
- symbolic differentiation
- domain analysis
- extrema and critical point analysis
- monotonicity analysis
- intercept calculation
- asymptote detection
- structured result generation for downstream services
- user-friendly explanation generation using an LLM

## LLM Integration

This repository includes two LLM-based components:

### 1. Input Normalization LLM

The first LLM is responsible for transforming user input into a format that SymPy can understand.

Users may write expressions in inconsistent or informal ways, such as:

- `3x + 2`
- `x^2 + 4x - 1`
- natural language-like input with unclear formatting

This component converts such input into a normalized mathematical representation, for example:

- `3*x + 2`
- `x**2 + 4*x - 1`

This step makes the system more flexible and improves the reliability of symbolic parsing.

### 2. Presentation LLM

The second LLM is responsible for taking the engine's structured analytical output and converting it into a clearer, more readable, and more user-friendly explanation.

Its role is not to perform the mathematics itself, but to present the results in a way that is easier for end users to understand.

For example, instead of returning only raw symbolic data, the system can return a friendlier explanation of:

- what the derivative means
- where the function increases or decreases
- what the critical points are
- how to interpret the final analysis

## Kafka Role

The engine is also designed to participate in an event-driven workflow using Kafka.

Kafka is used as the communication layer between services so that the engine can work asynchronously and remain decoupled from other parts of the system.

At a high level, the flow is:

1. A request is produced to Kafka from an upstream service
2. The engine consumes the request
3. The input is normalized by the input LLM
4. The normalized expression is parsed and analyzed with SymPy
5. The structured result is passed through the presentation LLM
6. The final processed response is produced back for downstream consumption

This design helps keep the engine modular, scalable, and easier to evolve independently.

## High-Level Flow

1. A mathematical function is received from another service
2. The input normalization LLM converts it into a SymPy-compatible format
3. The engine parses and validates the normalized expression
4. Symbolic analysis is performed
5. A structured analytical result is generated
6. The presentation LLM transforms the output into a more user-friendly response
7. The final response is returned through the service communication layer

## Purpose

This repository isolates the computation and processing logic from the rest of the platform.

By separating the engine from the API and UI layers, the project becomes easier to maintain, test, scale, and improve independently.

## Tech Stack

- Python 3
- SymPy
- Kafka
- LLM integration

## Project Goals

- provide reliable symbolic math analysis
- support flexible user input through LLM-based normalization
- improve user experience through LLM-based output presentation
- keep the computation layer modular and independently scalable
- integrate cleanly with the broader FunctionLab architecture

## Notes

This repository focuses on computation, input normalization, symbolic analysis, and user-oriented result transformation.

Authentication, HTTP request handling, and frontend interaction are managed outside the engine layer.

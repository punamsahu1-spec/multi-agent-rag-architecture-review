# Scalability and Reliability Standard

## Scalability Requirements
- RFC must include current and projected traffic.
- RFC must mention expected RPS, peak load, and data growth.
- RFC must define horizontal or vertical scaling approach.
- RFC must identify bottlenecks.
- RFC must mention load testing plan for critical services.

## Reliability Requirements
- RFC must define availability target.
- RFC must define SLOs and SLIs.
- RFC must include timeout strategy.
- RFC must include retry strategy.
- RFC must include circuit breaker strategy where downstream systems are used.
- RFC must include graceful degradation plan.
- RFC must define disaster recovery and backup strategy where applicable.

## Failure Handling
- RFC must define what happens when dependencies fail.
- RFC must include dead-letter queue strategy for async processing.
- RFC must define idempotency for retryable operations.
- RFC must document recovery procedure.

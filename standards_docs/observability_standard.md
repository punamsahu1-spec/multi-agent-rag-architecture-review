# Observability Standard

## Metrics
- RFC must define business and technical metrics.
- RFC must include RED metrics: Rate, Errors, Duration.
- RFC must define infrastructure metrics where applicable.
- RFC must identify golden signals for service health.

## Logging
- RFC must define structured logging.
- Logs must include correlation ID or trace ID.
- Logs must avoid PII and secrets.
- Log retention must be documented.

## Tracing
- RFC must define distributed tracing for multi-service flows.
- Trace propagation must be documented across service boundaries.

## Alerting and Runbooks
- RFC must define alert thresholds.
- RFC must include runbook links or runbook ownership.
- RFC must define escalation path.
- RFC must avoid noisy alerts.

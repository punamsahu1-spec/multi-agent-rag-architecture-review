# RFC Standard Template — Required Sections

## 1. Problem Statement
- Clear description of current pain.
- Measurable impact such as latency, error rate, manual effort, cost, or customer impact.
- Stakeholders affected.

## 2. Proposed Solution
- Technical approach with architecture explanation.
- Alternatives considered and rejected.
- Trade-offs documented.
- Major components and integration points.

## 3. Security Considerations
- Threat model using STRIDE or OWASP Top 10.
- Authentication method such as OAuth2, SAML, mTLS, or API key.
- Authorization model such as RBAC or ABAC.
- Data encryption at rest and in transit.
- PII handling and data residency.
- Secrets management approach.

## 4. Scalability Approach
- Current and projected load such as RPS, DAU, data volume, and peak traffic.
- Horizontal or vertical scaling strategy.
- Bottleneck analysis.
- SLOs such as p99 latency and availability percentage.

## 5. Observability Plan
- Metrics to track using RED method: Rate, Errors, Duration.
- Structured logging approach.
- Distributed tracing approach.
- Alert thresholds and runbooks.
- Dashboard plan.

## 6. Rollback Strategy
- Step-by-step rollback procedure.
- Estimated rollback time.
- Named owner accountable for rollback.
- Data migration rollback plan.

## 7. Dependencies
- External services and APIs.
- Internal team dependencies.
- Third-party libraries and licenses.
- SLA of dependent services.

## 8. Timeline
- Milestones with dates.
- Named owner for each milestone.
- Risks and mitigations.

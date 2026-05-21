# Security Review Checklist for RFCs

## Authentication and Authorization
- Authentication method must be specified.
- Authorization model must be defined.
- Token expiry and refresh strategy must be documented.
- Admin access must have stronger controls.

## Data Security
- Data must be encrypted at rest.
- Data must be encrypted in transit.
- PII fields must be identified.
- Data retention and deletion policy must be defined.
- Data residency requirements must be documented where applicable.

## Application Security
- OWASP Top 10 risks must be assessed.
- Input validation must be described.
- SQL or NoSQL injection prevention must be addressed.
- XSS and CSRF risks must be considered where relevant.
- Secrets must not be hardcoded.
- Secrets must be stored in a vault or approved secret manager.

## Operational Security
- Audit logging must be defined for privileged actions.
- Vulnerability scanning must be part of CI/CD.
- Incident response ownership must be clear.

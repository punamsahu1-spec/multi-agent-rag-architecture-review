@'
# RFC: Customer Notification Service

## 1. Problem Statement

The current customer notification process is manual and slow. Business teams need to send order updates, payment reminders, shipment alerts, and service notifications to customers faster.

Current pain points:
- Notifications are delayed by several hours.
- Manual effort is high.
- Customers sometimes do not receive important updates on time.
- Support tickets increase when customers do not get timely notifications.

## 2. Proposed Solution

We propose building a new Customer Notification Service.

The service will:
- Receive notification requests from internal applications.
- Publish events to Kafka.
- Store notification status in PostgreSQL.
- Call an external SMS provider API.
- Retry failed notifications.
- Expose REST APIs for other systems.

High-level flow:
1. Internal application sends notification request.
2. Notification Service validates the request.
3. Service publishes the request to Kafka.
4. Worker consumes the message.
5. Worker calls SMS provider.
6. Status is saved in PostgreSQL.

## 3. Security Considerations

The service will use HTTPS.

Internal systems will call the service through REST APIs.

Customer phone numbers will be stored in PostgreSQL.

Secrets for the SMS provider will be configured in application settings.

## 4. Scalability Approach

The service should support future growth.

Kafka will help process messages asynchronously.

Workers can be increased if load increases.

## 5. Observability Plan

Application logs will be added.

Failures will be logged for debugging.

## 6. Rollback Strategy

If the deployment fails, we will roll back to the previous version.

## 7. Dependencies

The service depends on:
- Kafka
- PostgreSQL
- External SMS provider
- Internal order management system
- Internal payment system

## 8. Timeline

The team expects to complete the first version in 6 weeks.
'@ | Set-Content sample_rfcs\customer_notification_service_rfc.md -Encoding utf8
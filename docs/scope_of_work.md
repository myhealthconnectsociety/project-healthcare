# Documentation and Scope of Work for Project-Healthcare Phase 2

This document formalizes the functional analysis, requirements, and scope of work
for the PoC phase of `project-healthcare`, addressing all goals in Issue #39.

---

## 1. High-Level System Workflow and Architecture

The brokering service must evolve from a simple API to a robust, event-driven
architecture complying with international standards, modelled around **HL7 FHIR R4**.

### Open Solutions to Reference

| Solution | Purpose |
| --- | --- |
| [HAPI FHIR](https://hapifhir.io/) | FHIR R4 data modeling reference for Python/BlackSheep backend |
| [Bahmni](https://www.bahmni.org/) | Hospital IS / EMR — reference for facility monitoring, triage, inventory |
| [OpenMRS](https://openmrs.org/) | EMR platform — reference for patient data and clinical workflows |
| [iHRIS](https://www.ihris.org/) | Open-source HR for health — reference for doctors insight and workforce data |

### Architecture Decision Record (ADR)

- **API Gateway:** BlackSheep acts as the API Gateway
- **Datastore:** PostgreSQL with JSONB (FHIR resources). NocoDB for PoC prototyping
  only — strictly segregated from PHI
- **Async Messaging:** RabbitMQ or Redis Pub/Sub for enqueueing geolocation and
  telemetry events

---

## 2. Definition and Scope of Work

### A. Patient Data for Consultation

- **Scope:** Capture demographics (age, gender, location) and structured clinical
  data (chief complaints, symptoms)
- **Standard:** FHIR `Patient` and `Observation` resources
- **Work Item:** Update `/diagnose` and `/geo` to accept FHIR-compliant JSON

### B. Analytics Scope

All analytics must operate exclusively on **anonymized/de-identified** data.

#### i. Patient Traffic Flow

- Track `/geo` and `/diagnose` endpoint volumes geographically to expose hotspots
- Expose time-series dashboards per region/city

#### ii. Clinical Data and Disease Outbreak Monitoring

- Aggregate observation types (e.g. sudden spikes in "fever" queries in a zip code)
- Trigger alerts when an observation type exceeds a statistical threshold
  (Z-score based anomaly detection)

#### iii. Inventory Insight

- Predict resource exhaustion (beds, ventilators, medicines) based on patient
  routing volume
- Ingest facility-reported inventory levels via a push endpoint

#### iv. Doctors Insight

- Track: number of available doctors by specialty, consultation load per doctor,
  average wait time
- Use FHIR `Practitioner` and `PractitionerRole` resources for doctor registry data
- **Work Item:** Expose `GET /providers/doctors?specialty=<x>` with real-time
  availability

#### v. Seasonal Forecast

- Apply seasonal time-series models (Facebook Prophet or ARIMA) on historical
  diagnosis query data
- Predict spikes in diseases like Malaria, Dengue, Chikungunya by region
- **Work Item:** Expose `GET /analytics/forecast?disease=<x>&region=<y>`

#### vi. Other Hospital Resources

- Track nurse-to-patient ratios, ICU occupancy, OT availability, lab capacity
- Map to FHIR `Device` (equipment) and `Location` (ward/room) resources

### C. Facility Monitoring and Inventory Supply

- Track real-time operational status (open/closed/full) and capacity of facilities
- **Work Item:** Create a `Facility` entity (FHIR `Location`) and expose push
  endpoints for facility edge-devices to report status updates

### D. Location-Aware Triage

- Enhance geolocation logic to find the nearest *available and capable* facility
  based on real-time load, specialty, and wait time

### E. Telehealth Integration

- Return capability flags in `/geo` response indicating Telehealth support
- **Work Item:** Expose deep links or hand-off tokens to Telehealth endpoints
  (WebRTC standards) directly in the matched facility response

---

## 3. Compliance Assessment

### HIPAA and GDPR

| Requirement | Action |
| --- | --- |
| Data at Rest | Encrypt patient-identifiable data using `pgcrypto` or block-level encryption |
| Data in Transit | Enforce TLS 1.2+ on all BlackSheep inbound connections |
| Access Control | JWT-based RBAC verified against an Identity Provider |
| Audit Logging | Log Who/What/When for every PHI endpoint — never log raw patient data |
| Right to Erasure (GDPR Art. 17) | Implement a patient data deletion endpoint |

### FHIR HL7 (Release 4)

Implement a FHIR facade over BlackSheep endpoints allowing downstream consumers
to query via standard FHIR REST interfaces (e.g. `GET /Patient/{id}`).

### ABDM UHI (Beckn Protocol)

Build an adapter to support Beckn Protocol requests (discovery, order, fulfillment)
so this project acts as an HSP (Health Service Provider) in the ABDM network.

---

## 4. GitHub Project Board — Milestones and Definition of Done

These milestones are intended to be tracked on the GitHub Project Board.

### Milestone 1 — FHIR-compliant API Schemas

- **Goal:** Refactor `/geo` and `/diagnose` to accept and validate FHIR R4 schemas
- **Definition of Done:** API tests confirm FHIR-compliant payloads accepted;
  non-compliant payloads return 400 with descriptive errors

### Milestone 2 — Auth, Security and GDPR/HIPAA Compliance

- **Goal:** JWT RBAC, TLS enforcement, audit logging, GDPR deletion endpoint
- **Definition of Done:** All PHI endpoints return 401 without valid JWT;
  audit logs verified in CI; GDPR deletion endpoint tested

### Milestone 3 — Analytics Pipeline

- **Goal:** Async analytics for traffic, disease outbreak, doctors insight,
  seasonal forecasting
- **Definition of Done:** Anonymized dashboards available via API; forecast
  endpoint returns predictions; anomaly alerts trigger on threshold breach

### Milestone 4 — ABDM UHI and Telehealth Integration

- **Goal:** Beckn Protocol adapter live; Telehealth deep-links in `/geo` responses
- **Definition of Done:** Project registered as HSP in ABDM sandbox; Telehealth
  handoff verified end-to-end in integration tests

---

## 5. Required Resources Assessment

| Resource | Need | Priority |
| --- | --- | --- |
| `fhir.resources` (Python) | FHIR R4 schema validation | High |
| Redis or RabbitMQ | Async event queuing | High |
| `presidio-analyzer` | Data anonymization (GDPR compliance) | High |
| Facebook Prophet or statsmodels | Seasonal forecasting models | Medium |
| ABDM Developer Sandbox | Beckn Protocol integration testing | Medium |

---

*This scope of work serves as the guiding ADR and roadmap for the next 4 development
milestones, trackable via the GitHub Project Board.*

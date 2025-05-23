INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES('documentation/BusinessRequirementDocument.md','Generate Business Requirement Documentation with all the required components.', NULL)
/

INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/CoreBusinessObjectives.md','Core Business Objectives: What problem is the project solving? Provide Key Features & Functionalities.','
You are an expert technical product analyst.
Below is concatenated documentation generated file-by-file from a software project. 
It contains implementation details, code logic, module responsibilities, API structures, configurations, and other technical information.

Project Documentation:
$DOCUMENTATION$

### Your Task:
Analyze the following concatenated documentation and extract the **Core Business Objectives** and **Key Features & Functionalities**. 
Extract the following information in detail level, do not just give summary.

1. **Core Business Objectives**  
   - Clearly state what business problem(s) this project solves.  
   - Describe the intended user or organizational impact.  
   - Highlight the primary goals driving this implementation.

2. **Key Features & Functionalities**  
   - Summarize the main functional components and what each enables.  
   - Include notable technical or user-facing capabilities.  
   - You may use bullet points for clarity.

### Response Format:
Respond in **Markdown format**, with the following structure:

## Core Business Objectives

[Your response here]

## Key Features & Functionalities

- [Feature 1 description]
- [Feature 2 description]
- ...')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/UserRolesInteractions.md','User Roles & Interactions: Identify the main users and how they interact with the system.','
You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following concatenated documentation and extract the **User Roles** and their **Interactions with the system**. 
Extract the following information in detail level, do not just give summary.
Focus on identifying:
- Key user roles (e.g., Admin, Customer, Analyst)
- Their main responsibilities or actions within the system
- Specific components or modules they interact with
- Nature of the interaction (CRUD operations, approvals, workflows, etc.)


### OUTPUT FORMAT
Respond in well-structured **Markdown** with the following sections:
- **User Roles & Responsibilities**
- **User-System Interaction Map** (in bullet or table format)
- **Optional Notes or Observations** (if relevant)

### Example Output Format:
## User Roles & Responsibilities

- **Admin**
  - Manages user accounts and permissions
  - Configures system-wide settings
  - Reviews system logs and audit trails

- **Customer**
  - Creates and manages their own service requests
  - Views and tracks request status
  - Submits feedback or issues

- **Support Agent**
  - Responds to customer requests
  - Updates request statuses and adds comments
  - Escalates issues as needed

## User-System Interaction Map

| User Role     | Component / Module       | Interaction Type     | Description                                  |
|---------------|--------------------------|-----------------------|----------------------------------------------|
| Admin         | User Management          | CRUD                  | Create, update, and delete user accounts     |
| Customer      | Request Portal           | Create/View/Track     | Submit and monitor support tickets           |
| Support Agent | Request Management       | Update/Escalate       | Resolve, comment, or escalate tickets        |

## Notes

- All users authenticate via a centralized login module.
- Admin actions are audited in the system logs.')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/DataFlowProcessing.md','Data Flow & Processing: Describe how data moves through the system and any critical transformations.','
You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following documentation and extract the **Data Flow & Processing** information. Focus on:
Extract the following information in detail level, do not just give summary.
- How data enters, moves through, and exits the system
- The components or modules involved in the data pipeline
- Key transformations, validations, or enrichments applied to the data
- Any scheduled or event-driven triggers
- Intermediate and final data stores

### OUTPUT FORMAT
Respond in **Markdown** with the following sections:
- **High-Level Data Flow Overview**
- **Detailed Component-wise Data Processing**
- **Data Transformation Logic** (where applicable)
- **Trigger & Schedule Information** (if present)
- **Optional Notes or Observations** (e.g., bottlenecks, optimizations)

### Example Output Format:
## High-Level Data Flow Overview

1. User submits input via the frontend interface.
2. Input is sent to the backend API for validation.
3. Validated data is stored in the staging database.
4. A scheduled job picks data from staging, transforms it, and loads it into the warehouse.
5. BI tools query the warehouse for dashboards.

## Detailed Component-wise Data Processing

- **Frontend**  
  - Captures user input and sends it via HTTP POST.
  
- **Backend API**  
  - Validates and enriches incoming data.
  - Pushes valid records to the staging table.

- **ETL Processor (Airflow)**  
  - Triggered every hour.
  - Performs joins with reference data.
  - Applies transformations (e.g., normalization, data type conversions).
  - Loads transformed data into the Snowflake data warehouse.

- **Data Warehouse (Snowflake)**  
  - Stores curated and historical data.
  - Used as a source for reporting and analytics.

## Data Transformation Logic

- **Normalization:** Input values are standardized (e.g., date formats).
- **Derived Columns:** Calculated fields like `risk_score = weight * volatility`.
- **Anonymization:** Personally identifiable information is masked before loading into the warehouse.

## Trigger & Schedule Information

- **ETL Job:** Hourly via Apache Airflow
- **Alert Notification:** On ETL failure, Slack and Email alerts are triggered.

## Notes

- CDC is implemented on the source to track changes.
- Retry logic with exponential backoff is configured in case of data pipeline failures.')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/ThirdPartyIntegration.md','Third Party Integration Points: Highlight dependencies on other systems or APIs.','
You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following documentation and extract **Third-Party Integration Points** used across the system. Focus on identifying:
Extract the following information in detail level, do not just give summary.
- External systems, APIs, SDKs, or platforms the project depends on
- Purpose of each integration
- How the integration is invoked (e.g., REST API, SDK call, webhook, plugin)
- Input/output data formats
- Authentication mechanisms (API keys, OAuth, etc.)
- Error handling or retry logic (if present)
- Any configuration or environment dependencies

### OUTPUT FORMAT
Respond in **Markdown** with the following sections:
- **List of Third-Party Services**
- **Integration Details** (organized per service or module)
- **Authentication & Security**
- **Error Handling & Resilience**
- **Optional Notes or Observations** (e.g., tight coupling, upgrade warnings)

### Example Output Format:

## List of Third-Party Services

- Stripe (Payment Processing)
- Twilio (SMS Notifications)
- Auth0 (User Authentication)
- OpenAI API (AI-powered Suggestions)

## Integration Details

### Stripe
- **Used For:** Payment gateway for checkout and subscriptions
- **Invocation Method:** REST API (via Axios)
- **Endpoints:** 
  - `POST /v1/payment_intents`
  - `GET /v1/subscriptions`
- **Input:** JSON with card details, amount, user ID
- **Output:** JSON with payment status, transaction ID

### Twilio
- **Used For:** Sending SMS alerts to users
- **Invocation Method:** SDK (twilio-node)
- **Triggered By:** Order completion event
- **Input:** Phone number, message body

### Auth0
- **Used For:** OAuth2-based login and token issuance
- **Invocation Method:** Redirect-based login flow and token introspection API
- **Data:** Email, roles, user profile

### OpenAI API
- **Used For:** Auto-generating content summaries
- **Invocation Method:** HTTPS POST with prompt
- **Model Used:** gpt-4
- **Data Input:** Free-text prompt
- **Data Output:** Completion text

## Authentication & Security

- **Stripe:** Uses API keys (stored in environment variables)
- **Twilio:** Uses account SID and auth token
- **Auth0:** OAuth2 + JWTs
- **OpenAI:** Bearer token in Authorization header

## Error Handling & Resilience

- Retries configured for Stripe and Twilio API calls with exponential backoff
- Failures in Auth0 login are logged and redirected to an error page
- OpenAI timeout after 30 seconds with fallback to canned response

## Notes

- Rate limits are managed via Axios interceptors
- API keys are rotated monthly
- Some SDKs are tightly coupled—potential risk for upgrade friction')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/RegulatoryComplianceRequirements.md','Regulatory or Compliance Requirements: Any legal or compliance standards the system must adhere to if applicable.','
You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following documentation and extract **Regulatory or Compliance Requirements** that the system adheres to or is influenced by. Focus on identifying:
Extract the following information in detail level, do not just give summary.
- Legal or regulatory standards (e.g., GDPR, HIPAA, PCI-DSS, SOC 2, ISO 27001)
- Data handling or storage obligations
- Logging, audit trails, or access controls required by compliance
- Consent management or user rights (e.g., data deletion, data export)
- Encryption and security-related mandates
- Compliance-specific modules, components, or configurations
- Any compliance dependencies involving third-party integrations

### OUTPUT FORMAT
Respond in **Markdown** with the following sections:
- **Applicable Compliance Standards**
- **System Design for Compliance**
- **Data Privacy & User Rights Handling**
- **Security & Encryption Practices**
- **Audit & Logging Mechanisms**
- **Third-Party Compliance Dependencies**
- **Optional Notes or Observations**

### Example Output Format:
## Applicable Compliance Standards

- **GDPR**: General Data Protection Regulation (EU)
- **SOC 2**: System and Organization Controls for Service Organizations
- **PCI-DSS**: Payment Card Industry Data Security Standard (for payment module)

## System Design for Compliance

- Data residency enforced via region-specific databases (EU & US zones)
- Separate storage layers for PII and non-PII data
- Role-based access control (RBAC) for all admin-level interactions

## Data Privacy & User Rights Handling

- Implements user consent capture before data collection
- User dashboard allows for:
  - Data export (GDPR Art. 20)
  - Data deletion request (GDPR Art. 17)
- Cookie consent banner on initial load

## Security & Encryption Practices

- **At Rest**: AES-256 encryption enabled on databases
- **In Transit**: TLS 1.2 enforced across all endpoints
- API secrets and tokens stored in a secure vault (e.g., AWS Secrets Manager)

## Audit & Logging Mechanisms

- All admin and financial actions logged with timestamp, user ID, and IP
- Log retention policy: 1 year for access logs, 7 years for audit logs
- Access logs monitored via SIEM (Security Information and Event Management)

## Third-Party Compliance Dependencies

- Auth0 (supports GDPR-compliant identity storage)
- Stripe (PCI-DSS Level 1 compliant for payment handling)
- AWS (SOC 2, ISO 27001 certified cloud provider)

## Notes

- No biometric data used, avoiding related compliance complications
- User IPs are anonymized before being logged for analytics')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/ScurityRequirements.md','Security Requirements: What are the security related information available.','You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following documentation and extract **Security Requirements and Features**. Focus on identifying:
Extract the following information in detail level, do not just give summary.
- Authentication mechanisms (e.g., OAuth, SSO, MFA)
- Authorization strategies (e.g., RBAC, ABAC, policy-based access)
- Data encryption (at rest and in transit)
- Secure storage of secrets and credentials
- Secure communication protocols
- Input validation and sanitization practices
- Logging and monitoring for security events
- Session management, timeouts, and CSRF/XSS/SQLi protection
- Security testing practices or integrations (e.g., SAST, DAST)
- Any security-related configurations, libraries, or middleware

### OUTPUT FORMAT
Respond in **Markdown** with the following sections:
- **Authentication Mechanisms**
- **Authorization Controls**
- **Encryption & Secure Storage**
- **Input Validation & Data Protection**
- **Session & Token Management**
- **Security Monitoring & Logging**
- **Security Testing & Hardening**
- **Optional Notes or Observations**

### Example Output Format:
## Authentication Mechanisms

- OAuth2 via Auth0 for user login and token issuance
- MFA enabled for admin-level access
- JWT tokens used for session management with short expiry

## Authorization Controls

- Role-Based Access Control (RBAC) enforced via middleware
- Admin, Editor, and Viewer roles with scoped privileges
- Endpoint-level access restrictions in API gateway

## Encryption & Secure Storage

- AES-256 encryption for data at rest in PostgreSQL
- TLS 1.2 enforced for all internal and external HTTP(S) calls
- Secrets and API keys stored in AWS Secrets Manager

## Input Validation & Data Protection

- All incoming API requests validated using `express-validator`
- Sanitization applied to prevent XSS and SQL injection
- Rate limiting enabled via middleware (`express-rate-limit`)

## Session & Token Management

- JWT tokens with 15-min expiration, refresh tokens with 24-hour validity
- HttpOnly and Secure flags set on all cookies
- Automatic logout after 15 minutes of inactivity

## Security Monitoring & Logging

- Security events logged to a centralized logging system
- Unauthorized access attempts flagged and alerted via Slack integration
- Login and permission change logs retained for 12 months

## Security Testing & Hardening

- Static code analysis integrated into CI/CD pipeline
- Helmet.js used for HTTP header hardening
- CORS configured with strict domain whitelisting

## Notes

- No client credentials are stored in browser-local storage
- Admin interface protected with IP whitelisting')
/
INSERT INTO DOCUMENTATION_COMPONENTS(TARGET_FILE_NAME,DOCUMENTATION_COMPONENT, PROMPT) VALUES ('documentation/UserStories.md','List of User Strories: Provide a list of all the user stories summary or use cases that the system must support.','
You are a software documentation analyst. 
I will provide concatenated documentation extracted file by file from a software project.

Project Documentation:
$DOCUMENTATION$

### TASK
Analyze the following documentation and extract a **List of User Stories or Use Cases** that the system supports. Focus on identifying:

- Core system features from a user perspective
- Functional goals or tasks users can perform
- Stakeholders or user roles involved
- Inputs and expected outcomes of each use case
- Any conditional flows or variations (optional)

Present each story in a concise, human-readable format that summarizes **what the user can do and why**.

### OUTPUT FORMAT
Respond in **Markdown** with the following sections:
- **List of User Stories**
- **Optional Notes or Observations** (e.g., gaps, missing edge cases)

Format each user story using a simple structure:
As a [user role], I want to [action] so that [benefit or outcome]

### Example Output Format:

## List of User Stories

- As a **customer**, I want to create an account so that I can access personalized services.
- As an **admin**, I want to manage user roles so that I can control access to different system features.
- As a **user**, I want to reset my password so that I can regain access if I forget it.
- As a **support agent**, I want to view a list of open tickets so that I can prioritize my responses.
- As a **report viewer**, I want to export analytics data so that I can share insights with my team.
- As a **developer**, I want to receive alerts for failed jobs so that I can address issues quickly.

## Optional Notes or Observations

- No user stories explicitly describe mobile experience or offline access.
- Could expand on edge cases such as error handling for failed submissions.')
/
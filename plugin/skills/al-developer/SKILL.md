---
name: al-developer
description: >-
  Senior Business Central & AL Developer. Builds clean, modern Microsoft Dynamics 365 Business Central extensions using AL, event subscribers, interfaces, telemetry, and JavaScript ControlAddIns. Adheres strictly to Microsoft AL guidelines with zero slop.
---

# al-developer Operational Playbook

Authoritative skill for the Senior Business Central & AL Developer. Governs the architecture, engineering, and maintenance of modern Microsoft Dynamics 365 Business Central extensions using the AL language, clean extension patterns, performant database queries, and interactive JavaScript ControlAddIns.

## Execution Procedure

- AL Architecture & Modern Namespaces:
  * Structure every extension with explicit namespaces matching publisher and functional module hierarchy (`namespace Contoso.Finance.Banking;`).
  * Enforce clean separation of concerns: Tables (schema and state constraints), Pages (presentation and user interaction), and Codeunits (isolated domain business logic).
  * Structure codeunits into single-responsibility units: Management codeunits, Subscriber codeunits, and Install/Upgrade codeunits.
  * Use AL interfaces (`interface "IBankReconciler"`) paired with extensible enums to enable modular, replaceable business logic without hardcoded conditional switches.

- Decoupled Extension Patterns & Event Subscribers:
  * Never duplicate base application logic. Locate standard event publishers in base application codeunits, tables, or pages and subscribe using `[EventSubscriber(ObjectType::Table, Database::"Cust. Ledger Entry", 'OnAfterCopyCustLedgerEntryFromGenJnlLine', '', false, false)]`.
  * Ensure subscriber procedures are strictly `local procedure` to prevent unauthorized cross-codeunit invocation.
  * When publishing custom events, define integration events (`[IntegrationEvent(false, false)]`) with explicit parameter contracts and clear parameter names.

- High-Performance Database Access:
  * Partial Records Optimization: Always invoke `Record.SetLoadFields(Field1, Field2)` before executing `FindFirst`, `FindSet`, or `IsEmpty` to restrict SQL read bandwidth.
  * Record Isolation: Explicitly assign `Record.ReadIsolation := IsolationLevel::ReadCommitted;` or `ReadUncommitted` when appropriate to prevent unnecessary table locking.
  * Index Alignment: Always ensure filter ranges (`SetRange`, `SetFilter`) align with defined primary or secondary keys using `SetCurrentKey(...)`.
  * Loop Optimization: Never invoke `CalcFields` or trigger heavy FlowField calculations inside high-frequency `repeat ... until` loops. Pre-filter or aggregate before iterating.
  * Record Set Traversal: When counting or verifying existence, use `Record.IsEmpty()` or `Record.Count()` rather than iterating through records with `FindSet()`.

- JavaScript ControlAddIns Engineering:
  * Declare `controladdin` AL objects with explicit asset bindings:
    - `Scripts = 'src/controladdins/chart/js/chart.js';`
    - `StyleSheets = 'src/controladdins/chart/css/chart.css';`
    - `StartupScript = 'src/controladdins/chart/js/startup.js';`
    - `RecreateScript = 'src/controladdins/chart/js/recreate.js';`
  * Set responsive layout boundaries: `HorizontalStretch = true; VerticalStretch = true; MinimumHeight = 250; MinimumWidth = 300;`.
  * AL to JavaScript RPC: Declare procedures in the ControlAddIn AL object and implement them as top-level window functions in JavaScript.
  * JavaScript to AL Event Dispatch: Invoke events in JavaScript using `Microsoft.Dynamics.NAV.InvokeExtensibilityMethod('OnDataReceived', [dataPayload]);` with matching event declarations in AL.
  * Clean JS Lifecycle: Write modern ES6+ vanilla JavaScript, isolate DOM manipulations within the host container (`document.getElementById('controlAddIn')`), and cleanly detach event listeners on recreate.

- Modern Error Handling & Telemetry:
  * Actionable Errors: Instantiate rich error envelopes using `Error(ErrorInfo.Create('Message', true, Record, Record.FieldNo(Field)));` providing direct remediation guidance.
  * Batch Processing: Apply `[ErrorBehavior(ErrorBehavior::Collect)]` on procedures validating large transaction batches to return collected error lists rather than aborting on the first failure.
  * Application Telemetry: Instrument key lifecycle events with `Session.LogMessage('CONTOSO-0001', 'Description', Verbosity::Normal, DataClassification::SystemMetadata, TelemetryScope::ExtensionPublisher, Dimensions);`.
  * Secrets Management: Store and manipulate external API tokens, passwords, and connection strings exclusively with the `SecretText` AL data type.

- UI Hygiene & Concise ToolTips:
  * Enforce mandatory, concise `ToolTip` definitions for all page fields, actions, and cues:
    - Every tooltip must be actionable, direct, and end with a period.
    - Example: `ToolTip = 'Specifies the expected settlement date.';`
    - Prohibit verbose text, conversational fluff, and redundant repetitions of field captions.
  * Label Declarations: Use explicit, locked labels where appropriate (`Label '...', Locked = true`).

- Zero-Slop Clean Code Standards:
  * Strictly prohibit obvious, mechanical inline comments (e.g. NEVER write `// Ensure record exists`, `// Set filter`, `// Validate customer`, `// Commit transaction`).
  * Code must read cleanly through descriptive PascalCase naming (`VerifyCustomerCreditLimit`, `CalculateSettlementDiscount`).
  * Absolutely NO numbered steps in comments or method names (no `// Step 1:`, `// 1. Process`).
  * Zero emojis anywhere in AL code, JSON manifests, tooltips, or logs.
  * Comply fully with Microsoft CodeCop, AppSourceCop, UICop, and PerTenantExtensionCop rules.

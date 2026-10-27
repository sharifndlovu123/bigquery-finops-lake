# BigQuery FinOps Lake

A billing-to-BigQuery cost engine plus a governed Cloud Storage lake with Autoclass and retention locks, where Pub/Sub budget alerts trigger cleanup.

### Business use case

A South African agency or SME has many projects and no view of spend by team, while storage quietly grows. The platform shows chargeback by label, locks compliance records, and stops dev spend when a budget is breached.

### The hard piece

Automated cost remediation with storage lifecycle control

### Rough monthly cost, ZAR

R100 to R500 a month. BigQuery and Cloud Storage have free tiers, and the functions are tiny, so this is the cheapest project to leave running.

### Tool stack

- Cloud Billing export to BigQuery
- BigQuery views + scheduled queries
- Looker Studio
- Recommender API
- Budgets + Pub/Sub
- Cloud Run functions + Eventarc
- Cloud Scheduler + Workflows
- Cloud Storage (Autoclass, lifecycle, soft delete, versioning)
- Bucket Lock retention
- CMEK
- Storage Transfer Service
- Cloud Asset Inventory
- Infracost
- Terraform
- GitHub Actions + Workload Identity Federation
- dbt (optional)

### Diagrams

#### Diagram 1 · Architecture: billing data, remediation and the lake

```mermaid
flowchart TD
  subgraph PROJ["Projects under the organization"]
    R["Resources with labels<br/>team, env, owner"]
  end
  R --> BE[("Billing export<br/>BigQuery dataset")]
  BE --> V["Chargeback views by label"]
  V --> LS["Looker Studio dashboard"]
  BUD["Budgets at 50, 90 and 100 percent"] --> PS["Pub/Sub topic"]
  PS --> CF["Cloud Run function<br/>remediation ladder"]
  BE --> ANOM["Scheduled anomaly query<br/>vs 28 day baseline"]
  ANOM --> PS
  REC["Recommender API<br/>idle VMs, rightsizing"] --> CF
  CF -->|"stop dev VMs, scale nonprod GKE to zero"| R
  subgraph LAKE["Storage lake - africa-south1"]
    B1[("Bucket: Autoclass on<br/>soft delete, versioning")]
    B2[("Bucket: retention lock<br/>compliance records")]
  end
  B1 -.->|"optional encrypted copy<br/>Storage Transfer Service"| DR[("Bucket in another region<br/>needs POPIA review")]
```

> **How to read this:** Everything starts with labels: without them, the billing export cannot say who spent what. The export feeds dashboards and an anomaly query, and both budgets and anomalies publish to the same Pub/Sub topic, so one function handles every trigger. The lake at the bottom is separate: Autoclass moves data between storage classes on its own, and the locked bucket cannot be shortened or deleted early.

#### Diagram 2 · CI/CD: SQL, functions and cost diff

```mermaid
flowchart TD
  A["Commit or pull request"] --> B["Validate<br/>SQL lint, terraform validate"]
  B --> C["Scan<br/>Checkov and dbt tests"]
  C --> D["Plan<br/>terraform plan with Infracost diff"]
  D --> E{"Approval gate<br/>approval before enabling remediation"}
  E -->|"approved"| F["Deploy<br/>apply, deploy functions"]
  F --> G["Verify<br/>views return rows, remediation runs in dry-run"]
  G -->|"pass"| H["Promote to next environment"]
  G -->|"fail"| R["Rollback<br/>revert and disable the remediation function"]
  R --> K["Last known good state restored"]
  E -->|"rejected"| X["Stop and comment on the PR"]
```

> **How to read this:** Follow the top line from a commit to a deploy: the pipeline stops at the first red step, and nothing reaches the approval gate unless validation, scanning and the plan all passed. The bottom branch is the one hiring managers ask about: when verification fails, the rollback box puts the environment back without a human editing the console. Infracost adds the unusual part: the PR shows what the change will cost before it merges.

#### Diagram 3 · Hard piece: the budget ladder

```mermaid
flowchart TD
  A["Budget alert at 50 percent"] --> B["Notify team channel"]
  C["Budget alert at 90 percent"] --> D["Open a ticket and list the top 5<br/>cost drivers from the billing export"]
  E["Budget alert at 100 percent"] --> F{"Project labeled env dev?"}
  F -->|"yes"| G["Function stops VMs<br/>and scales GKE node pools to zero"]
  F -->|"no"| H["Page the owner<br/>no automatic action on prod"]
  G --> I["Log action and estimated saving<br/>in a BigQuery ledger"]
  H --> I
```

> **How to read this:** The ladder escalates with spend: tell, then investigate, then act. Automatic action is limited to projects labeled dev. Prod only pages a human, which is the safeguard you should call out in an interview.

### How it covers the five focus areas

- **Compute** (light): Cloud Run functions and jobs, Scheduler-driven stop and start of dev VMs and nonprod GKE, Spot for batch.
- **Networking** (light): Cloud Run with internal ingress, private bucket access, optional reuse of the VPC Service Controls perimeter from the landing zone.
- **Storage · HOME**: Autoclass versus lifecycle experiment, soft delete, versioning, Bucket Lock, CMEK, BigQuery partition expiry and long-term storage pricing, a documented DR option.
- **CI/CD** (deep): Terraform, SQL and function deploys in one pipeline, Infracost cost diff in PRs, dry-run first.
- **Cost optimisation · HOME**: Billing export, label-based chargeback, budgets, anomaly query, Recommender, BigQuery cost controls (maximum bytes billed), a savings ledger.
### Advanced features that show depth

- Chargeback views by label with an 'unlabeled' bucket that you drive towards zero
- Anomaly query against a 28-day baseline
- A remediation ladder that only acts on dev
- Infracost in every pull request
- BigQuery guardrails: maximum bytes billed and custom quotas, with a before-and-after cost test

### Production-like touches

- Dev and prod datasets and functions
- Alerts on pipeline failures and anomalies
- Runbook: a budget was breached, what to check first
- Post-incident write-up: a function stopped a VM that was labeled wrongly
- Monthly chargeback report

### AWS to GCP bridge

| AWS | Google Cloud | Where it differs |
| --- | --- | --- |
| CUR + Athena | Billing export to BigQuery | The export is native and queryable immediately. You write the anomaly logic yourself. |
| S3 Intelligent-Tiering | Cloud Storage Autoclass | Autoclass moves objects between classes on its own. |
| S3 Object Lock | Bucket Lock / retention policy | Locking a retention policy is permanent. |
| Lambda | Cloud Run functions | Triggered by Pub/Sub or Eventarc. |
| EventBridge Scheduler | Cloud Scheduler | Cron to HTTP or Pub/Sub. |
| Account budget actions | Budgets + Pub/Sub + function | Budgets only notify, so you build the action yourself. |

### Résumé pitch

- Built a billing-to-BigQuery FinOps pipeline with label-based chargeback covering \[N\]% of spend.
- Automated budget-triggered cleanup of dev resources, saving an estimated R\[N\] a month.
- Reduced storage cost by \[N\]% with Autoclass and lifecycle rules while keeping locked retention for compliance records.

> *Replace every \[N\] with a number you measured. If you cannot measure it, remove the claim.*

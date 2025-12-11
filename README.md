# **GenMerch Assembly Automation**

## 📄 Overview

**GenMerch Assembly Automation**
Automate POS frequency processing by reducing the hand off and manual interventions.

---

## 🧭 Solution Objective

The task is to **develop and validate a Python script** that:

1. Anomaly Detection will now fill out a standardized form with all of the parameters that they normally share via Teams Message.
2. A Python RPA application then takes that signal, produces the same message AO would normally post, and posts it to Teams.
3. The app then goes through all the manual NAV clicking, status updates (GOATS, Felix) that the Genpact Ops team manually does in the closeout process.

**Current Implementation:**
1. Anomaly Detection Hands-off to GenMerch Delivery team via a Teams message.
2. The team takes those parameters and translates them into job orders in NAV (Edit Manager, Console, Element Centre, ETL Job Control).
3. They monitor the status of those jobs, updating tracking tools, and then post back to Teams for final validation by Anomaly Detection.

---

## 🧩 Architecture & Solution Design

### Components

| Component                                     | Description                                                                             |
| --------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Decision Key "Utility Belt" SDK**           | Provides prebuilt functions for data extraction.                                        |
| **Databricks Runtime**                        | The execution environment required to access the proprietary `com.npd.ca.utilitybelt.DK` library. |
| **DK Data Extraction Layer**                  | A Python wrapper around the DK library to fetch `report_id`, `batch_id`, and underlying data. |
| **Unify API Client**                          | A Python class handling Basic Authentication, Session Management (Login), and the `saveReport` POST operation. |
| **Payload Transformation**                    | A logic block that maps the flat DK DataFrame structure into the hierarchical JSON format required by Unify (Rows, Columns, Filters). |
| **Automation Script (`solution.py`)**         | Implements extraction logic, flat file generation, and delivery.                        |
| **Config (`config.yaml`)**                    | Stores environment variables such as service endpoint, credentials, and delivery paths. |
| **Dev Container (`.devcontainer/` folder)**   | Defines a portable development environment for GitHub Codespaces.                       |
| **Tests (`/tests`)**                          | Unit tests for validating the automation workflow.                                      |

### Flow

1. **Initialize**: Load credentials and libraries.
2. **Fetch Source**: Query DK to find the `report_id` by name, then fetch the latest `schedule_event_id` (batch).
3. **Transform**: Map the DK result set to the Unify JSON Schema. *Note: The provided code uses a static template based on your schema; dynamic mapping requires specific logic to translate DK Member IDs to Unify Member IDs.*
4. **Push to Target**: Authenticate with the Unify Login API and POST the constructed JSON to the `saveReport` endpoint.

**Environment Setup:**
1. Developer launches a Codespace → container builds automatically using the provided `Dockerfile` and `devcontainer.json`.
2. The Python environment installs all dependencies from `requirements.txt`.
3. Developer configures `config.yaml` with valid credentials and parameters.
4. The `solution.py` script is executed via `python3 solution.py <ARGS>`.
5. Output file is validated and delivered to the target location.

---

## 🧰 Reference Documentation

* [ Cloud Analytics - Enablement Layer](https://iriworldwide-my.sharepoint.com/:p:/g/personal/olufemi_akinbode_circana_com/IQCnQBptMAfPH_W6lERel-GGAYQGeoX2M0kUnoSlcT-ysFs?e=hF4e90)
* [GenMerch Resource Center](https://iriworldwide.sharepoint.com/sites/product)
* [Coding Standards & Review Process](./docs/code_review_standards.md)
* [Architecture Diagram](./architecture.mmd)

---

## ⚙️ Development Environment

### GitHub Codespaces

Click **"Code → Open with Codespaces"** to launch the preconfigured environment.


---

## 🧪 Testing

Run all tests before submitting for review:

```bash
pytest tests/
```

Test coverage includes:

* DK connection validation
* Flat file schema conformity
* Delivery endpoint availability

---

## 🚀 Deployment / Delivery

Once validated, the automation will be scheduled or integrated into internal orchestration tools (e.g., Airflow, Control-M, or internal schedulers).
For the POC, execution will be manual via the CLI.


---

## 🔒 Security & Access

* **Authentication:** Service credentials are stored as GitHub Secrets or in a local `.env` file (excluded via `.gitignore`).
* **Data Handling:** Generated flat files contain internal data and cannot be uploaded to public repositories.
* **Access Control:** Only approved developers will have access to this repo (via MARU Developer Portal).

---

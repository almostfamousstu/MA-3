# A script that takes a decision key report_id as in

I have designed a Databricks Notebook solution to automate the migration of Decision Key reports to Unify. This solution wraps the provided `DK` library to extract source report metadata and constructs a compliant JSON payload for the Unify `saveReport` API.

## Blueprint

## Architecture Blueprint

### Components
1.  **Databricks Runtime**: The execution environment is required to access the proprietary `com.npd.ca.utilitybelt.DK` library.
2.  **DK Data Extraction Layer**: A Python wrapper around the DK library to fetch `report_id`, `batch_id`, and underlying data.
3.  **Unify API Client**: A Python class handling Basic Authentication, Session Management (Login), and the `saveReport` POST operation.
4.  **Payload Transformation**: A logic block that maps the flat DK DataFrame structure into the hierarchical JSON format required by Unify (Rows, Columns, Filters).

### Workflow
1.  **Initialize**: Load credentials and libraries.
2.  **Fetch Source**: Query DK to find the `report_id` by name, then fetch the latest `schedule_event_id` (batch).
3.  **Transform**: (Placeholder) Map the DK result set to the Unify JSON Schema. *Note: The provided code uses a static template based on your schema; dynamic mapping requires specific logic to translate DK Member IDs to Unify Member IDs.*
4.  **Push to Target**: Authenticate with the Unify Login API and POST the constructed JSON to the `saveReport` endpoint.

## Deployment Details

- **Category:** Other
- **Deployed:** 12/3/2025
- **Tags:** automated, circana, verified

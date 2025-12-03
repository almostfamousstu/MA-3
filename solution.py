%python
import requests
import json
import base64
from pyspark.sql import DataFrame

# ==========================================
# CONFIGURATION
# ==========================================
UNIFY_BASE_URL = "https://advantage.iriworldwide.com/unify-internal/reportbuilder"
UNIFY_USERNAME = "your_username"
UNIFY_PASSWORD = "your_password"
DK_REPORT_NAME = "Name of Decision Key Report" # Input Report Name
APP_NAME = "AppName"

# ==========================================
# UNIFY API CLIENT
# ==========================================
class UnifyClient:
    def __init__(self, base_url, username, password, app_name):
        self.base_url = base_url.rstrip('/')
        self.app_name = app_name
        self.session = requests.Session()
        
        # Construct Basic Auth Header
        creds = f"{username}:{password}"
        b64_creds = base64.b64encode(creds.encode()).decode()
        self.auth_header = {"Authorization": f"Basic {b64_creds}"}

    def login(self):
        """
        Authenticates with Unify to establish a session.
        Assumes endpoint is /login based on provided context.
        """
        url = f"{self.base_url}/login" # Adjust endpoint if specific path differs
        payload = {"appName": self.app_name}
        
        print(f"Logging into Unify: {url}")
        try:
            response = self.session.post(url, headers=self.auth_header, json=payload)
            response.raise_for_status()
            print("Login successful.")
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            raise

    def save_report(self, report_payload):
        """
        Posts the report structure to the saveReport API.
        """
        url = f"{self.base_url}/saveReport" # Implied endpoint
        print(f"Saving report to: {url}")
        
        # Ensure headers are set (Cookies are handled by self.session)
        headers = {
            "Content-Type": "application/json",
            **self.auth_header
        }
        
        try:
            response = self.session.post(url, headers=headers, json=report_payload)
            response.raise_for_status()
            print("Report saved successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to save report: {e}")
            if response.content:
                print(f"Response: {response.content}")
            raise

# ==========================================
# DK LIBRARY WRAPPER
# ==========================================
def get_dk_data(report_name):
    """
    Uses the Databricks DK Utility Belt to fetch report data.
    """
    try:
        # Import internal library
        from com.npd.ca.utilitybelt.DK import DK
        
        print(f"Initializing DK for report: {report_name}")
        dk = DK()
        
        # 1. Get Report ID
        all_report_ids_df = dk.get_all_report_id(report_name=report_name)
        reports = [{"report_name": r.report_name, "report_id": r.report_id} for r in all_report_ids_df.collect()]
        
        if not reports:
            raise ValueError(f"No report found with name: {report_name}")
            
        report_dict = reports[0]
        report_id = report_dict.get("report_id")
        print(f"Found Report ID: {report_id}")
        
        # 2. Get Batch ID
        all_batch_ids = dk.get_all_batch_id(report_id=report_id)
        if not all_batch_ids:
             raise ValueError(f"No batches found for report ID: {report_id}")
             
        report_batch_id = all_batch_ids[0].get("schedule_event_id")
        print(f"Using Batch ID: {report_batch_id}")
        
        # 3. Get Data
        df = dk.get_data(batch_event_id=report_batch_id, type="csv")
        return df, report_dict
        
    except ImportError:
        print("Error: com.npd.ca.utilitybelt.DK library not found. Ensure this runs on the correct Databricks cluster.")
        raise

# ==========================================
# PAYLOAD CONSTRUCTION
# ==========================================
def construct_unify_payload(report_name, dk_data_df):
    """
    Constructs the Unify JSON payload.
    NOTE: This uses the template provided. Dynamic mapping of DK rows 
    to Unify Member IDs (e.g., :SubCategory:...) requires a mapping logic 
    not present in the raw CSV data.
    """
    
    # Template based on user input
    payload = {
        "isUnifyTemplate": True,
        "reportName": report_name, # Dynamically set name
        "description": f"Migrated from DK Report: {report_name}",
        "workspaceId": None,
        "modelId": "1100",
        "asymmetric": True,
        "async": True,
        "progressiveFilter": { "progressiveDimensions": [] },
        "metadata": { "margin": 0, "background": { "color": "", "imageURL": "", "opacity": 100 } },
        "tags": [],
        "gridLayout": {
            "row": [
                {
                    "name": "Product",
                    "members": [
                        # TODO: Insert logic here to map dk_data_df rows to these member objects
                        {
                            "id": ":SubCategory:4527492:3506828:3506829:3506762:3506881:6124292",
                            "isSelected": True,
                            "level": "SubCategory",
                            "fullPath": "Product.Standard Hierarchy.TOTAL STORE.EDIBLE.DEPT-BEVERAGES.AISLE-COFFEE & TEA.COFFEE.COFFEE ADDITIVE/FLAVORING",
                            "name": "COFFEE ADDITIVE/FLAVORING",
                            "timeAggregate": None,
                            "dispLevelName": "SubCategory"
                        }
                        # ... additional members ...
                    ],
                    "attributes": [],
                    "isEditable": True,
                    "isPersistSelections": True,
                    "isVisible": True,
                    "userAlias": "Product",
                    "systemAlias": "Product",
                    "uiDispDimName": "Product"
                }
            ],
            "column": [
                {
                    "name": "Measures",
                    "members": [
                        {
                            "id": "!M2_1",
                            "isSelected": True,
                            "level": "Sales : FOLDER",
                            "fullPath": "Measures.Sales : FOLDER.Dollar Sales",
                            "name": "Dollar Sales",
                            "timeAggregate": None,
                            "dispLevelName": "Sales : FOLDER"
                        }
                    ],
                    "isEditable": False,
                    "isVisible": False,
                    "userAlias": "Measures",
                    "systemAlias": "Measures",
                    "uiDispDimName": "Measures"
                }
            ],
            "filter": [],
            "other": []
        },
        "hierarchies": [],
        "gridVisible": True,
        "chartVisible": False,
        "visualizerConfig": { "visualizers": [], "visLayout": { "template": "OneCellTemplate" } }
    }
    
    return payload

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Get Data from DK
    try:
        dk_df, report_info = get_dk_data(DK_REPORT_NAME)
        # dk_df.show(5) # Debug: View source data
        
        # 2. Construct Payload
        payload = construct_unify_payload(report_info['report_name'], dk_df)
        
        # 3. Send to Unify
        client = UnifyClient(UNIFY_BASE_URL, UNIFY_USERNAME, UNIFY_PASSWORD, APP_NAME)
        client.login()
        client.save_report(payload)
        
    except Exception as e:
        print(f"Process failed: {str(e)}")

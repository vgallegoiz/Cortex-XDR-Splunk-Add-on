# Cortex XDR Audit Add-on for Splunk

This Splunk add-on uses the Unified Configuration Console (UCC) Framework to collect data from Palo Alto Networks Cortex XDR public APIs. It enables security teams to ingest, monitor, and analyze management and agent audit events from XDR directly into Splunk.

---

## 📦 Features

- Connects to Cortex XDR APIs:
  - `GET /public_api/v1/audits/management_logs`
  - `GET /public_api/v1/audits/agents_reports`
- Collects and indexes:
  - Management logs (user, system, policy actions)
  - Agent reports (telemetry and endpoint activity)
- UCC-based UI for easy setup and configuration
- Secure credential handling
- Compatible with Splunk Enterprise and Splunk Cloud

---

## ⚙️ Configuration

Navigate to the **Configuration** page of the add-on within Splunk and set up your Cortex XDR account details.

### 🔐 Account Fields

| Field         | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Name          | Unique name for the account                                                 |
| Tenant Name   | Cortex XDR tenant name                                                      |
| API KEY       | The API key (stored encrypted)                                              |
| API Key ID    | The identifier associated with the API key (stored encrypted)              |
| Region        | XDR region. Options include `eu`, `us`, `uk`, `sg`, `jp`, `ca`, etc.        |

> 💡 Region determines the API host (e.g., `https://api-eu.xdr.traps.paloaltonetworks.com/` for EU).

---

## 🛠️ Inputs

Set up one or more data inputs via the **Inputs** page. Choose what data you want to pull from Cortex XDR.

### Available Input Types

- `Management Logs` - System and user actions within the XDR tenant
- `Agents Reports` - Endpoint activity and agent telemetry

### Input Configuration Fields

| Field         | Description                                                           |
|---------------|-----------------------------------------------------------------------|
| Name          | Unique name for the input                                             |
| Input Type    | One or both: `Management Logs`, `Agents Reports`                     |
| Index         | The target Splunk index to send data to                               |
| Interval      | How frequently (in seconds) to poll the API                           |
| Account       | The account (from Configuration) to use for authentication            |

---

## 📊 Dashboards

A default dashboard is available with basic visualizations. Extend it with your own panels using indexed events.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for full details.

---

## 🧰 Support

To report issues or request features, please open a [GitHub issue](https://github.com/vgallegoiz/Cortex-XDR-Splunk-Add-on/issues).

---

## 🔖 Version

- Add-on Name: `cortexxdr_audit`  
- Display Name: `CortexXDR Audit`  
- Version: `1.0.0`  
- UCC Framework Version: `5.49.0`

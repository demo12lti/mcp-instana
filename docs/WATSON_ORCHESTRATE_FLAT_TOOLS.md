# Watson Orchestrate Compatible Synthetic Monitoring Tools

## Overview

This document describes the new **flat parameter** synthetic monitoring tools designed specifically for Watson Orchestrate and other AI agents that cannot construct nested JSON objects.

## Problem Statement

Watson Orchestrate had difficulty using the original synthetic monitoring tools because they required nested parameter structures like:

```json
{
  "custom_properties": {
    "imap": "EAL-012471",
    "env": "dev"
  }
}
```

Watson Orchestrate cannot easily construct such nested objects, leading to tool call failures.

## Solution: Flat Parameter Tools

We've created two new standalone MCP tools with **completely flat parameters**:

1. **`get_synthetic_locations`** - Get available monitoring locations (no parameters)
2. **`create_synthetic_test`** - Create monitors with simple string/number parameters

## Tool 1: get_synthetic_locations

### Purpose
Retrieve all available synthetic monitoring locations where tests can be executed.

### Parameters
**NONE** - This tool requires no parameters at all!

### Usage
```python
get_synthetic_locations()
```

### Response
```json
{
  "locations": [
    {
      "id": "bxx9yzjHmKFn1u2oz3Kg",
      "displayLabel": "AWS US East (N. Virginia)",
      "description": "AWS us-east-1",
      "country": "US"
    },
    ...
  ],
  "count": 15
}
```

### When to Use
- **ALWAYS call this FIRST** before creating any synthetic monitor
- Show users the available locations
- Get location IDs for the create_synthetic_test tool

## Tool 2: create_synthetic_test

### Purpose
Create a new API synthetic monitor with flat parameters (no nested objects).

### Required Parameters

All parameters are simple strings, numbers, or arrays - **NO NESTED OBJECTS**:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `label` | string | Monitor name (must start with IMAP) | `"EAL-012471_MyAPI"` |
| `url` | string | API endpoint to monitor | `"https://ibm.com"` |
| `locations` | array[string] | Location IDs from get_synthetic_locations | `["bxx9yzjHmKFn1u2oz3Kg"]` |
| `imap` | string | IMAP identifier | `"EAL-012471"` |
| `env` | string | Environment | `"dev"`, `"prod"`, `"test"` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | integer | 10000 | Request timeout in milliseconds |
| `test_frequency` | integer | 15 | Test frequency in minutes (1, 5, 10, 15, 30, 60, 120, 240, 720, 1440) |
| `method` | string | "GET" | HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) |
| `headers` | object | null | HTTP headers as key-value pairs |
| `body` | string | null | Request body for POST/PUT/PATCH |
| `follow_redirects` | boolean | true | Follow HTTP redirects |
| `allow_insecure` | boolean | false | Allow insecure SSL certificates |
| `expect_status` | integer | 200 | Expected HTTP status code |
| `expect_json` | string | null | JSONPath expression to validate |
| `expect_match` | string | null | Regex pattern to match |
| `description` | string | null | Description of the test |
| `application_id` | string | null | Associate with an application |
| `active` | boolean | true | Whether test is active |

### Usage Example (Minimal)

```python
create_synthetic_test(
    label="EAL-012471_MyAPI",
    url="https://ibm.com",
    locations=["bxx9yzjHmKFn1u2oz3Kg"],
    imap="EAL-012471",
    env="dev"
)
```

### Usage Example (With Options)

```python
create_synthetic_test(
    label="EAL-012471_UserAPI",
    url="https://api.example.com/users",
    locations=["location1", "location2"],
    imap="EAL-012471",
    env="prod",
    method="POST",
    headers={"Content-Type": "application/json"},
    body='{"name": "test"}',
    expect_status=201,
    test_frequency=5,
    timeout=15000
)
```

### Response

```json
{
  "success": true,
  "message": "Successfully created API synthetic monitor: EAL-012471_MyAPI",
  "test": {
    "id": "abc123",
    "label": "EAL-012471_MyAPI",
    "url": "https://instana.example.com/#/synthetic;testId=abc123...",
    "api_endpoint": "https://ibm.com",
    "method": "GET",
    "frequency_minutes": 15,
    "locations": ["bxx9yzjHmKFn1u2oz3Kg"],
    "active": true,
    "custom_properties": {
      "imap": "EAL-012471",
      "env": "dev"
    }
  }
}
```

## Complete Workflow for Watson Orchestrate

### Step 1: Get Locations
```
User: "Create a monitor for https://ibm.com"

Watson: Calls get_synthetic_locations()
```

### Step 2: Present Options
```
Watson: "I found 15 available locations:
  1. AWS US East (N. Virginia) - ID: bxx9yzjHmKFn1u2oz3Kg
  2. AWS EU West (Ireland) - ID: xyz123abc456
  3. Azure US West - ID: abc789def012
  
Which location would you like to use?"
```

### Step 3: Collect Information
```
Watson: "I need a few more details:
  1. What is your IMAP identifier? (e.g., EAL-012471)"
  
User: "EAL-012471"

Watson: "2. Which environment? (dev/prod/test)"

User: "dev"

Watson: "3. What should we name this monitor? I suggest: EAL-012471_IBM_API"

User: "That works"
```

### Step 4: Create Monitor
```
Watson: Calls create_synthetic_test(
    label="EAL-012471_IBM_API",
    url="https://ibm.com",
    locations=["bxx9yzjHmKFn1u2oz3Kg"],
    imap="EAL-012471",
    env="dev"
)
```

### Step 5: Confirm Success
```
Watson: "✓ Successfully created monitor 'EAL-012471_IBM_API'!
  - Monitor ID: abc123
  - View in Instana: [URL]
  - Running every 15 minutes from AWS US East"
```

## Key Advantages

### 1. No Nested Objects
❌ **Old way (doesn't work with Watson):**
```json
{
  "custom_properties": {
    "imap": "EAL-012471",
    "env": "dev"
  }
}
```

✅ **New way (works with Watson):**
```json
{
  "imap": "EAL-012471",
  "env": "dev"
}
```

### 2. Automatic Internal Construction
The tool automatically builds the nested `custom_properties` structure internally:
- Watson passes: `imap="EAL-012471"`, `env="dev"`
- Tool builds: `custom_properties={"imap": "EAL-012471", "env": "dev"}`

### 3. Built-in Validation
- Label must start with IMAP value
- All required parameters validated
- Clear error messages with hints

### 4. Simple Parameter Types
- Strings: `"EAL-012471"`, `"dev"`, `"https://ibm.com"`
- Numbers: `10000`, `15`, `200`
- Arrays: `["location1", "location2"]`
- Booleans: `true`, `false`

## Validation Rules

### Label Validation
The `label` parameter **MUST** start with the `imap` value (case insensitive):

✅ Valid:
- `imap="EAL-012471"`, `label="EAL-012471_MyAPI"`
- `imap="EAL-012471"`, `label="eal-012471_test"` (case insensitive)

❌ Invalid:
- `imap="EAL-012471"`, `label="MyAPI"` (doesn't start with IMAP)

### Test Frequency Validation
Must be one of: `1, 5, 10, 15, 30, 60, 120, 240, 720, 1440` minutes

### HTTP Method Validation
Must be one of: `GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS`

## Error Handling

### Missing Required Parameter
```json
{
  "error": "Parameter 'imap' is required"
}
```

### Invalid Label
```json
{
  "error": "Label must start with imap value 'EAL-012471' (case insensitive)",
  "hint": "Current label: 'MyAPI', should start with: 'EAL-012471'",
  "example": "EAL-012471_MyAPI"
}
```

### Invalid Location
```json
{
  "error": "Parameter 'locations' is required and must contain at least one location ID",
  "hint": "Call get_synthetic_locations() first to get valid location IDs"
}
```

## Testing

Run the test script to verify the flat parameter structure:

```bash
python test_flat_synthetic_tools.py
```

This will:
1. Test `get_synthetic_locations()` with no parameters
2. Test `create_synthetic_test()` with flat parameters
3. Verify parameter validation
4. Confirm custom_properties are built correctly

## Migration Guide

### From Router Tool to Flat Tools

**Old Router Approach:**
```python
manage_synthetic_monitoring(
    resource_type="tools",
    operation="create_api_monitor",
    params={
        "label": "EAL-012471_MyAPI",
        "url": "https://ibm.com",
        "locations": ["loc1"],
        "custom_properties": {  # Nested object - Watson can't build this
            "imap": "EAL-012471",
            "env": "dev"
        }
    }
)
```

**New Flat Tool Approach:**
```python
create_synthetic_test(
    label="EAL-012471_MyAPI",
    url="https://ibm.com",
    locations=["loc1"],
    imap="EAL-012471",      # Flat parameter
    env="dev"                # Flat parameter
)
```

## Summary

The flat parameter tools solve Watson Orchestrate's limitation with nested objects by:

1. **Eliminating nested structures** - All parameters are flat
2. **Automatic internal construction** - Tool builds nested structures internally
3. **Simple parameter types** - Only strings, numbers, arrays, booleans
4. **Clear validation** - Helpful error messages
5. **Complete workflow** - Two tools cover all use cases

Watson Orchestrate can now successfully create synthetic monitors by simply passing flat string and number parameters!

## Support

For issues or questions:
1. Check the test script: `test_flat_synthetic_tools.py`
2. Review the prompts: `src/prompts/synthetic/synthetic_flat_tools.py`
3. See the implementation: `src/synthetic/synthetic_flat_tools.py`

---

**Made with Bob** 🤖
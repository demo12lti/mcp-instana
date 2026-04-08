# IMAP-Based Application Creation

This document describes how to create Instana Application Perspectives with IMAP-based tag filter expressions.

## Overview

When creating an Application Perspective in Instana, you can now provide an IMAP identifier (e.g., `EAL-012471`) which will automatically generate a comprehensive tag filter expression that matches services across multiple tag types.

## Tag Filter Expression Structure

The IMAP-based tag filter expression uses a logical `OR` operator to match services that have any of the following tags:

1. **agent.tag** with `imap` key (SOURCE and DESTINATION entities)
2. **kubernetes.pod.label** with `applications.cirrus.ibm.com/eal` key (SOURCE and DESTINATION entities)
3. **opentelemetry.tag** with `imap` key (NOT_APPLICABLE entity)

## Usage

### Method 1: Using the `imap` Parameter (Recommended)

Simply provide the `imap` parameter when creating an application.

**IMPORTANT**: The `label` must start with the IMAP value.

```python
payload = {
    "label": "EAL-012471_MyApplication",  # Label MUST start with IMAP value
    "imap": "EAL-012471",
    "scope": "INCLUDE_ALL_DOWNSTREAM",
    "boundaryScope": "ALL"
}

result = await client._add_application_config(payload=payload)
```

### Method 2: Manual Tag Filter Expression

You can also manually provide the complete tag filter expression:

```python
payload = {
    "label": "My Application",
    "tagFilterExpression": {
        "type": "EXPRESSION",
        "logicalOperator": "OR",
        "elements": [
            {
                "type": "TAG_FILTER",
                "name": "agent.tag",
                "stringValue": "imap=EAL-012471",
                "numberValue": None,
                "booleanValue": None,
                "floatValue": None,
                "key": "imap",
                "value": "EAL-012471",
                "operator": "EQUALS",
                "entity": "DESTINATION"
            },
            # ... additional filter elements
        ]
    }
}
```

## Generated Tag Filter Expression

When you provide `imap: "EAL-012471"`, the system automatically generates:

```json
{
    "type": "EXPRESSION",
    "logicalOperator": "OR",
    "elements": [
        {
            "type": "TAG_FILTER",
            "name": "agent.tag",
            "stringValue": "imap=EAL-012471",
            "numberValue": null,
            "booleanValue": null,
            "floatValue": null,
            "key": "imap",
            "value": "EAL-012471",
            "operator": "EQUALS",
            "entity": "DESTINATION"
        },
        {
            "type": "TAG_FILTER",
            "name": "agent.tag",
            "stringValue": "imap=EAL-012471",
            "numberValue": null,
            "booleanValue": null,
            "floatValue": null,
            "key": "imap",
            "value": "EAL-012471",
            "operator": "EQUALS",
            "entity": "SOURCE"
        },
        {
            "type": "TAG_FILTER",
            "name": "kubernetes.pod.label",
            "stringValue": "applications.cirrus.ibm.com/eal=EAL-012471",
            "numberValue": null,
            "booleanValue": null,
            "floatValue": null,
            "key": "applications.cirrus.ibm.com/eal",
            "value": "EAL-012471",
            "operator": "EQUALS",
            "entity": "DESTINATION"
        },
        {
            "type": "TAG_FILTER",
            "name": "kubernetes.pod.label",
            "stringValue": "applications.cirrus.ibm.com/eal=EAL-012471",
            "numberValue": null,
            "booleanValue": null,
            "floatValue": null,
            "key": "applications.cirrus.ibm.com/eal",
            "value": "EAL-012471",
            "operator": "EQUALS",
            "entity": "SOURCE"
        },
        {
            "type": "TAG_FILTER",
            "name": "opentelemetry.tag",
            "stringValue": "imap=EAL-012471",
            "numberValue": null,
            "booleanValue": null,
            "floatValue": null,
            "key": "imap",
            "value": "EAL-012471",
            "operator": "EQUALS",
            "entity": "NOT_APPLICABLE"
        }
    ]
}
```

## Complete Example

### Minimal Configuration

```python
from src.application.application_settings import ApplicationSettingsMCPTools

client = ApplicationSettingsMCPTools(
    read_token="your-api-token",
    base_url="https://your-instana-instance.com"
)

# Create application with just label and IMAP
# IMPORTANT: Label must start with IMAP value
result = await client._add_application_config(
    payload={
        "label": "EAL-012471_MyApplication",  # Must start with IMAP value
        "imap": "EAL-012471"
    }
)
```

This will use default values:
- `scope`: `INCLUDE_ALL_DOWNSTREAM`
- `boundaryScope`: `ALL`
- `accessRules`: `[{"accessType": "READ_WRITE", "relationType": "GLOBAL"}]`
- `tagFilterExpression`: Auto-generated from IMAP

### Full Configuration

```python
result = await client._add_application_config(
    payload={
        "label": "EAL-012471_MyApplication",  # Must start with IMAP value
        "imap": "EAL-012471",
        "scope": "INCLUDE_ALL_DOWNSTREAM",
        "boundaryScope": "ALL",
        "accessRules": [
            {
                "accessType": "READ_WRITE",
                "relationType": "GLOBAL"
            }
        ]
    }
)
```

## Testing

Run the test script to verify the functionality:

```bash
python test_create_application_with_imap.py
```

The test script will:
1. Show the generated tag filter expression for a test IMAP value
2. Prompt you to create an actual application with your IMAP identifier
3. Display the created application details including the tag filter

## Configuration Options

### Required Fields
- `label`: Application perspective name (string) - **MUST start with IMAP value if `imap` is provided**

### Optional Fields
- `imap`: IMAP identifier (string) - Auto-generates tag filter expression
- `scope`: Monitoring scope (string)
  - Options: `INCLUDE_ALL_DOWNSTREAM` (default), `INCLUDE_IMMEDIATE_DOWNSTREAM_DATABASE_AND_MESSAGING`, `INCLUDE_NO_DOWNSTREAM`
- `boundaryScope`: Boundary scope (string)
  - Options: `ALL` (default), `INBOUND`, `DEFAULT`
- `accessRules`: Access control rules (list)
  - Options: `READ_WRITE_GLOBAL` (default), `READ_ONLY_GLOBAL`, `CUSTOM`
- `tagFilterExpression`: Custom tag filter (dict) - Ignored if `imap` is provided

## Implementation Details

The IMAP-based tag filter generation is implemented in:
- `src/application/application_settings.py`: `_create_imap_tag_filter_expression()` method
- `src/application/application_settings.py`: `_validate_and_prepare_application_payload()` method

The feature automatically:
1. Detects when `imap` parameter is provided
2. Generates the comprehensive tag filter expression
3. Removes the `imap` parameter from the payload (it's not a valid API field)
4. Applies the generated tag filter to the application configuration

## Notes

- **IMPORTANT**: When using `imap`, the application label MUST start with the IMAP value (e.g., "EAL-012471_MyApp")
- The `imap` parameter is a convenience feature and is not sent to the Instana API
- The generated tag filter expression is what gets sent to the API
- If both `imap` and `tagFilterExpression` are provided, `imap` takes precedence
- The IMAP value is case-sensitive and should match your service tags exactly
- Validation will fail if the label doesn't start with the IMAP value

## Related Files

- `src/application/application_settings.py` - Main implementation
- `src/prompts/application/application_settings.py` - Prompt definitions
- `test_create_application_with_imap.py` - Test script
- `docs/IMAP_APPLICATION_CREATION.md` - This documentation
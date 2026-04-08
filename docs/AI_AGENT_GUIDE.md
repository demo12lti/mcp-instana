# AI Agent Guide for Application Creation

This guide is specifically designed for AI agents consuming the MCP server to create Instana Application Perspectives.

## Critical Requirements

### 🚨 MANDATORY: IMAP and Label Collection

When a user requests to create an application, you **MUST** collect TWO pieces of information:

1. **IMAP Identifier** (e.g., "EAL-012471")
2. **Application Name/Label** - **THE NAME/LABEL MUST CONTAIN IMAP AS PREFIX**

### ⚠️ Naming Convention Rule

**The label MUST start with the IMAP identifier.**

✅ **CORRECT Examples:**
- `EAL-012471_StatusRadar`
- `EAL-012471_MC_TST`
- `EAL-012471_MyApplication`

❌ **WRONG Examples:**
- `StatusRadar_EAL-012471` (IMAP not at beginning)
- `MyApplication` (no IMAP)
- `App_EAL-012471` (IMAP not at beginning)

## Recommended AI Agent Flow

### Example Conversation 1: User Provides IMAP

```
User: "Create an application for EAL-012471"

AI Agent: "I'll help you create an application for EAL-012471. What should the application name be? 
          Note: The name must start with 'EAL-012471_' followed by your application name.
          For example: EAL-012471_StatusRadar or EAL-012471_MC_TST"

User: "StatusRadar"

AI Agent: [Creates application with label="EAL-012471_StatusRadar", imap="EAL-012471"]
          "✅ Application 'EAL-012471_StatusRadar' created successfully!"
```

### Example Conversation 2: User Provides Full Name

```
User: "Create an application called MyApp"

AI Agent: "I'll help you create an application. First, what is the IMAP identifier for this application?"

User: "EAL-012471"

AI Agent: "Got it. The application name must start with 'EAL-012471_'. 
          Would you like to name it 'EAL-012471_MyApp'?"

User: "Yes"

AI Agent: [Creates application with label="EAL-012471_MyApp", imap="EAL-012471"]
          "✅ Application 'EAL-012471_MyApp' created successfully!"
```

## Error Handling

### Error 1: Missing Label

If you try to create without a label, you'll receive:

```json
{
  "error": "Missing required fields for application configuration",
  "ai_agent_instruction": "You MUST ask the user for both IMAP identifier and application label. The label must start with the IMAP value.",
  "ai_elicitation_flow": [
    "1. Ask user: 'What is the IMAP identifier for this application?' (e.g., EAL-012471)",
    "2. Ask user: 'What should the application name be?' Suggest format: '{IMAP}_ApplicationName'",
    "3. Optionally ask about scope, boundary scope, and access rules (or use defaults)"
  ]
}
```

**Action:** Follow the elicitation flow to collect required information.

### Error 2: Invalid Label Format

If the label doesn't start with IMAP, you'll receive:

```json
{
  "error": "Label must start with IMAP value 'EAL-012471'",
  "validation_failed": true,
  "current_label": "MyApp_EAL-012471",
  "required_format": "EAL-012471_ApplicationName",
  "ai_agent_instruction": "Please ask the user to provide a label that starts with 'EAL-012471'. Suggest format: 'EAL-012471_ApplicationName'",
  "examples": [
    "EAL-012471_StatusRadar",
    "EAL-012471_MC_TST",
    "EAL-012471_MyApplication"
  ]
}
```

**Action:** Ask user to provide a corrected name that starts with the IMAP identifier.

## API Request Format

### Minimal Request (Recommended)

```json
{
  "label": "EAL-012471_MyApplication",
  "imap": "EAL-012471"
}
```

### Full Request (With Optional Parameters)

```json
{
  "label": "EAL-012471_MyApplication",
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
```

## What Happens Automatically

When you provide the IMAP identifier, the system automatically:

1. **Generates comprehensive tag filters** for:
   - `agent.tag` with imap key (SOURCE and DESTINATION)
   - `kubernetes.pod.label` with applications.cirrus.ibm.com/eal key (SOURCE and DESTINATION)
   - `opentelemetry.tag` with imap key (NOT_APPLICABLE)

2. **Uses OR logic** to match any service with the IMAP tag

3. **Applies default values** for optional parameters:
   - scope: `INCLUDE_ALL_DOWNSTREAM`
   - boundaryScope: `ALL`
   - accessRules: `READ_WRITE_GLOBAL`

## Validation Rules

The MCP server will validate:

1. ✅ Label is provided
2. ✅ Label starts with IMAP value (if IMAP is provided)
3. ✅ IMAP format is valid

If validation fails, you'll receive detailed error messages with:
- Current values
- Required format
- Suggestions
- Examples

## Best Practices for AI Agents

1. **Always ask for IMAP first** - This is the foundation of the application
2. **Suggest the naming format** - Help users understand the requirement
3. **Validate before submitting** - Check that label starts with IMAP
4. **Use defaults for optional fields** - Don't overwhelm users with choices
5. **Provide clear feedback** - Confirm what was created

## Example Prompts for AI Agents

### When User Mentions IMAP

```
"I'll create an application for {IMAP}. What should the application name be? 
The name must start with '{IMAP}_' followed by your application name.
For example: {IMAP}_StatusRadar"
```

### When User Doesn't Mention IMAP

```
"To create an application, I need two pieces of information:
1. The IMAP identifier (e.g., EAL-012471)
2. The application name (which must start with the IMAP identifier)

What is the IMAP identifier for this application?"
```

### After Getting IMAP

```
"Great! Now, what should the application name be? 
Remember, it must start with '{IMAP}_'
For example: {IMAP}_MyApp or {IMAP}_StatusRadar"
```

## Testing Your Implementation

Use the test script to verify your AI agent handles all scenarios:

```bash
python3 test_ai_agent_guidance.py
```

This will show you:
- Error messages for missing label
- Error messages for invalid label format
- Success response for correct format

## Summary Checklist

Before creating an application, ensure:

- [ ] You have collected the IMAP identifier
- [ ] You have collected the application name
- [ ] The application name starts with the IMAP identifier
- [ ] The format is: `{IMAP}_{ApplicationName}`
- [ ] You're ready to handle validation errors if format is wrong

## Support

If you encounter issues or need clarification:
- Review error messages - they contain specific guidance
- Check examples in error responses
- Follow the suggested format exactly
- Refer to this guide for best practices
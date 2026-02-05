# Adding a New Automation

Guide for adding a new automation task to the framework.

## Overview

Automations are reusable workflows that orchestrate multiple OCI operations or queries. Unlike bulk operations that process large datasets, automations typically perform intelligent searches, validations, or multi-step configuration tasks.

## Architecture

The automation system follows a consistent pattern:

```
User → Agent → AutomationTasks → YourAutomation → BaseAutomation
                                        ↓
                                   _run() logic
                                        ↓
                                  SharedOperations
```

**Key Components:**

- `BaseAutomation[RequestT, PayloadT]` - Abstract base class all automations inherit from
- `AutomationResult[PayloadT]` - Standardised wrapper for automation outputs
- `AutomationTasks` - Gateway class that exposes automations to users
- `SharedOperations` - Reusable methods for fetching entity details

## Steps

### 1. Define Request and Result Dataclasses

Create dataclasses to structure your automation's input and output:

```python
from dataclasses import dataclass, field
from typing import Optional
from mercury_ocip.libs.types import OCIResponse


@dataclass(slots=True)
class YourAutomationRequest:
    """Input parameters for your automation"""
    service_provider_id: str
    group_id: str
    target_value: str
    # Add other required parameters


@dataclass(slots=True)
class YourAutomationResult:
    """Output data from your automation"""
    success: bool = field(default=False)
    data: Optional[OCIResponse] = None
    message: str = "Operation not completed."
    # Add other result fields as needed
```

**Design Tips:**
- Use `slots=True` for memory efficiency
- Provide sensible defaults for result fields
- Keep request simple - just the minimal data needed
- Result should contain all relevant information the user needs

### 2. Create Your Automation Class

Create a new file in `src/mercury_ocip/automate/` (e.g., `your_automation.py`):

```python
from mercury_ocip.automate.base_automation import BaseAutomation, AutomationResult
from mercury_ocip.client import BaseClient


class YourAutomation(BaseAutomation[YourAutomationRequest, YourAutomationResult]):
    """Brief description of what your automation does"""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: YourAutomationRequest) -> YourAutomationResult:
        """
        Core automation logic.
        
        Args:
            request: Input parameters
            
        Returns:
            Result containing outcome and relevant data
        """
        result = YourAutomationResult()
        
        # Your automation logic here
        # Use self.shared_ops for common operations
        # Use self.client for direct API calls
        
        return result

    def _wrap(self, payload: YourAutomationResult) -> AutomationResult[YourAutomationResult]:
        """
        Wrap result in standard AutomationResult container.
        
        Override this to customise ok/message fields based on your result.
        """
        result = super()._wrap(payload)
        result.ok = payload.success
        result.message = payload.message
        return result
```

### 3. Implement Core Logic

The `_run()` method contains your automation's logic. Common patterns:

#### Pattern 1: Search/Find Operations

```python
def _run(self, request: YourAutomationRequest) -> YourAutomationResult:
    result = YourAutomationResult()
    
    # Fetch entities
    entities = self.shared_ops.fetch_user_details(
        service_provider_id=request.service_provider_id,
        group_id=request.group_id
    )
    
    # Search through entities
    for entity in entities:
        if self._matches_criteria(entity, request):
            result.success = True
            result.data = entity
            result.message = "Found matching entity."
            break
    
    return result
```

#### Pattern 2: Validation Operations

```python
def _run(self, request: YourAutomationRequest) -> YourAutomationResult:
    result = YourAutomationResult()
    
    # Fetch and validate
    entity = self.shared_ops.fetch_specific_entity(
        service_provider_id=request.service_provider_id,
        entity_id=request.entity_id
    )
    
    validation_errors = self._validate_entity(entity, request.rules)
    
    if not validation_errors:
        result.success = True
        result.message = "Validation passed."
    else:
        result.success = False
        result.message = f"Validation failed: {', '.join(validation_errors)}"
        result.data = {"errors": validation_errors}
    
    return result
```

#### Pattern 3: Multi-Step Configuration

```python
def _run(self, request: YourAutomationRequest) -> YourAutomationResult:
    result = YourAutomationResult()
    
    try:
        # Step 1: Create entity
        entity_response = self.client.command(
            CreateEntityCommand(...)
        )
        
        # Step 2: Configure services
        service_response = self.client.command(
            AssignServiceCommand(...)
        )
        
        # Step 3: Set permissions
        permission_response = self.client.command(
            SetPermissionsCommand(...)
        )
        
        result.success = True
        result.data = entity_response
        result.message = "Entity created and configured successfully."
        
    except Exception as e:
        result.success = False
        result.message = f"Failed: {str(e)}"
    
    return result
```

### 4. Optional: Override _validate()

Add pre-execution validation to catch issues early:

```python
def _validate(self, request: YourAutomationRequest) -> None:
    """Quick validation before hitting the network"""
    if not request.service_provider_id:
        raise ValueError("service_provider_id is required")
    
    if len(request.target_value) < 3:
        raise ValueError("target_value must be at least 3 characters")
    
    # Add other validation logic
```

### 5. Register in AutomationTasks

Add your automation to `src/mercury_ocip/automate/automtion_tasks.py`:

```python
from mercury_ocip.automate.your_automation import (
    YourAutomation, 
    YourAutomationRequest, 
    YourAutomationResult
)


class AutomationTasks:
    """Main automation tasks handler"""

    def __init__(self, client: BaseClient):
        self.client = client
        self._alias_finder = AliasFinder(client)
        self._your_automation = YourAutomation(client)  # Add this

    # ... existing methods ...

    def your_automation(
        self,
        service_provider_id: str,
        group_id: str,
        target_value: str,
    ) -> AutomationResult[YourAutomationResult]:
        """
        Brief description of what this does.
        
        Args:
            service_provider_id: Service provider ID
            group_id: Group ID
            target_value: The value to process
            
        Returns:
            AutomationResult with success status and relevant data
        """
        request = YourAutomationRequest(
            service_provider_id=service_provider_id,
            group_id=group_id,
            target_value=target_value,
        )
        return self._your_automation.execute(request=request)
```

### 6. Add Tests

Create tests in `tests/automate_tasks/` following this pattern:

```python
import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass

from mercury_ocip.client import Client
from mercury_ocip.agent import Agent


class TestYourAutomation:
    """Tests for your automation"""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing"""
        return Mock(spec=Client)

    @pytest.fixture
    def agent(self, mock_client):
        """Agent instance with mocked client"""
        Agent._Agent__instance = None
        with patch.object(Agent, 'load_plugins'), patch.object(Agent, 'activate_plugins'):
            return Agent.get_instance(mock_client)

    def test_success_case(self, agent, mock_client):
        """Test successful execution"""
        # Mock shared_ops or client methods
        with patch.object(agent.automate._your_automation.shared_ops, 'some_method', return_value=[...]):
            result = agent.automate.your_automation(
                service_provider_id="TestSP",
                group_id="TestGroup",
                target_value="test"
            )

        assert result.ok is True
        assert result.payload.success is True
        assert result.payload.data is not None

    def test_failure_case(self, agent, mock_client):
        """Test failure scenario"""
        with patch.object(agent.automate._your_automation.shared_ops, 'some_method', return_value=[]):
            result = agent.automate.your_automation(
                service_provider_id="TestSP",
                group_id="TestGroup",
                target_value="nonexistent"
            )

        assert result.ok is False
        assert result.payload.success is False

    def test_edge_case(self, agent, mock_client):
        """Test specific edge case or behaviour"""
        # Test implementation
        pass
```

### 7. Add User Documentation

Create user-facing docs in `docs/agent/automations/your-automation.md`:

```markdown
# Your Automation

Brief description of what it does.

## Usage

\`\`\`python
from mercury_ocip import Client, Agent

client = Client(host="...", username="...", password="...")
agent = Agent.get_instance(client)

result = agent.automate.your_automation(
    service_provider_id="SP",
    group_id="Group",
    target_value="value"
)

if result.ok:
    print(f"Success: {result.payload.data}")
else:
    print(f"Failed: {result.message}")
\`\`\`

## Response Format

Describe the structure of the response...

## Notes

Important considerations...
```

## Base Automation Lifecycle

Understanding the execution flow:

```python
# User calls
agent.automate.your_automation(params)
    ↓
# AutomationTasks creates request
YourAutomationRequest(...)
    ↓
# Calls execute() on automation instance
your_automation.execute(request)
    ↓
# BaseAutomation.execute() orchestrates:
    1. _validate(request)     # Optional validation
    2. _run(request)          # Your core logic
    3. _wrap(result)          # Standardise output
    ↓
# Returns to user
AutomationResult[YourAutomationResult]
```

## Using SharedOperations

The `shared_ops` attribute provides reusable methods:

```python
# Fetch entity details
users = self.shared_ops.fetch_user_details(sp_id, group_id)
call_centers = self.shared_ops.fetch_call_center_details(sp_id, group_id)
hunt_groups = self.shared_ops.fetch_hunt_group_details(sp_id, group_id)
auto_attendants = self.shared_ops.fetch_auto_attendant_details(sp_id, group_id)

# Each returns: List[OCIResponse]
```

**When to use SharedOperations vs direct client calls:**

- **Use `shared_ops`**: For common read operations (fetching entity lists/details)
- **Use `self.client`**: For write operations, specific commands, or complex queries

## Best Practices

### 1. Keep Automations Focused

Each automation should do one thing well. If you find yourself adding too many parameters or conditionals, consider splitting into multiple automations.

**Good:**
```python
# One clear purpose
def find_alias(sp_id, group_id, alias)
def validate_hunt_group(sp_id, group_id, hg_id)
def migrate_user(sp_id, source_group, target_group, user_id)
```

**Avoid:**
```python
# Too many responsibilities
def manage_entities(sp_id, group_id, action, entity_type, options)
```

### 2. Provide Meaningful Results

Your result dataclass should give users everything they need:

```python
@dataclass(slots=True)
class ValidationResult:
    success: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    entity: Optional[OCIResponse] = None
    checked_items: int = 0
    message: str = ""
```

### 3. Handle Errors Gracefully

Catch and wrap exceptions with context:

```python
try:
    entities = self.shared_ops.fetch_user_details(...)
except Exception as e:
    result.success = False
    result.message = f"Failed to fetch users: {str(e)}"
    return result
```

### 4. Document Your Intent

Add docstrings explaining the why, not just the what:

```python
def _check_alias_format(self, alias: str) -> bool:
    """
    Validate alias format against BroadWorks requirements.
    
    Checks for:
    - Valid characters (alphanumeric, dots, hyphens)
    - Proper email format if domain is included
    - Length constraints (min 3, max 80 characters)
    
    Args:
        alias: The alias string to validate
        
    Returns:
        True if valid, False otherwise
    """
```

### 5. Make Results Actionable

Include enough information for users to act on the result:

```python
if not result.success:
    result.message = f"Alias '{alias}' already assigned to Hunt Group '{entity.name}'"
    result.data = {
        "entity_type": "Hunt Group",
        "entity_id": entity.service_instance_id,
        "entity_name": entity.name,
        "suggested_aliases": self._generate_alternatives(alias)
    }
```

## Common Patterns

### Early Exit Pattern

```python
def _run(self, request: Request) -> Result:
    result = Result()
    
    # Check each entity type
    for entity_type, fetch_func in self.entity_checks:
        entities = fetch_func(request.sp_id, request.group_id)
        
        for entity in entities:
            if self._matches(entity, request):
                result.found = True
                result.entity = entity
                return result  # Early exit on first match
    
    return result  # Not found
```

### Accumulation Pattern

```python
def _run(self, request: Request) -> Result:
    result = Result()
    errors = []
    
    # Check all entities, accumulate issues
    entities = self.shared_ops.fetch_user_details(...)
    
    for entity in entities:
        entity_errors = self._validate_entity(entity)
        if entity_errors:
            errors.extend(entity_errors)
    
    result.success = len(errors) == 0
    result.errors = errors
    return result
```

### Fan-Out Pattern

```python
def _run(self, request: Request) -> Result:
    result = Result()
    
    # Fetch data from multiple sources in parallel (conceptually)
    users = self.shared_ops.fetch_user_details(...)
    devices = self.shared_ops.fetch_device_details(...)
    services = self._fetch_services(...)
    
    # Aggregate and analyse
    result.data = self._correlate_data(users, devices, services)
    return result
```

## Troubleshooting

### Automation Not Found

**Issue:** `AttributeError: 'AutomationTasks' object has no attribute 'your_automation'`

**Solution:** Ensure you've registered your automation in the `AutomationTasks.__init__()` method and added the gateway method.

### Type Errors

**Issue:** `TypeError: BaseAutomation.__init__() missing 1 required positional argument: 'client'`

**Solution:** Ensure your automation class calls `super().__init__(client)` in its `__init__` method.

### Result Not Accessible

**Issue:** Users can't access fields in the result

**Solution:** Remember the wrapping structure:
- `result` → `AutomationResult`
- `result.payload` → `YourAutomationResult`
- `result.payload.data` → Actual data

### Shared Operations Not Available

**Issue:** `AttributeError: 'SharedOperations' object has no attribute 'fetch_X'`

**Solution:** Check if the method exists in `SharedOperations`. If not, either add it there or use `self.client.command()` directly.

## Examples from Existing Automations

### AliasFinder

A complete example showing the search pattern:

```python
# Request: Simple input parameters
@dataclass(slots=True)
class AliasRequest:
    service_provider_id: str
    group_id: str
    alias: str

# Result: Success flag + optional entity
@dataclass(slots=True)
class AliasResult:
    found: bool = False
    entity: Optional[OCIResponse] = None
    message: str = "Alias not found."

# Automation: Search logic with early exit
class AliasFinder(BaseAutomation[AliasRequest, AliasResult]):
    def _run(self, request: AliasRequest) -> AliasResult:
        result = AliasResult()
        
        for entity_type in self.checked_entities:
            matched = self._locate_alias(entity_type["func"], request)
            if matched:
                result.found = True
                result.entity = matched
                result.message = "Alias found."
                break
        
        return result
    
    def _wrap(self, payload: AliasResult) -> AutomationResult[AliasResult]:
        result = super()._wrap(payload)
        result.ok = payload.found
        result.message = payload.message
        return result
```

This demonstrates:
- Clear request/result separation
- Early exit on first match
- Custom wrap logic for ok/message
- Helper methods (`_locate_alias`) for clarity


# Automations Overview

The automations system provides a standardised framework for building intelligent workflows that orchestrate multiple API calls, perform searches, validations, or complex configuration tasks.

## Architecture

The automations system consists of three main layers:

1. **Gateway Layer** (`AutomationTasks`) - Provides user-friendly methods for each automation
2. **Automation Layer** - Individual automation classes (e.g., `AliasFinder`)
3. **Base Layer** (`BaseAutomation`) - Shared execution lifecycle and result wrapping

## Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
│                                                                   │
│  agent.automate.find_alias(sp_id, group_id, alias)              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AutomationTasks                              │
│                     (Gateway Layer)                              │
│                                                                   │
│  • Receives user parameters                                      │
│  • Creates Request dataclass                                     │
│  • Calls automation.execute()                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BaseAutomation.execute()                      │
│                     (Base Layer)                                 │
│                                                                   │
│  1. _validate(request)  ──► Pre-execution checks                │
│  2. _run(request)       ──► Core automation logic               │
│  3. _wrap(payload)      ──► Standardise result                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              YourAutomation._run(request)                        │
│              (Automation Layer)                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────┐                │
│  │ Access Helper Methods:                      │                │
│  │                                              │                │
│  │  • self.shared_ops.fetch_user_details()    │                │
│  │  • self.shared_ops.fetch_hunt_groups()     │                │
│  │  • self.client.command(...)                │                │
│  └─────────────────────────────────────────────┘                │
│                                                                   │
│  Returns: YourAutomationResult                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              YourAutomation._wrap(payload)                       │
│                                                                   │
│  • Maps payload fields to AutomationResult                       │
│  • Sets ok status based on success criteria                     │
│  • Sets user-facing message                                      │
│  • Returns: AutomationResult[YourAutomationResult]              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     User Receives Result                         │
│                                                                   │
│  result.ok              → Boolean success status                 │
│  result.message         → Human-readable message                 │
│  result.payload         → YourAutomationResult                   │
│  result.payload.data    → Actual data/entities                   │
│  result.notes           → Optional metadata                      │
└─────────────────────────────────────────────────────────────────┘
```

The pipeline processes requests through these stages:

1. **Gateway** - User calls simple method with parameters
2. **Request Creation** - Parameters packaged into typed Request object
3. **Validation** - Optional pre-flight checks (fast fail)
4. **Execution** - Core automation logic runs
5. **Wrapping** - Result standardised into AutomationResult
6. **Return** - User receives typed, consistent response

## Key Components

### BaseAutomation

Abstract base class providing the execution lifecycle:

```python
class BaseAutomation(ABC, Generic[RequestT, PayloadT]):
    def __init__(self, client: BaseClient):
        self.client = client
        self.shared_ops = SharedOperations(client)
    
    def execute(self, request: RequestT) -> AutomationResult[PayloadT]:
        self._validate(request)      # Optional validation
        raw = self._run(request)     # Core logic (abstract)
        return self._wrap(raw)       # Result wrapping
```

**Key Features:**
- Generic types for type safety (`RequestT`, `PayloadT`)
- Provides `client` for direct API access
- Provides `shared_ops` for common operations
- Enforces consistent execution flow
- Standardises error handling boundaries

### AutomationResult

Generic wrapper providing consistent result structure:

```python
@dataclass(slots=True)
class AutomationResult(Generic[PayloadT]):
    ok: bool                           # Success indicator
    payload: Optional[PayloadT]        # Typed automation result
    message: str                       # User-facing message
    notes: dict[str, Any]              # Optional metadata
```

**Design Goals:**
- Consistent interface across all automations
- Clear success/failure indicator (`ok`)
- Human-readable messages for users
- Strongly typed payload for IDE support
- Extensible notes field for metadata

### Request & Result Dataclasses

Each automation defines typed input and output:

```python
@dataclass(slots=True)
class AliasRequest:
    """Input parameters - what the automation needs"""
    service_provider_id: str
    group_id: str
    alias: str


@dataclass(slots=True)
class AliasResult:
    """Output data - what the automation found/did"""
    found: bool = False
    entity: Optional[OCIResponse] = None
    message: str = "Alias not found."
```

**Benefits:**
- Type safety and IDE autocompletion
- Self-documenting interfaces
- Validation support (dataclass validators)
- Memory efficiency (slots=True)
- Clear separation of concerns

### AutomationTasks Gateway

Provides user-facing API that hides internal complexity:

```python
class AutomationTasks:
    def __init__(self, client: BaseClient):
        self._alias_finder = AliasFinder(client)
        # ... other automations
    
    def find_alias(
        self, 
        service_provider_id: str, 
        group_id: str, 
        alias: str
    ) -> AutomationResult[AliasResult]:
        request = AliasRequest(
            service_provider_id=service_provider_id,
            group_id=group_id,
            alias=alias
        )
        return self._alias_finder.execute(request=request)
```

**Responsibilities:**
- Convert simple parameters to Request objects
- Manage automation instances
- Provide clean, consistent API
- Hide implementation details from users

### SharedOperations

Reusable methods for common entity operations:

```python
class SharedOperations:
    def fetch_user_details(self, sp_id: str, group_id: str) -> List[OCIResponse]:
        """Fetch all users in a group with full details"""
        
    def fetch_call_center_details(self, sp_id: str, group_id: str) -> List[OCIResponse]:
        """Fetch all call centers in a group"""
        
    def fetch_hunt_group_details(self, sp_id: str, group_id: str) -> List[OCIResponse]:
        """Fetch all hunt groups in a group"""
        
    def fetch_auto_attendant_details(self, sp_id: str, group_id: str) -> List[OCIResponse]:
        """Fetch all auto attendants in a group"""
```

**Purpose:**
- Avoid code duplication across automations
- Provide consistent entity fetching patterns
- Handle common API patterns (get list → fetch each)
- Centralize error handling for reads

## Execution Lifecycle

### 1. Pre-Validation Phase

```python
def _validate(self, request: RequestT) -> None:
    """Optional quick checks before hitting the network"""
```

**Use Cases:**
- Check required fields are present
- Validate format/length constraints
- Fast-fail on obviously invalid input
- Avoid unnecessary API calls

**Example:**
```python
def _validate(self, request: AliasRequest) -> None:
    if not request.alias:
        raise ValueError("alias cannot be empty")
    if len(request.alias) < 3:
        raise ValueError("alias must be at least 3 characters")
```

### 2. Execution Phase

```python
@abstractmethod
def _run(self, request: RequestT) -> PayloadT:
    """Core automation logic - must be implemented"""
```

**Responsibilities:**
- Fetch data using `shared_ops` or `client`
- Process/search/validate/transform data
- Handle business logic
- Return typed result object

**Example:**
```python
def _run(self, request: AliasRequest) -> AliasResult:
    result = AliasResult()
    
    # Fetch entities
    users = self.shared_ops.fetch_user_details(
        request.service_provider_id,
        request.group_id
    )
    
    # Search for match
    for user in users:
        if self._matches_alias(user, request.alias):
            result.found = True
            result.entity = user
            result.message = "Alias found."
            break
    
    return result
```

### 3. Wrapping Phase

```python
def _wrap(self, payload: PayloadT) -> AutomationResult[PayloadT]:
    """Standardise the result structure"""
```

**Default Behavior:**
```python
# BaseAutomation._wrap() default
return AutomationResult(ok=payload is not None, payload=payload)
```

**Custom Override:**
```python
# Override to customize ok/message
def _wrap(self, payload: AliasResult) -> AutomationResult[AliasResult]:
    result = super()._wrap(payload)
    result.ok = payload.found
    result.message = payload.message
    return result
```

## Common Automation Patterns

### Pattern 1: Search/Find

Find an entity matching specific criteria.

**Characteristics:**
- Iterates through entities
- Early exit on first match
- Returns found entity or None

**Example:** `AliasFinder`
```python
def _run(self, request: AliasRequest) -> AliasResult:
    for entity_type in self.entity_types:
        entities = self._fetch_entities(entity_type, request)
        
        for entity in entities:
            if self._matches(entity, request.alias):
                return AliasResult(
                    found=True, 
                    entity=entity,
                    message="Alias found."
                )
    
    return AliasResult(found=False)
```

### Pattern 2: Validation/Audit

Check entities for compliance or issues.

**Characteristics:**
- Accumulates errors/warnings
- Checks all items (no early exit)
- Returns list of issues

**Example:** Configuration Validator
```python
def _run(self, request: ValidationRequest) -> ValidationResult:
    errors = []
    warnings = []
    
    entities = self.shared_ops.fetch_user_details(
        request.service_provider_id, 
        request.group_id
    )
    
    for entity in entities:
        entity_issues = self._check_entity(entity, request.rules)
        errors.extend(entity_issues.errors)
        warnings.extend(entity_issues.warnings)
    
    return ValidationResult(
        success=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checked_count=len(entities)
    )
```

### Pattern 3: Multi-Step Workflow

Orchestrate multiple API operations in sequence.

**Characteristics:**
- Multiple API calls
- State tracking between steps
- Rollback on failure (optional)

**Example:** User Migration
```python
def _run(self, request: MigrationRequest) -> MigrationResult:
    try:
        # Step 1: Fetch source user
        user = self._get_user(request.user_id)
        
        # Step 2: Create in target group
        new_user = self.client.command(
            UserAddCommand(
                service_provider_id=request.target_sp,
                group_id=request.target_group,
                **user.to_dict()
            )
        )
        
        # Step 3: Copy services
        services = self._copy_services(user, new_user)
        
        # Step 4: Delete original (if requested)
        if request.delete_original:
            self.client.command(UserDeleteCommand(user_id=request.user_id))
        
        return MigrationResult(
            success=True,
            new_user=new_user,
            message="Migration complete."
        )
        
    except Exception as e:
        return MigrationResult(
            success=False,
            message=f"Migration failed: {str(e)}"
        )
```

### Pattern 4: Fan-Out/Aggregation

Gather data from multiple sources and correlate.

**Characteristics:**
- Multiple parallel fetches
- Data correlation/merging
- Summary/report generation

**Example:** Group Report
```python
def _run(self, request: ReportRequest) -> ReportResult:
    # Fetch from multiple sources
    users = self.shared_ops.fetch_user_details(
        request.service_provider_id,
        request.group_id
    )
    call_centers = self.shared_ops.fetch_call_center_details(
        request.service_provider_id,
        request.group_id
    )
    hunt_groups = self.shared_ops.fetch_hunt_group_details(
        request.service_provider_id,
        request.group_id
    )
    
    # Aggregate and analyse
    report = {
        "total_users": len(users),
        "total_call_centers": len(call_centers),
        "total_hunt_groups": len(hunt_groups),
        "users_without_devices": self._count_deviceless_users(users),
        "empty_hunt_groups": self._find_empty_hunt_groups(hunt_groups),
    }
    
    return ReportResult(
        success=True,
        report=report,
        message="Report generated."
    )
```

## Comparison: Automations vs Bulk Operations

| Aspect | Automations | Bulk Operations |
|--------|-------------|-----------------|
| **Purpose** | Intelligent workflows, searches, validations | Mass creation/modification of entities |
| **Input** | Simple parameters | CSV files or data arrays |
| **Scale** | Single or few entities | Hundreds/thousands of entities |
| **Operations** | Read-heavy, some writes | Write-heavy |
| **Result** | Single result object | Array of result objects |
| **Complexity** | Custom business logic | Standardised CRUD patterns |
| **Use Cases** | Find, validate, migrate, report | Create users, devices, call centers |

**When to use Automations:**
- You need to search or find specific entities
- You're validating configurations
- You're orchestrating multiple operations
- You need custom business logic
- Working with one or few entities

**When to use Bulk Operations:**
- You're creating many similar entities
- You have data in CSV format
- You need batch creation/updates
- Operations follow standard CRUD patterns
- Working with dozens or more entities

## Error Handling

### Validation Errors

Thrown during `_validate()` phase:
```python
def _validate(self, request: Request) -> None:
    if not request.required_field:
        raise ValueError("required_field is required")
```

**Behavior:** Exception propagates to user immediately, no API calls made.

### Execution Errors

Caught during `_run()` phase:
```python
def _run(self, request: Request) -> Result:
    try:
        data = self.shared_ops.fetch_users(...)
        # Process data
    except Exception as e:
        return Result(
            success=False,
            message=f"Failed: {str(e)}"
        )
```

**Behavior:** Return error in Result object, user receives structured error.

### Best Practice

Combine both approaches:
```python
def _validate(self, request: Request) -> None:
    # Fast-fail for obvious issues
    if not request.service_provider_id:
        raise ValueError("service_provider_id required")

def _run(self, request: Request) -> Result:
    try:
        # Handle runtime errors gracefully
        data = self._fetch_data(request)
        return Result(success=True, data=data)
    except Exception as e:
        return Result(
            success=False,
            message=f"Operation failed: {str(e)}",
            notes={"error_type": type(e).__name__}
        )
```

## Type Safety

The automation system uses Python generics for type safety:

```python
# Base class declares generic types
class BaseAutomation(ABC, Generic[RequestT, PayloadT]):
    def execute(self, request: RequestT) -> AutomationResult[PayloadT]:
        ...

# Concrete class specifies actual types
class AliasFinder(BaseAutomation[AliasRequest, AliasResult]):
    def _run(self, request: AliasRequest) -> AliasResult:
        ...
```

**Benefits:**
- IDE autocomplete for request/result fields
- Type checking catches errors early
- Self-documenting code
- Refactoring safety

## Testing Strategy

Automations should be tested through the user-facing API:

```python
def test_find_alias_success(agent, mock_client):
    # Mock the underlying data source
    with patch.object(
        agent.automate._alias_finder.shared_ops, 
        'fetch_user_details', 
        return_value=[mock_user]
    ):
        # Test through the public API
        result = agent.automate.find_alias(
            service_provider_id="SP",
            group_id="Group",
            alias="test"
        )
    
    # Verify structure and content
    assert result.ok is True
    assert result.payload.found is True
    assert result.payload.entity == mock_user
```

**Testing Principles:**
- Test through `agent.automate.*` methods (user perspective)
- Mock `shared_ops` methods for isolation
- Verify both `result` wrapper and `result.payload` content
- Test success cases, failure cases, and edge cases

## Extension Points

The automation system can be extended in several ways:

### 1. Add New Shared Operations

Extend `SharedOperations` with common fetch patterns:
```python
def fetch_device_details(self, sp_id: str, group_id: str) -> List[OCIResponse]:
    """Add new shared operation"""
```

### 2. Create Custom Automations

Implement `BaseAutomation` for new workflows:
```python
class MyAutomation(BaseAutomation[MyRequest, MyResult]):
    """Custom automation for specific workflow"""
```

### 3. Plugin System

Create separate packages that register automations:
```python
# In mercury_ocip_myplugin package
class MyPluginAutomation(BaseAutomation[...]):
    """Automatically discovered by Agent"""
```

The Agent will automatically load and register any automation classes from packages named `mercury_ocip_*`.

## Performance Considerations

### Fetching Strategies

**Option 1: Fetch All Upfront**
```python
# Good for: Small groups, need all data anyway
users = self.shared_ops.fetch_user_details(sp, group)
for user in users:
    process(user)
```

**Option 2: Fetch On-Demand**
```python
# Good for: Large groups, early exit likely
user_ids = self._get_user_ids(sp, group)
for user_id in user_ids:
    user = self._fetch_single_user(user_id)
    if matches(user):
        return user  # Early exit saves API calls
```

### Caching

Consider caching for repeated operations:
```python
@lru_cache(maxsize=128)
def _fetch_group_services(self, sp_id: str, group_id: str):
    """Cache expensive lookups"""
```

### Parallel Processing

For independent operations, consider concurrent execution:
```python
from concurrent.futures import ThreadPoolExecutor

# Fetch multiple entity types in parallel
with ThreadPoolExecutor() as executor:
    users_future = executor.submit(self.shared_ops.fetch_user_details, sp, group)
    devices_future = executor.submit(self.shared_ops.fetch_device_details, sp, group)
    
    users = users_future.result()
    devices = devices_future.result()
```

## See Also

- [Adding Automations](./adding-automations.md) - Step-by-step guide for creating new automations
- [Bulk Operations Overview](../bulk_opertaions/bulk-operations-overview.md) - Similar system for bulk entity operations
- [SharedOperations Reference](../../api/shared-operations.md) - Available helper methods


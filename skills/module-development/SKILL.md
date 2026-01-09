---
name: module-development
description: Guide for creating new Amplifier modules including protocol implementation, entry points, mount functions, and testing patterns. Use when creating new modules or understanding module architecture.
version: 1.0.0
license: MIT
metadata:
  category: development
  complexity: medium
  original_source: https://github.com/microsoft/amplifier-core/tree/main/docs/contracts
---

<!--
  Source: https://github.com/microsoft/amplifier-core
  License: MIT
  Auto-synced for Claude Code Plugin format
-->

# Module Contracts

**Start here for building Amplifier modules.**

This directory contains the authoritative guidance for building each type of Amplifier module. Each contract document explains:

1. **What it is** - Purpose and responsibilities
2. **Protocol reference** - Link to interfaces.py with exact line numbers
3. **Entry point pattern** - How modules are discovered and loaded
4. **Configuration** - Mount Plan integration
5. **Canonical example** - Reference implementation
6. **Validation** - How to verify your module works

---

## Module Types

| Module Type | Contract | Purpose |
|-------------|----------|---------|
| **Provider** | [PROVIDER_CONTRACT.md](PROVIDER_CONTRACT.md) | LLM backend integration |
| **Tool** | [TOOL_CONTRACT.md](TOOL_CONTRACT.md) | Agent capabilities |
| **Hook** | [HOOK_CONTRACT.md](HOOK_CONTRACT.md) | Lifecycle observation and control |
| **Orchestrator** | [ORCHESTRATOR_CONTRACT.md](ORCHESTRATOR_CONTRACT.md) | Agent loop execution strategy |
| **Context** | [CONTEXT_CONTRACT.md](CONTEXT_CONTRACT.md) | Conversation memory management |

---

## Quick Start Pattern

All modules follow this pattern:

```python
# 1. Implement the Protocol from interfaces.py
class MyModule:
    # ... implement required methods
    pass

# 2. Provide mount() function
async def mount(coordinator, config):
    """Initialize and register module."""
    instance = MyModule(config)
    await coordinator.mount("category", instance, name="my-module")
    return instance  # or cleanup function

# 3. Register entry point in pyproject.toml
# [project.entry-points."amplifier.modules"]
# my-module = "my_package:mount"
```

---

## Source of Truth

**Protocols are in code**, not docs:

- **Protocol definitions**: `amplifier_core/interfaces.py`
- **Data models**: `amplifier_core/models.py`
- **Message models**: `amplifier_core/message_models.py` (Pydantic models for request/response envelopes)
- **Content models**: `amplifier_core/content_models.py` (dataclass types for events and streaming)

These contract documents provide **guidance** that code cannot express. Always read the code docstrings first.

---

## Related Documentation

- [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) - Configuration contract
- [MODULE_SOURCE_PROTOCOL.md](https://github.com/microsoft/amplifier-core/blob/main/MODULE_SOURCE_PROTOCOL.md) - Module loading mechanism
- [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/specs/CONTRIBUTION_CHANNELS.md) - Module contribution pattern
- [DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/DESIGN_PHILOSOPHY.md) - Kernel design principles

---

## Validation

Verify your module before release:

```bash
# Structural validation
amplifier module validate ./my-module
```

See individual contract documents for type-specific validation requirements.

---

**For ecosystem overview**: [amplifier](https://github.com/microsoft/amplifier)


---

---
contract_type: module_specification
module_type: tool
contract_version: 1.0.0
last_modified: 2025-01-29
related_files:
  - path: amplifier_core/interfaces.py#Tool
    relationship: protocol_definition
    lines: 121-146
  - path: amplifier_core/models.py#ToolResult
    relationship: result_model
  - path: amplifier_core/message_models.py#ToolCall
    relationship: invocation_model
  - path: ../specs/MOUNT_PLAN_SPECIFICATION.md
    relationship: configuration
  - path: amplifier_core/testing.py#MockTool
    relationship: test_utilities
canonical_example: https://github.com/microsoft/amplifier-module-tool-filesystem
---

# Tool Contract

Tools provide capabilities that agents can invoke during execution.

---

## Purpose

Tools extend agent capabilities beyond pure conversation:
- **Filesystem operations** - Read, write, edit files
- **Command execution** - Run shell commands
- **Web access** - Fetch URLs, search
- **Task delegation** - Spawn sub-agents
- **Custom capabilities** - Domain-specific operations

---

## Protocol Definition

**Source**: `amplifier_core/interfaces.py` lines 121-146

```python
@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str:
        """Tool name for invocation."""
        ...

    @property
    def description(self) -> str:
        """Human-readable tool description."""
        ...

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """
        Execute tool with given input.

        Args:
            input: Tool-specific input parameters

        Returns:
            Tool execution result
        """
        ...
```

---

## Data Models

### ToolCall (Input)

**Source**: `amplifier_core/message_models.py`

```python
class ToolCall(BaseModel):
    id: str                    # Unique ID for correlation
    name: str                  # Tool name to invoke
    arguments: dict[str, Any]  # Tool-specific parameters
```

### ToolResult (Output)

**Source**: `amplifier_core/models.py`

```python
class ToolResult(BaseModel):
    success: bool = True              # Whether execution succeeded
    output: Any | None = None         # Tool output (typically str or dict)
    error: dict[str, Any] | None = None  # Error details if failed
```

---

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Tool | Callable | None:
    """
    Initialize and register tool.

    Returns:
        - Tool instance
        - Cleanup callable (for resource cleanup)
        - None for graceful degradation
    """
    tool = MyTool(config=config)
    await coordinator.mount("tools", tool, name="my-tool")
    return tool
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-tool = "my_tool:mount"
```

---

## Implementation Requirements

### Name and Description

Tools must provide clear identification:

```python
class MyTool:
    @property
    def name(self) -> str:
        return "my_tool"  # Used for invocation

    @property
    def description(self) -> str:
        return "Performs specific action with given parameters."
```

**Best practices**:
- `name`: Short, snake_case, unique across mounted tools
- `description`: Clear explanation of what the tool does and expects

### execute() Method

Handle inputs and return structured results:

```python
async def execute(self, input: dict[str, Any]) -> ToolResult:
    try:
        # Validate input
        required_param = input.get("required_param")
        if not required_param:
            return ToolResult(
                success=False,
                error={"message": "required_param is required"}
            )

        # Do the work
        result = await self._do_work(required_param)

        return ToolResult(
            success=True,
            output=result
        )

    except Exception as e:
        return ToolResult(
            success=False,
            error={"message": str(e), "type": type(e).__name__}
        )
```

### Tool Schema (Optional but Recommended)

Provide JSON schema for input validation:

```python
def get_schema(self) -> dict:
    """Return JSON schema for tool input."""
    return {
        "type": "object",
        "properties": {
            "required_param": {
                "type": "string",
                "description": "Description of parameter"
            },
            "optional_param": {
                "type": "integer",
                "default": 10
            }
        },
        "required": ["required_param"]
    }
```

---

## Configuration

Tools receive configuration via Mount Plan:

```yaml
tools:
  - module: my-tool
    source: git+https://github.com/org/my-tool@main
    config:
      max_size: 1048576
      allowed_paths:
        - /home/user/projects
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

---

## Observability

Register lifecycle events:

```python
coordinator.register_contributor(
    "observability.events",
    "my-tool",
    lambda: ["my-tool:started", "my-tool:completed", "my-tool:error"]
)
```

Standard tool events emitted by orchestrators:
- `tool:pre` - Before tool execution
- `tool:post` - After successful execution
- `tool:error` - On execution failure

---

## Canonical Example

**Reference implementation**: [amplifier-module-tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem)

Study this module for:
- Tool protocol implementation
- Input validation patterns
- Error handling and result formatting
- Configuration integration

Additional examples:
- [amplifier-module-tool-bash](https://github.com/microsoft/amplifier-module-tool-bash) - Command execution
- [amplifier-module-tool-web](https://github.com/microsoft/amplifier-module-tool-web) - Web access

---

## Validation Checklist

### Required

- [ ] Implements Tool protocol (name, description, execute)
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Returns `ToolResult` from execute()
- [ ] Handles errors gracefully (returns success=False, doesn't crash)

### Recommended

- [ ] Provides JSON schema via `get_schema()`
- [ ] Validates input before processing
- [ ] Logs operations at appropriate levels
- [ ] Registers observability events

---

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import TestCoordinator, MockTool

@pytest.mark.asyncio
async def test_tool_execution():
    tool = MyTool(config={})

    result = await tool.execute({
        "required_param": "value"
    })

    assert result.success
    assert result.error is None
```

### MockTool for Testing Orchestrators

```python
from amplifier_core.testing import MockTool

mock_tool = MockTool(
    name="test_tool",
    description="Test tool",
    return_value="mock result"
)

# After use
assert mock_tool.call_count == 1
assert mock_tool.last_input == {...}
```

---

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-tool --type tool
```

---

**Related**: [README.md](README.md) | [HOOK_CONTRACT.md](HOOK_CONTRACT.md)


---

---
contract_type: module_specification
module_type: provider
contract_version: 1.0.0
last_modified: 2025-01-29
related_files:
  - path: amplifier_core/interfaces.py#Provider
    relationship: protocol_definition
    lines: 54-119
  - path: amplifier_core/message_models.py
    relationship: request_response_models
  - path: amplifier_core/content_models.py
    relationship: event_content_types
  - path: amplifier_core/models.py#ProviderInfo
    relationship: metadata_models
  - path: ../specs/PROVIDER_SPECIFICATION.md
    relationship: detailed_spec
  - path: ../specs/MOUNT_PLAN_SPECIFICATION.md
    relationship: configuration
  - path: ../specs/CONTRIBUTION_CHANNELS.md
    relationship: observability
  - path: amplifier_core/testing.py
    relationship: test_utilities
canonical_example: https://github.com/microsoft/amplifier-module-provider-anthropic
---

# Provider Contract

Providers translate between Amplifier's unified message format and vendor-specific LLM APIs.

---

## Detailed Specification

**See [PROVIDER_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/PROVIDER_SPECIFICATION.md)** for complete implementation guidance including:

- Protocol summary and method signatures
- Content block preservation requirements
- Role conversion patterns
- Auto-continuation handling
- Debug levels and observability

This contract document provides the quick-reference essentials. The specification contains the full details.

---

## Protocol Definition

**Source**: `amplifier_core/interfaces.py` lines 54-119

```python
@runtime_checkable
class Provider(Protocol):
    @property
    def name(self) -> str: ...

    def get_info(self) -> ProviderInfo: ...

    async def list_models(self) -> list[ModelInfo]: ...

    async def complete(self, request: ChatRequest, **kwargs) -> ChatResponse: ...

    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]: ...
```

**Note**: `ToolCall` is from `amplifier_core.message_models` (see [REQUEST_ENVELOPE_V1](https://github.com/microsoft/amplifier-core/blob/main/specs/PROVIDER_SPECIFICATION.md) for details)

---

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Provider | Callable | None:
    """
    Initialize and return provider instance.

    Returns:
        - Provider instance (registered automatically)
        - Cleanup callable (for resource cleanup on unmount)
        - None for graceful degradation (e.g., missing API key)
    """
    api_key = config.get("api_key") or os.environ.get("MY_API_KEY")
    if not api_key:
        logger.warning("No API key - provider not mounted")
        return None

    provider = MyProvider(api_key=api_key, config=config)
    await coordinator.mount("providers", provider, name="my-provider")

    async def cleanup():
        await provider.client.close()

    return cleanup
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-provider = "my_provider:mount"
```

---

## Configuration

Providers receive configuration via Mount Plan:

```yaml
providers:
  - module: my-provider
    source: git+https://github.com/org/my-provider@main
    config:
      api_key: "${MY_API_KEY}"
      default_model: model-v1
      debug: true
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

---

## Observability

Register custom events via contribution channels:

```python
coordinator.register_contributor(
    "observability.events",
    "my-provider",
    lambda: ["my-provider:rate_limit", "my-provider:retry"]
)
```

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/specs/CONTRIBUTION_CHANNELS.md) for the pattern.

---

## Canonical Example

**Reference implementation**: [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)

Study this module for:
- Complete Provider protocol implementation
- Content block handling patterns
- Configuration and credential management
- Debug logging integration

---

## Validation Checklist

### Required

- [ ] Implements all 5 Provider protocol methods
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Preserves all content block types (especially `signature` in ThinkingBlock)
- [ ] Reports `Usage` (input/output/total tokens)
- [ ] Returns `ChatResponse` from `complete()`

### Recommended

- [ ] Graceful degradation on missing config (return None from mount)
- [ ] Validates tool call/result sequences
- [ ] Supports debug configuration flags
- [ ] Registers cleanup function for resource management
- [ ] Registers observability events via contribution channels

---

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import TestCoordinator, create_test_coordinator

@pytest.mark.asyncio
async def test_provider_mount():
    coordinator = create_test_coordinator()
    cleanup = await mount(coordinator, {"api_key": "test-key"})

    assert "my-provider" in coordinator.get_mounted("providers")

    if cleanup:
        await cleanup()
```

---

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-provider --type provider
```

---

**Related**: [PROVIDER_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/PROVIDER_SPECIFICATION.md) | [README.md](README.md)


---

---
contract_type: module_specification
module_type: hook
contract_version: 1.0.0
last_modified: 2025-01-29
related_files:
  - path: amplifier_core/interfaces.py#HookHandler
    relationship: protocol_definition
    lines: 205-220
  - path: amplifier_core/models.py#HookResult
    relationship: result_model
  - path: ../HOOKS_API.md
    relationship: detailed_api
  - path: ../specs/MOUNT_PLAN_SPECIFICATION.md
    relationship: configuration
  - path: ../specs/CONTRIBUTION_CHANNELS.md
    relationship: observability
  - path: amplifier_core/testing.py#EventRecorder
    relationship: test_utilities
canonical_example: https://github.com/microsoft/amplifier-module-hooks-logging
---

# Hook Contract

Hooks observe, validate, and control agent lifecycle events.

---

## Purpose

Hooks enable:
- **Observation** - Logging, metrics, audit trails
- **Validation** - Security checks, input validation
- **Feedback injection** - Automated correction loops
- **Approval gates** - Dynamic permission requests
- **Output control** - Clean user experience

---

## Detailed API Reference

**See [HOOKS_API.md](https://github.com/microsoft/amplifier-core/blob/main/HOOKS_API.md)** for complete documentation including:

- HookResult actions and fields
- Registration patterns
- Common patterns with examples
- Best practices

This contract provides the essentials. The API reference contains full details.

---

## Protocol Definition

**Source**: `amplifier_core/interfaces.py` lines 205-220

```python
@runtime_checkable
class HookHandler(Protocol):
    async def __call__(self, event: str, data: dict[str, Any]) -> HookResult:
        """
        Handle a lifecycle event.

        Args:
            event: Event name (e.g., "tool:pre", "session:start")
            data: Event-specific data

        Returns:
            HookResult indicating action to take
        """
        ...
```

---

## HookResult Actions

**Source**: `amplifier_core/models.py`

| Action | Behavior | Use Case |
|--------|----------|----------|
| `continue` | Proceed normally | Default, observation only |
| `deny` | Block operation | Validation failure, security |
| `modify` | Transform data | Preprocessing, enrichment |
| `inject_context` | Add to agent's context | Feedback loops, corrections |
| `ask_user` | Request approval | High-risk operations |

```python
from amplifier_core.models import HookResult

# Simple observation
HookResult(action="continue")

# Block with reason
HookResult(action="deny", reason="Access denied")

# Inject feedback
HookResult(
    action="inject_context",
    context_injection="Found 3 linting errors...",
    user_message="Linting issues detected"
)

# Request approval
HookResult(
    action="ask_user",
    approval_prompt="Allow write to production file?",
    approval_default="deny"
)
```

---

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Callable | None:
    """
    Initialize and register hook handlers.

    Returns:
        Cleanup callable to unregister handlers
    """
    handlers = []

    # Register handlers for specific events
    handlers.append(
        coordinator.hooks.register("tool:pre", my_validation_hook, priority=10)
    )
    handlers.append(
        coordinator.hooks.register("tool:post", my_feedback_hook, priority=20)
    )

    # Return cleanup function
    def cleanup():
        for unregister in handlers:
            unregister()

    return cleanup
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-hook = "my_hook:mount"
```

---

## Event Registration

Register handlers during mount():

```python
from amplifier_core.hooks import HookRegistry

# Get registry from coordinator
registry: HookRegistry = coordinator.hooks

# Register with priority (lower = earlier)
unregister = registry.register(
    event="tool:post",
    handler=my_handler,
    priority=10,
    name="my_handler"
)

# Later: unregister()
```

---

## Common Events

| Event | Trigger | Data Includes |
|-------|---------|---------------|
| `session:start` | Session created | session_id, config |
| `session:end` | Session ending | session_id, stats |
| `prompt:submit` | User input | prompt text |
| `tool:pre` | Before tool execution | tool_name, tool_input |
| `tool:post` | After tool execution | tool_name, tool_result |
| `tool:error` | Tool failed | tool_name, error |
| `provider:request` | LLM call starting | provider, messages |
| `provider:response` | LLM call complete | provider, response, usage |

---

## Configuration

Hooks receive configuration via Mount Plan:

```yaml
hooks:
  - module: my-hook
    source: git+https://github.com/org/my-hook@main
    config:
      enabled_events:
        - "tool:pre"
        - "tool:post"
      log_level: "info"
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

---

## Observability

Register custom events your hook emits:

```python
coordinator.register_contributor(
    "observability.events",
    "my-hook",
    lambda: ["my-hook:validation_failed", "my-hook:approved"]
)
```

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/specs/CONTRIBUTION_CHANNELS.md) for the pattern.

---

## Canonical Example

**Reference implementation**: [amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging)

Study this module for:
- Hook registration patterns
- Event handling
- Configuration integration
- Observability contribution

Additional examples:
- [amplifier-module-hooks-approval](https://github.com/microsoft/amplifier-module-hooks-approval) - Approval gates
- [amplifier-module-hooks-redaction](https://github.com/microsoft/amplifier-module-hooks-redaction) - Security redaction

---

## Validation Checklist

### Required

- [ ] Handler implements `async def __call__(event, data) -> HookResult`
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Returns valid `HookResult` for all code paths
- [ ] Handles exceptions gracefully (don't crash kernel)

### Recommended

- [ ] Register cleanup function to unregister handlers
- [ ] Use appropriate priority (10-90, lower = earlier)
- [ ] Log handler registration for debugging
- [ ] Support configuration for enabled events
- [ ] Register custom events via contribution channels

---

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import TestCoordinator, EventRecorder
from amplifier_core.models import HookResult

@pytest.mark.asyncio
async def test_hook_handler():
    # Test handler directly
    result = await my_validation_hook("tool:pre", {
        "tool_name": "Write",
        "tool_input": {"file_path": "/etc/passwd"}
    })

    assert result.action == "deny"
    assert "denied" in result.reason.lower()

@pytest.mark.asyncio
async def test_hook_registration():
    coordinator = TestCoordinator()
    cleanup = await mount(coordinator, {})

    # Verify handlers registered
    # ... test event emission

    cleanup()
```

### EventRecorder for Testing

```python
from amplifier_core.testing import EventRecorder

recorder = EventRecorder()

# Use in tests
await recorder.record("tool:pre", {"tool_name": "Write"})

# Assert
events = recorder.get_events()
assert len(events) == 1
assert events[0][0] == "tool:pre"  # events are (event_name, data) tuples
```

---

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-hook --type hook
```

---

**Related**: [HOOKS_API.md](https://github.com/microsoft/amplifier-core/blob/main/HOOKS_API.md) | [README.md](README.md)


---

---
contract_type: module_specification
module_type: orchestrator
contract_version: 1.0.0
last_modified: 2025-01-29
related_files:
  - path: amplifier_core/interfaces.py#Orchestrator
    relationship: protocol_definition
    lines: 26-52
  - path: amplifier_core/content_models.py
    relationship: event_content_types
  - path: ../specs/MOUNT_PLAN_SPECIFICATION.md
    relationship: configuration
  - path: ../specs/CONTRIBUTION_CHANNELS.md
    relationship: observability
  - path: amplifier_core/testing.py#ScriptedOrchestrator
    relationship: test_utilities
canonical_example: https://github.com/microsoft/amplifier-module-loop-basic
---

# Orchestrator Contract

Orchestrators implement the agent execution loop strategy.

---

## Purpose

Orchestrators control **how** agents execute:
- **Basic loops** - Simple prompt → response → tool → response cycles
- **Streaming** - Real-time response delivery
- **Event-driven** - Complex multi-step workflows
- **Custom strategies** - Domain-specific execution patterns

**Key principle**: The orchestrator is **policy**, not mechanism. Swap orchestrators to change agent behavior without modifying the kernel.

---

## Protocol Definition

**Source**: `amplifier_core/interfaces.py` lines 26-52

```python
@runtime_checkable
class Orchestrator(Protocol):
    async def execute(
        self,
        prompt: str,
        context: ContextManager,
        providers: dict[str, Provider],
        tools: dict[str, Tool],
        hooks: HookRegistry,
    ) -> str:
        """
        Execute the agent loop with given prompt.

        Args:
            prompt: User input prompt
            context: Context manager for conversation state
            providers: Available LLM providers (keyed by name)
            tools: Available tools (keyed by name)
            hooks: Hook registry for lifecycle events

        Returns:
            Final response string
        """
        ...
```

---

## Execution Flow

A typical orchestrator implements this flow:

```
User Prompt
    ↓
Add to Context
    ↓
┌─────────────────────────────────────┐
│  LOOP until response has no tools   │
│                                     │
│  1. emit("provider:request")        │
│  2. provider.complete(messages)     │
│  3. emit("provider:response")       │
│  4. Add response to context         │
│                                     │
│  If tool_calls:                     │
│    for each tool_call:              │
│      5. emit("tool:pre")            │
│      6. tool.execute(input)         │
│      7. emit("tool:post")           │
│      8. Add result to context       │
│                                     │
│  Continue loop...                   │
└─────────────────────────────────────┘
    ↓
Return final text response
```

---

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Orchestrator | Callable | None:
    """
    Initialize and return orchestrator instance.

    Returns:
        - Orchestrator instance
        - Cleanup callable
        - None for graceful degradation
    """
    orchestrator = MyOrchestrator(config=config)
    await coordinator.mount("session", orchestrator, name="orchestrator")
    return orchestrator
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-orchestrator = "my_orchestrator:mount"
```

---

## Implementation Requirements

### Event Emission

Orchestrators must emit lifecycle events for observability:

```python
async def execute(self, prompt, context, providers, tools, hooks):
    # Before LLM call
    await hooks.emit("provider:request", {
        "provider": provider_name,
        "messages": messages,
        "model": model_name
    })

    response = await provider.complete(request)

    # After LLM call
    await hooks.emit("provider:response", {
        "provider": provider_name,
        "response": response,
        "usage": response.usage
    })

    # Before tool execution
    await hooks.emit("tool:pre", {
        "tool_name": tool_call.name,
        "tool_input": tool_call.input
    })

    result = await tool.execute(tool_call.input)

    # After tool execution
    await hooks.emit("tool:post", {
        "tool_name": tool_call.name,
        "tool_input": tool_call.input,
        "tool_result": result
    })
```

### Hook Processing

Handle HookResult actions:

```python
# Before tool execution
pre_result = await hooks.emit("tool:pre", data)

if pre_result.action == "deny":
    # Don't execute tool
    return ToolResult(is_error=True, output=pre_result.reason)

if pre_result.action == "modify":
    # Use modified data
    data = pre_result.data

if pre_result.action == "inject_context":
    # Add feedback to context
    await context.add_message({
        "role": pre_result.context_injection_role,
        "content": pre_result.context_injection
    })

if pre_result.action == "ask_user":
    # Request approval (requires approval provider)
    approved = await request_approval(pre_result)
    if not approved:
        return ToolResult(is_error=True, output="User denied")
```

### Context Management

Manage conversation state:

```python
# Add user message
await context.add_message({"role": "user", "content": prompt})

# Add assistant response
await context.add_message({"role": "assistant", "content": response.content})

# Add tool result
await context.add_message({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result.output
})

# Get messages for LLM request (context handles compaction internally)
messages = await context.get_messages_for_request()
```

### Provider Selection

Handle multiple providers:

```python
# Get default or configured provider
provider_name = config.get("default_provider", list(providers.keys())[0])
provider = providers[provider_name]

# Or allow per-request provider selection
provider_name = request_options.get("provider", default_provider_name)
```

---

## Configuration

Orchestrators receive configuration via Mount Plan:

```yaml
session:
  orchestrator: my-orchestrator
  context: context-simple

# Orchestrator-specific config can be passed via providers/tools config
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

---

## Observability

Register custom events your orchestrator emits:

```python
coordinator.register_contributor(
    "observability.events",
    "my-orchestrator",
    lambda: [
        "my-orchestrator:loop_started",
        "my-orchestrator:loop_iteration",
        "my-orchestrator:loop_completed"
    ]
)
```

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/specs/CONTRIBUTION_CHANNELS.md) for the pattern.

---

## Canonical Example

**Reference implementation**: [amplifier-module-loop-basic](https://github.com/microsoft/amplifier-module-loop-basic)

Study this module for:
- Complete execute() implementation
- Event emission patterns
- Hook result handling
- Context management

Additional examples:
- [amplifier-module-loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming) - Real-time streaming
- [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events) - Event-driven patterns

---

## Validation Checklist

### Required

- [ ] Implements `execute(prompt, context, providers, tools, hooks) -> str`
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Emits standard events (provider:request/response, tool:pre/post)
- [ ] Handles HookResult actions appropriately
- [ ] Manages context (add messages, check compaction)

### Recommended

- [ ] Supports multiple providers
- [ ] Implements max iterations limit (prevent infinite loops)
- [ ] Handles provider errors gracefully
- [ ] Registers custom observability events
- [ ] Supports streaming via async generators

---

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import (
    TestCoordinator,
    MockTool,
    MockContextManager,
    ScriptedOrchestrator,
    EventRecorder
)

@pytest.mark.asyncio
async def test_orchestrator_basic():
    orchestrator = MyOrchestrator(config={})
    context = MockContextManager()
    providers = {"test": MockProvider()}
    tools = {"test_tool": MockTool()}
    hooks = HookRegistry()

    result = await orchestrator.execute(
        prompt="Test prompt",
        context=context,
        providers=providers,
        tools=tools,
        hooks=hooks
    )

    assert isinstance(result, str)
    assert len(context.messages) > 0
```

### ScriptedOrchestrator for Testing

```python
from amplifier_core.testing import ScriptedOrchestrator

# For testing components that use orchestrators
orchestrator = ScriptedOrchestrator(responses=["Response 1", "Response 2"])

result = await orchestrator.execute(...)
assert result == "Response 1"
```

---

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-orchestrator --type orchestrator
```

---

**Related**: [README.md](README.md) | [CONTEXT_CONTRACT.md](CONTEXT_CONTRACT.md)


---

---
contract_type: module_specification
module_type: context
contract_version: 2.1.0
last_modified: 2026-01-01
related_files:
  - path: amplifier_core/interfaces.py#ContextManager
    relationship: protocol_definition
    lines: 148-180
  - path: ../specs/MOUNT_PLAN_SPECIFICATION.md
    relationship: configuration
  - path: ../specs/CONTRIBUTION_CHANNELS.md
    relationship: observability
  - path: amplifier_core/testing.py#MockContextManager
    relationship: test_utilities
canonical_example: https://github.com/microsoft/amplifier-module-context-simple
---

# Context Contract

Context managers handle conversation memory and message storage.

---

## Purpose

Context managers control **what the agent remembers**:
- **Message storage** - Store conversation history
- **Request preparation** - Return messages that fit within token limits
- **Persistence** - Optionally persist across sessions
- **Memory strategies** - Implement various memory patterns

**Key principle**: The context manager owns **policy** for memory. The orchestrator asks for messages; the context manager decides **how** to fit them within limits. Swap context managers to change memory behavior without modifying orchestrators.

**Mechanism vs Policy**: Orchestrators provide the mechanism (request messages, make LLM calls). Context managers provide the policy (what to return, when to compact, how to fit within limits).

---

## Protocol Definition

**Source**: `amplifier_core/interfaces.py` lines 148-180

```python
@runtime_checkable
class ContextManager(Protocol):
    async def add_message(self, message: dict[str, Any]) -> None:
        """Add a message to the context."""
        ...

    async def get_messages_for_request(
        self,
        token_budget: int | None = None,
        provider: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get messages ready for an LLM request.

        The context manager handles any compaction needed internally.
        Returns messages that fit within the token budget.

        Args:
            token_budget: Optional explicit token limit (deprecated, prefer provider).
            provider: Optional provider instance for dynamic budget calculation.
                If provided, budget = context_window - max_output_tokens - safety_margin.

        Returns:
            Messages ready for LLM request, compacted if necessary.
        """
        ...

    async def get_messages(self) -> list[dict[str, Any]]:
        """Get all messages (raw, uncompacted) for transcripts/debugging."""
        ...

    async def set_messages(self, messages: list[dict[str, Any]]) -> None:
        """Set messages directly (for session resume)."""
        ...

    async def clear(self) -> None:
        """Clear all messages."""
        ...
```

---

## Message Format

Messages follow a standard structure:

```python
# User message
{
    "role": "user",
    "content": "User's input text"
}

# Assistant message
{
    "role": "assistant",
    "content": "Assistant's response"
}

# Assistant message with tool calls
{
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": "call_123",
            "type": "function",
            "function": {"name": "read_file", "arguments": "{...}"}
        }
    ]
}

# System message
{
    "role": "system",
    "content": "System instructions"
}

# Tool result
{
    "role": "tool",
    "tool_call_id": "call_123",
    "content": "Tool output"
}
```

---

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> ContextManager | Callable | None:
    """
    Initialize and return context manager instance.

    Returns:
        - ContextManager instance
        - Cleanup callable
        - None for graceful degradation
    """
    context = MyContextManager(
        max_tokens=config.get("max_tokens", 100000),
        compaction_threshold=config.get("compaction_threshold", 0.8)
    )
    await coordinator.mount("session", context, name="context")
    return context
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-context = "my_context:mount"
```

---

## Implementation Requirements

### add_message()

Store messages with proper validation:

```python
async def add_message(self, message: dict[str, Any]) -> None:
    """Add a message to the context."""
    # Validate required fields
    if "role" not in message:
        raise ValueError("Message must have 'role' field")

    # Store message
    self._messages.append(message)

    # Track token count (approximate)
    self._token_count += self._estimate_tokens(message)
```

### get_messages_for_request()

Return messages ready for LLM request, handling compaction internally:

```python
async def get_messages_for_request(
    self,
    token_budget: int | None = None,
    provider: Any | None = None,
) -> list[dict[str, Any]]:
    """
    Get messages ready for an LLM request.

    Handles compaction internally if needed. Orchestrators call this
    before every LLM request and trust the context manager to return
    messages that fit within limits.

    Args:
        token_budget: Optional explicit token limit (deprecated, prefer provider).
        provider: Optional provider instance for dynamic budget calculation.
            If provided, budget = context_window - max_output_tokens - safety_margin.
    """
    budget = self._calculate_budget(token_budget, provider)

    # Check if compaction needed
    if self._token_count > (budget * self._compaction_threshold):
        await self._compact_internal()

    return list(self._messages)  # Return copy to prevent mutation

def _calculate_budget(self, token_budget: int | None, provider: Any | None) -> int:
    """Calculate effective token budget from provider or fallback to config."""
    # Explicit budget takes precedence (for backward compatibility)
    if token_budget is not None:
        return token_budget

    # Try provider-based dynamic budget
    if provider is not None:
        try:
            info = provider.get_info()
            defaults = info.defaults or {}
            context_window = defaults.get("context_window")
            max_output_tokens = defaults.get("max_output_tokens")

            if context_window and max_output_tokens:
                safety_margin = 1000  # Buffer to avoid hitting hard limits
                return context_window - max_output_tokens - safety_margin
        except Exception:
            pass  # Fall back to configured max_tokens

    return self._max_tokens
```

### get_messages()

Return all messages for transcripts/debugging (no compaction):

```python
async def get_messages(self) -> list[dict[str, Any]]:
    """Get all messages (raw, uncompacted) for transcripts/debugging."""
    return list(self._messages)  # Return copy to prevent mutation
```

### set_messages()

Set messages directly for session resume:

```python
async def set_messages(self, messages: list[dict[str, Any]]) -> None:
    """Set messages directly (for session resume)."""
    self._messages = list(messages)
    self._token_count = sum(self._estimate_tokens(m) for m in self._messages)
```

**File-Based Context Managers - Special Behavior**:

For context managers with persistent file storage (like `context-persistent`), the behavior on session resume is different:

```python
async def set_messages(self, messages: list[dict[str, Any]]) -> None:
    """
    Set messages - behavior depends on whether we loaded from file.
    
    If we already loaded from our own file (session resume):
      - IGNORE this call to preserve our complete history
      - CLI's filtered transcript would lose system/developer messages
    
    If this is a fresh session or migration:
      - Accept the messages and write to our file
    """
    if self._loaded_from_file:
        # Already have complete history - ignore CLI's filtered transcript
        logger.info("Ignoring set_messages - loaded from persistent file")
        return
    
    # Fresh session: accept messages
    self._messages = list(messages)
    self._write_to_file()
```

**Why This Pattern?**:
- CLI's `SessionStore` saves a **filtered** transcript (no system/developer messages)
- File-based context managers save the **complete** history
- On resume, the context manager's file is authoritative
- Prevents loss of system context during session resume

### clear()

Reset context state:

```python
async def clear(self) -> None:
    """Clear all messages."""
    self._messages = []
    self._token_count = 0
```

---

## Internal Compaction

Compaction is an **internal implementation detail** of the context manager. It happens automatically when `get_messages_for_request()` is called and the context exceeds thresholds.

### Non-Destructive Compaction (REQUIRED)

**Critical Design Principle**: Compaction MUST be **ephemeral** - it returns a compacted VIEW without modifying the stored history.

```
┌─────────────────────────────────────────────────────────────────┐
│                    NON-DESTRUCTIVE COMPACTION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  messages[]                    get_messages_for_request()       │
│  ┌──────────┐                  ┌──────────┐                     │
│  │ msg 1    │                  │ msg 1    │  (compacted view)   │
│  │ msg 2    │   ──────────▶    │ [summ]   │                     │
│  │ msg 3    │   ephemeral      │ msg N    │                     │
│  │ ...      │   compaction     └──────────┘                     │
│  │ msg N    │                                                   │
│  └──────────┘                  get_messages()                   │
│       │                        ┌──────────┐                     │
│       │                        │ msg 1    │  (FULL history)     │
│       └───────────────────▶    │ msg 2    │                     │
│         unchanged              │ msg 3    │                     │
│                                │ ...      │                     │
│                                │ msg N    │                     │
│                                └──────────┘                     │
│                                                                 │
│  Key: Internal state is NEVER modified by compaction.           │
│       Compaction produces temporary views for LLM requests.     │
│       Full history is always available via get_messages().      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why Non-Destructive?**:
- **Transcript integrity**: Full conversation history is preserved for replay/debugging
- **Session resume**: Can resume from any point with complete context
- **Reproducibility**: Same inputs produce same outputs
- **Observability**: Hook systems can observe the full conversation

**Implementation Pattern**:
```python
async def get_messages_for_request(self, token_budget=None, provider=None):
    """Return compacted VIEW without modifying internal state."""
    budget = self._calculate_budget(token_budget, provider)
    
    # Read current messages (don't modify)
    messages = list(self._messages)  # Copy!
    
    # Check if compaction needed
    token_count = self._count_tokens(messages)
    if not self._should_compact(token_count, budget):
        return messages
    
    # Compact EPHEMERALLY - return compacted copy
    return self._compact_messages(messages, budget)  # Returns NEW list

async def get_messages(self):
    """Return FULL history (never compacted)."""
    return list(self._messages)  # Always complete
```

### Tool Pair Preservation

**Critical**: During compaction, tool_use and tool_result messages must be kept together. Separating them causes LLM API errors.

```python
async def _compact_internal(self) -> None:
    """Internal compaction - preserves tool pairs."""
    # Emit pre-compaction event
    await self._hooks.emit("context:pre_compact", {
        "message_count": len(self._messages),
        "token_count": self._token_count
    })

    # Build tool_call_id -> tool_use index map
    tool_use_ids = set()
    for msg in self._messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_use_ids.add(tc.get("id"))

    # Identify which tool results have matching tool_use
    orphan_result_indices = []
    for i, msg in enumerate(self._messages):
        if msg.get("role") == "tool":
            if msg.get("tool_call_id") not in tool_use_ids:
                orphan_result_indices.append(i)

    # Strategy: Keep system messages + recent messages
    # But ensure we don't split tool pairs
    system_messages = [m for m in self._messages if m["role"] == "system"]

    # Find safe truncation point (not in middle of tool sequence)
    keep_count = self._keep_recent
    recent_start = max(0, len(self._messages) - keep_count)

    # Adjust start to not split tool sequences
    while recent_start > 0:
        msg = self._messages[recent_start]
        if msg.get("role") == "tool":
            # This is a tool result - need to include the tool_use before it
            recent_start -= 1
        else:
            break

    recent_messages = self._messages[recent_start:]

    self._messages = system_messages + recent_messages
    self._token_count = sum(self._estimate_tokens(m) for m in self._messages)

    # Emit post-compaction event
    await self._hooks.emit("context:post_compact", {
        "message_count": len(self._messages),
        "token_count": self._token_count
    })
```

### Compaction Strategies

Different strategies for different use cases:

#### Simple Truncation

Keep N most recent messages (with tool pair preservation):

```python
# Find safe truncation point
keep_from = len(self._messages) - keep_count
# Adjust to not split tool pairs
while keep_from > 0 and self._messages[keep_from].get("role") == "tool":
    keep_from -= 1
self._messages = self._messages[keep_from:]
```

#### Summarization

Use LLM to summarize older messages:

```python
# Summarize old messages
old_messages = self._messages[:-keep_recent]
summary = await summarize(old_messages)

# Replace with summary
self._messages = [
    {"role": "system", "content": f"Previous conversation summary: {summary}"},
    *self._messages[-keep_recent:]
]
```

#### Importance-Based

Keep messages based on importance score:

```python
scored = [(m, self._score_importance(m)) for m in self._messages]
scored.sort(key=lambda x: x[1], reverse=True)
# Keep high-importance messages, but preserve tool pairs
self._messages = self._reorder_preserving_tool_pairs(
    [m for m, _ in scored[:keep_count]]
)
```

---

## Configuration

Context managers receive configuration via Mount Plan:

```yaml
session:
  orchestrator: loop-basic
  context: my-context

# Context config can be passed via top-level config
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

---

## Observability

Register compaction events:

```python
coordinator.register_contributor(
    "observability.events",
    "my-context",
    lambda: ["context:pre_compact", "context:post_compact"]
)
```

Standard events to emit:
- `context:pre_compact` - Before compaction (include message_count, token_count)
- `context:post_compact` - After compaction (include new counts)

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/specs/CONTRIBUTION_CHANNELS.md) for the pattern.

---

## Canonical Example

**Reference implementation**: [amplifier-module-context-simple](https://github.com/microsoft/amplifier-module-context-simple)

Study this module for:
- Basic ContextManager implementation
- Token counting approach
- Internal compaction with tool pair preservation

Additional examples:
- [amplifier-module-context-persistent](https://github.com/microsoft/amplifier-module-context-persistent) - File-based persistence

---

## Validation Checklist

### Required

- [ ] Implements all 5 ContextManager protocol methods
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] `get_messages_for_request()` handles compaction internally
- [ ] Compaction preserves tool_use/tool_result pairs
- [ ] Messages returned in conversation order

### Recommended

- [ ] Token counting for accurate compaction triggers
- [ ] Emits context:pre_compact and context:post_compact events
- [ ] Preserves system messages during compaction
- [ ] Thread-safe for concurrent access
- [ ] Configurable thresholds

---

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import MockContextManager

@pytest.mark.asyncio
async def test_context_manager():
    context = MyContextManager(max_tokens=1000)

    # Add messages
    await context.add_message({"role": "user", "content": "Hello"})
    await context.add_message({"role": "assistant", "content": "Hi there!"})

    # Get messages for request (may compact)
    messages = await context.get_messages_for_request()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"

    # Get raw messages (no compaction)
    raw_messages = await context.get_messages()
    assert len(raw_messages) == 2

    # Test clear
    await context.clear()
    assert len(await context.get_messages()) == 0


@pytest.mark.asyncio
async def test_compaction_preserves_tool_pairs():
    """Verify tool_use and tool_result stay together during compaction."""
    context = MyContextManager(max_tokens=100, compaction_threshold=0.5)

    # Add messages including tool sequence
    await context.add_message({"role": "user", "content": "Read file.txt"})
    await context.add_message({
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_123", "type": "function", "function": {...}}]
    })
    await context.add_message({
        "role": "tool",
        "tool_call_id": "call_123",
        "content": "File contents..."
    })

    # Force compaction by adding more messages
    for i in range(50):
        await context.add_message({"role": "user", "content": f"Message {i}"})

    # Get messages for request (triggers compaction)
    messages = await context.get_messages_for_request()

    # Verify tool pairs are preserved
    tool_use_ids = set()
    tool_result_ids = set()
    for msg in messages:
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_use_ids.add(tc.get("id"))
        if msg.get("role") == "tool":
            tool_result_ids.add(msg.get("tool_call_id"))

    # Every tool result should have matching tool use
    assert tool_result_ids.issubset(tool_use_ids), "Orphaned tool results found!"


@pytest.mark.asyncio
async def test_session_resume():
    """Verify set_messages works for session resume."""
    context = MyContextManager(max_tokens=1000)

    saved_messages = [
        {"role": "user", "content": "Previous conversation"},
        {"role": "assistant", "content": "Previous response"}
    ]

    await context.set_messages(saved_messages)

    messages = await context.get_messages()
    assert len(messages) == 2
    assert messages[0]["content"] == "Previous conversation"
```

### MockContextManager for Testing

```python
from amplifier_core.testing import MockContextManager

# For testing orchestrators
context = MockContextManager()

await context.add_message({"role": "user", "content": "Test"})
messages = await context.get_messages_for_request()

# Access internal state for assertions
assert len(context.messages) == 1
```

---

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-context --type context
```

---

**Related**: [README.md](README.md) | [ORCHESTRATOR_CONTRACT.md](ORCHESTRATOR_CONTRACT.md)


---

# Appendix: Module Source Protocol

# Module Source Protocol

_Version: 1.0.0_
_Layer: Kernel Mechanism_
_Status: Specification_

---

## Purpose

The kernel provides a mechanism for custom module source resolution. The loader accepts an optional `ModuleSourceResolver` via mount point injection. If no resolver is provided, the kernel falls back to standard Python entry point discovery.

**How modules are discovered and from where is app-layer policy.**

---

## Kernel Contracts

### ModuleSource Protocol

```python
class ModuleSource(Protocol):
    """Contract for module sources.

    Implementations must resolve to a filesystem path where a Python module
    can be imported.
    """

    def resolve(self) -> Path:
        """
        Resolve source to filesystem path.

        Returns:
            Path: Directory containing importable Python module

        Raises:
            ModuleNotFoundError: Source cannot be resolved
            OSError: Filesystem access error
        """
```

**Examples of conforming implementations (app-layer):**

- FileSource: Resolves local filesystem paths
- GitSource: Clones git repos, caches, returns cache path
- PackageSource: Finds installed Python packages

**Kernel does NOT define these implementations.** They are app-layer policy.

### ModuleSourceResolver Protocol

```python
class ModuleSourceResolver(Protocol):
    """Contract for module source resolution strategies.

    Implementations decide WHERE to find modules based on module ID and
    optional profile hints.
    """

    def resolve(self, module_id: str, profile_hint: Any = None) -> ModuleSource:
        """
        Resolve module ID to a source.

        Args:
            module_id: Module identifier (e.g., "tool-bash")
            profile_hint: Optional hint from profile configuration
                         (format defined by app layer)

        Returns:
            ModuleSource that can be resolved to a path

        Raises:
            ModuleNotFoundError: Module cannot be found by this resolver
        """
```

**The resolver is app-layer policy.** Different apps may use different resolution strategies:

- Development app: Check workspace, then configs, then packages
- Production app: Only use verified packages
- Testing app: Use mock implementations

**Kernel does NOT define resolution strategy.** It only provides the injection mechanism.

---

## Loader Injection Contract

### Module Loader API

```python
class ModuleLoader:
    """Kernel mechanism for loading modules.

    Accepts optional ModuleSourceResolver via coordinator mount point.
    Falls back to direct entry-point discovery if no resolver provided.
    """

    def __init__(self, coordinator):
        """Initialize loader with coordinator."""
        self.coordinator = coordinator

    async def load(self, module_id: str, config: dict = None, profile_source = None):
        """
        Load module using resolver or fallback to direct discovery.

        Args:
            module_id: Module identifier
            config: Optional module configuration
            profile_source: Optional source hint from profile/config

        Raises:
            ModuleNotFoundError: Module not found
            ModuleLoadError: Module found but failed to load
        """
        # Try to get resolver from mount point
        source_resolver = None
        if self.coordinator:
            try:
                source_resolver = self.coordinator.get("module-source-resolver")
            except ValueError:
                pass  # No resolver mounted

        if source_resolver is None:
            # No resolver - use direct entry-point discovery
            return await self._load_direct(module_id, config)

        # Use resolver
        source = source_resolver.resolve(module_id, profile_source)
        module_path = source.resolve()

        # Load from resolved path
        # ... import and mount logic ...
```

### Mounting a Custom Resolver (App-Layer)

```python
# App layer creates resolver (policy)
resolver = CustomModuleSourceResolver()

# Mount it before creating loader
coordinator.mount("module-source-resolver", resolver)

# Loader will use custom resolver
loader = AmplifierModuleLoader(coordinator)
```

**Kernel provides the mount point and fallback. App layer provides the resolver.**

---

## Kernel Responsibilities

**The kernel:**

- ✅ Defines ModuleSource and ModuleSourceResolver protocols
- ✅ Accepts resolver via "module-source-resolver" mount point
- ✅ Falls back to entry point discovery if no resolver
- ✅ Loads module from resolved path
- ✅ Handles module import and mounting

**The kernel does NOT:**

- ❌ Define specific resolution strategies (6-layer, configs, etc.)
- ❌ Parse configuration files (YAML, TOML, JSON, etc.)
- ❌ Know about workspace conventions, git caching, or URIs
- ❌ Provide CLI commands for source management
- ❌ Define profile schemas or source field formats

---

## Error Contracts

### ModuleNotFoundError

```python
class ModuleNotFoundError(Exception):
    """Raised when a module cannot be found.

    Resolvers MUST raise this when all resolution attempts fail.
    Loaders MUST propagate this to callers.

    Message SHOULD be helpful, indicating:
    - What module was requested
    - What resolution attempts were made (if applicable)
    - Suggestions for resolution (if applicable)
    """
```

### ModuleLoadError

```python
class ModuleLoadError(Exception):
    """Raised when a module is found but cannot be loaded.

    Examples:
    - Module path exists but isn't valid Python
    - Import fails due to missing dependencies
    - Module doesn't implement required protocol
    """
```

---

## Fallback Behavior

### Direct Entry Point Discovery (Kernel Default)

When no ModuleSourceResolver is mounted, the kernel falls back to direct entry point discovery via the `_load_direct()` method:

1. Searches Python entry points (group="amplifier.modules")
2. Falls back to filesystem discovery (if search paths configured)
3. Uses standard Python import mechanisms

**Implementation**: The `_load_direct()` method directly calls `_load_entry_point()` and `_load_filesystem()` without creating a resolver wrapper object.

**This ensures the kernel works without any app-layer resolver.**

---

## Example: Custom Resolver (App-Layer)

**Not in kernel, but shown for clarity:**

```python
# App layer defines custom resolution strategy
class MyCustomResolver:
    """Example custom resolver (app-layer policy)."""

    def resolve(self, module_id: str, profile_hint: Any = None) -> ModuleSource:
        # App-specific logic
        if module_id in self.overrides:
            return FileSource(self.overrides[module_id])

        # Fall back to profile hint
        if profile_hint:
            return self.parse_profile_hint(profile_hint)

        # Fall back to some default
        return PackageSource(f"myapp-module-{module_id}")
```

This is **policy, not kernel.** Different apps can implement different strategies.

---

## Kernel Invariants

When implementing custom resolvers:

1. **Must return ModuleSource**: Conforming to protocol
2. **Must raise ModuleNotFoundError**: On failure
3. **Must not interfere with kernel**: No side effects beyond resolution
4. **Must be deterministic**: Same inputs → same output

---

## Related Documentation

**Kernel specifications:**

- [SESSION_FORK_SPECIFICATION.md](./SESSION_FORK_SPECIFICATION.md) - Session forking contracts
- [COORDINATOR_INFRASTRUCTURE_CONTEXT.md](./COORDINATOR_INFRASTRUCTURE_CONTEXT.md) - Mount point system

**Related Specifications:**

- [DESIGN_PHILOSOPHY.md](./DESIGN_PHILOSOPHY.md) - Kernel design principles
- [MOUNT_PLAN_SPECIFICATION.md](./specs/MOUNT_PLAN_SPECIFICATION.md) - Mount plan format

**Note**: Module source resolution implementation is application-layer policy. Applications may implement custom resolution strategies using the protocols defined above.

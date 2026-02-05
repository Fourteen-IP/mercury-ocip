# Developer Documentation

Documentation for developers maintaining or extending the bulk operations system.

## Contents

- [Bulk Operations Overview](./bulk-operations-overview.md) - Architecture and system overview
- [Adding a New Bulk Operation](./adding-bulk-operations.md) - Step-by-step guide for adding new entity types
- [Bulk Operations Reference](./bulk-operations-reference.md) - Quick reference for implementation details

## Quick Start

To add a new bulk operation:

1. Create entity operation class inheriting from `BaseBulkOperations`
2. Define `operation_mapping` with command, nested types, defaults, and integer fields
3. Register in `BulkOperations` gateway class
4. Add CSV template to `assets/bulk sheets/`
5. Add tests

See [Adding a New Bulk Operation](./adding-bulk-operations.md) for detailed steps.


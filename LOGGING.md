# Outfancy Logging System

Outfancy uses Python's standard `logging` module for all internal logging.

## Quick Start

By default, outfancy only shows WARNING and higher level logs. To enable more detailed logging:

```python
import logging
import outfancy.table

# Enable DEBUG logging to see everything
logging.getLogger('outfancy').setLevel(logging.DEBUG)

# Or set to INFO for less verbosity
logging.getLogger('outfancy').setLevel(logging.INFO)

# Now use outfancy normally
table = outfancy.table.Table()
result = table.render(data)
```

## Log Levels

Outfancy uses the following log levels:

### DEBUG
Detailed information for diagnosing issues:
- Function entry/exit points
- Configuration values
- Internal calculations

```python
# Example output:
# 2026-02-03 18:18:08 - outfancy - DEBUG - Starting Table.render()
# 2026-02-03 18:18:08 - outfancy - DEBUG - check_data = False
# 2026-02-03 18:18:08 - outfancy - DEBUG - LargeTable rendering 3 rows
```

### INFO
Confirmation that things are working as expected:
- Successful rendering completions
- Major operations completed

```python
# Example output:
# 2026-02-03 18:18:08 - outfancy - INFO - LargeTable rendered 3 rows successfully
```

### WARNING
Indication that something unexpected happened, but the library handled it:
- Parameters were rebuilt automatically
- Non-optimal configurations detected
- Fallback behaviors triggered

```python
# Example output:
# 2026-02-03 18:18:08 - outfancy - WARNING - label_list was rebuilt
```

### ERROR
A more serious problem occurred, but execution continued:
- Invalid data detected
- Required parameters missing and couldn't be rebuilt
- Validation failures

```python
# Example output:
# 2026-02-03 18:18:08 - outfancy - ERROR - Data integrity check failed
```

## Custom Configuration

You can customize the logging format and handlers:

```python
import logging

# Get the outfancy logger
logger = logging.getLogger('outfancy')

# Remove default handler if you want custom formatting
logger.handlers.clear()

# Add your own handler with custom formatting
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(levelname)s [%(name)s]: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set level
logger.setLevel(logging.DEBUG)
```

## Logging to File

```python
import logging

logger = logging.getLogger('outfancy')
logger.setLevel(logging.DEBUG)

# Add file handler
file_handler = logging.FileHandler('outfancy.log')
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
logger.addHandler(file_handler)
```

## Disable Logging

To completely silence outfancy logs:

```python
import logging

logging.getLogger('outfancy').setLevel(logging.CRITICAL)
# Or
logging.getLogger('outfancy').disabled = True
```

## API Changes

### show_* Methods
All `show_*` methods now **return values** instead of printing:

```python
# Old behavior (printed to console):
table.show_check_data()  # Printed: False

# New behavior (returns value):
value = table.show_check_data()  # Returns: False
print(value)  # You control output
```

The methods still log at DEBUG level for debugging purposes.

### LargeTable.render()
Now **returns a string** instead of printing directly:

```python
# Old behavior (printed directly):
large = LargeTable()
large.render(data)  # Printed to stdout

# New behavior (returns string):
large = LargeTable()
result = large.render(data)  # Returns string
print(result)  # You control when to print
```

## Best Practices

1. **Development**: Use `DEBUG` level to see everything
2. **Production**: Use `WARNING` level (default) to only see issues
3. **Testing**: Use `ERROR` level to only see actual problems
4. **Custom handlers**: Add file handlers in production for log persistence
5. **Per-module logging**: You can set different levels for different parts of your app

## Example: Production Configuration

```python
import logging
import outfancy.table

# Configure logging for production
logger = logging.getLogger('outfancy')
logger.setLevel(logging.WARNING)

# Add file handler for errors
error_handler = logging.FileHandler('outfancy_errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
logger.addHandler(error_handler)

# Use library normally
table = outfancy.table.Table()
result = table.render(data)
```

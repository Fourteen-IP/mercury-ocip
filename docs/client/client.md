# Client

The `Client` class is your main way to send messages to BroadWorks servers. It handles connection, authentication, and command execution. This is a synchronous client, so each call blocks until it finishes. If you need async, see [ocip-fast](https://mercury-fast-docs.14ip.net).

## What it does

All methods block until they complete. This works well for scripts, admin tools, and anywhere you want straightforward sequential execution.

The client logs in automatically when you create it. You pass credentials, it authenticates, done.

When you call `disconnect()`, network resources get cleaned up properly.

Errors include actual information about what went wrong instead of generic failures.

---

## Quick start

Connect, run a command, clean up:

```python
from mercury_ocip.client import Client
from mercury_ocip.commands.commands import UserGetListInSystemRequest

def get_users():
    client = Client(
        host="https://your-broadworks.com",
        port=2209,
        username="admin",
        password="secret123",
        conn_type="SOAP"  # or "TCP"
    )

    try:
        response = client.command(UserGetListInSystemRequest())
        return response.user_table  # Access the actual data
    finally:
        client.disconnect()  # Clean up and disconnect

users = get_users()
print(f"Found {len(users)} users")
```

## Connection types

SOAP works for most cases:
```python
client = Client(
    host="https://your-server.com",  # No /wsdl suffix needed
    username="your_user",
    password="your_pass",
    conn_type="SOAP"
)
```

TCP if you need it:
```python
client = Client(
    host="broadworks.company.com",
    port=2209,  # Usually 2209/2208 for TCP
    username="admin",
    password="password",
    conn_type="TCP",
    tls=True  # Set False for unencrypted (not recommended)
)
```

## Running commands

Using command classes (you get type hints and autocompletion):
```python
from mercury_ocip.commands.commands import GroupHuntGroupGetInstanceRequest20

response = client.command(
    GroupHuntGroupGetInstanceRequest20(
        group_id="MyGroup",
        service_provider_id="MyProvider"
    )
)

print(f"Hunt Group: {response}")
```

Using raw commands when you know the exact command name:
```python
# Same as above, but as a string
response = client.raw_command(
    "GroupHuntGroupGetInstanceRequest20",
    group_id="MyGroup",
    service_provider_id="MyProvider"
)
```

## Practical examples

Bulk user operations:
```python
def update_users_in_bulk():
    client = Client(
        host="https://broadworks.example.com",
        username="admin",
        password="admin123",
        conn_type="SOAP"
    )

    try:
        # Get all users
        users_resp = client.command(UserGetListInSystemRequest())

        # Process each user
        for user in users_resp.user_table:
            # Get detailed user info
            user_detail = client.command(
                UserGetRequest23V2(
                    user_id=user.user_id
                )
            )

            # Make some changes
            if user_detail.department == "Sales":
                client.command(
                    UserModifyRequest22(
                        user_id=user.user_id,
                        department="Business Development"
                    )
                )
                print(f"Updated {user.user_id}")

    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        client.disconnect()
```

Custom logging setup:
```python
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_broadworks_app")

client = Client(
    host="https://broadworks.example.com/webservice/services/ProvisioningService",
    username="service_account",
    password="complex_password_123",
    conn_type="SOAP",
    timeout=60,  # 60 seconds for slow operations
    user_agent="My Admin Tool v1.0",  # Shows up in logs
    logger=logger,  # Your custom logger
)

# Use DEBUG to see exact commands sent and received
logging.basicConfig(level=logging.DEBUG)
```

## Example debug log

```plaintext
DEBUG:zeep.transports:HTTP Post to https://broadworks.example.com/webservice/services/ProvisioningService:
b'
<?xml version=\'1.0\' encoding=\'utf-8\'?>\n
<soap-env:Envelope
	xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
	<soap-env:Body>
		<ns0:processOCIMessage
			xmlns:ns0="urn:com:broadsoft:webservice">
			<ns0:in0>&lt;?xml version=\'1.0\' encoding=\'ISO-8859-1\'?&gt;\n&lt;BroadsoftDocument
				xmlns="C"
				xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" protocol="OCI"&gt;&lt;sessionId
				xmlns=""&gt;12345678-1234-1234-1234-123456789abc&lt;/sessionId&gt;&lt;command
				xmlns="" xsi:type="LoginRequest22V5"&gt;&lt;userId&gt;example_user&lt;/userId&gt;&lt;password&gt;example_password&lt;/password&gt;&lt;/command&gt;&lt;/BroadsoftDocument&gt;
			</ns0:in0>
		</ns0:processOCIMessage>
	</soap-env:Body>
</soap-env:Envelope>'
DEBUG:httpcore.connection:connect_tcp.started host='broadworks.example.com' port=443 local_address=None timeout=5.0 socket_options=None
```

## Error handling

Wrap your client operations:
```python
from mercury_ocip.exceptions import MError

try:
    response = client.command(SomeCommand())
    # Process response...
except MError as e:
    print(f"BroadWorks error: {e}")
    # Handle specific BroadWorks errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle network issues, etc.
finally:
    client.disconnect()
```

## Checking for error responses

You can type-hint responses to handle errors explicitly:
```python
from mercury_ocip.commands import GroupHuntGroupGetInstanceRequest20, GroupHuntGroupGetInstanceResponse20
from mercury_ocip.commands.base_command import ErrorResponse
from mercury_ocip.libs.types import OCIResponse

response: OCIResponse[GroupHuntGroupGetInstanceResponse20] = client.command(
    GroupHuntGroupGetInstanceRequest20(
        group_id="MyGroup",
        service_provider_id="MyProvider"
    )
)

if isinstance(response, ErrorResponse):
    print(f"Request failed: {response.errorCode}: {response.summary}")
else:
    print(f"Hunt Group: {response}")
```

## Tips

Reuse connections. Don't create a new client for every command. One client handles many requests.

Check authentication status with `client.authenticated` if you need to.

SOAP is usually easier to work with. Use TCP only if you have specific requirements.

Only use `tls=False` for development or on a completely trusted network.

Increase timeout for slow operations like bulk imports.

::: mercury_ocip.client.Client

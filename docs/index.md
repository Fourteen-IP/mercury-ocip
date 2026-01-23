# Mercury

Mercury is an SDK for interfacing with BroadWorks OCI-P via TCP or SOAP.

- [Documentation](https://mercury-docs.14ip.net/)

---

## Overview

Mercury handles connection management, authentication, and command execution for BroadWorks. It includes automation tools and bulk operations built from real-world experience managing BroadWorks instances.

The package is maintained by the Dev Team at [Fourteen IP](https://fourteenip.com/). The team works alongside platform and telephony engineers with decades of BroadWorks experience.

---

!!! Warning "Important Legal Notice"
    Mercury is an independent, open-source project and is NOT affiliated with, endorsed by, or supported by Cisco Systems, Inc.

    BroadWorks is a product and trademark of Cisco Systems, Inc. Mercury provides a client interface to interact with BroadWorks systems via the Open Client Interface Protocol (OCI-P).

    Mercury does not bypass, circumvent, or provide any additional permissions or licenses. To use Mercury, you must:

    * Have an active, licensed BroadWorks system from Cisco
    * Possess valid credentials and appropriate access permissions
    * Comply with all Cisco licensing terms and agreements

    The OCI-P commands implemented in Mercury are generated from XML schemas. These schemas are:

    `Copyright © 2018 BroadSoft Inc. (now part of Cisco Systems, Inc.)
    All rights reserved.`

    Mercury implements these publicly documented interfaces and does not include any proprietary Cisco code or intellectual property. All command structures follow the official OCI-P specification.

---

## Features

* SOAP and TCP connections to BroadWorks OCI-P
* Type-safe command classes with serialization handled for you
* Async client for concurrent operations
* Bulk operations and automations for common admin tasks

> If you'd like to request a feature, please raise an issue with details.

---

## Installation

```bash
pip install mercury-ocip
```

### Basic usage

```python
from mercury_ocip import Client

# SOAP (works for most cases)
client = Client(
    host="https://your-server.com",  # No /wsdl suffix needed
    username="your_user",
    password="your_pass",
    conn_type="SOAP"
)

# TCP
client = Client(
    host="broadworks.company.com",
    port=2209,
    username="admin",
    password="password",
    conn_type="TCP",
    tls=True  # Set False for unencrypted (not recommended)
)

# Run a command
response = client.raw_command("SystemSoftwareVersionGetRequest")

print(response)
# Returns: SystemSoftwareVersionGetResponse(version='24')

print(response.to_dict())
# Returns: {'version': '24'}

print(response.to_xml())
# Returns: <command ... "SystemSoftwareVersionGetResponse"><version>24</version></command>
```

---

### Agent usage

```python
from mercury_ocip import Client, Agent

client = Client(
    host="url",
    username="username",
    password="password",
)

agent = Agent.get_instance(client)

agent.automate.find_alias(
    "serviceProvider",
    "groupId",
    alias="alias@sp.com"
)  # Returns BroadWorks entity where alias is assigned

agent.bulk.create_users_from_csv(
    path="local/file/path"
)  # Creates users from CSV
```

---

## Credits

This package builds upon the excellent work of the BroadWorks OCI-P Interface package. Special thanks to:

[@nigelm (Nigel Metheringham)](https://github.com/nigelm/) – Developer of the original Python version.

Karol Skibiński – For testing, bug reporting, and contributions.

[@ewurch (Eduardo Würch)](https://github.com/ewurch) – For contributing the R25 schema update and other improvements.
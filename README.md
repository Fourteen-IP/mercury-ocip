# Mercury

[![Downloads](https://static.pepy.tech/badge/mercury-ocip)](https://pepy.tech/project/mercury-ocip)
[![Downloads](https://static.pepy.tech/badge/mercury-ocip/month)](https://pepy.tech/project/mercury-ocip)
[![Downloads](https://static.pepy.tech/badge/mercury-ocip/week)](https://pepy.tech/project/mercury-ocip)
[![pypi version](https://img.shields.io/pypi/v/mercury-ocip.svg)](https://pypi.python.org/pypi/mercury-ocip)

**Mercury** is an SDK for interfacing with Broadworks OCIP interface either via TCP or SOAP.

- [Documentation](https://mercury-docs.14ip.net/)

---

## Overview

**Mercury** has extensive documentation, automation, and more to better manage Broadworks instances.

The package is currently actively managed by the Dev Team at [Fourteen IP](https://fourteenip.com/) the leading solution of hosted telephony in the hospitality industry. The team is working with the whole company including platform and telephony engineers with decades of experience.

The goal of the solution is to ease the management of Broadworks and give engineers tooling to better configure and administrate.

---

## Important Legal Notice

Mercury is an independent, open-source project and is NOT affiliated with, endorsed by, or supported by Cisco Systems, Inc.

BroadWorks is a product and trademark of Cisco Systems, Inc. Mercury provides a client  interface to interact with BroadWorks systems via the Open Client Interface Protocol(OCI-P).

Mercury does not bypass, circumvent, or provide any additional permissions or licenses. To  use Mercury, you must:
- Have an active, licensed BroadWorks system from Cisco
- Possess valid credentials and appropriate access permissions
- Comply with all Cisco licensing terms and agreements

The OCI-P commands implemented in Mercury are generated from XML schemas. These schemas are:

`Copyright © 2018 BroadSoft Inc. (now part of Cisco Systems, Inc.)
All rights reserved.`

Mercury implements these publicly documented interfaces and does not include any    proprietary Cisco code or intellectual property. All command structures follow the     official OCI-P specification.

---

## Features

* Interface with Broadworks OCIP via SOAP or TCP
* Command logic to seamlessly use API
* Asynchronous version
* Bulk and automated features (Requested by Broadworks engineers with decades of experience)
 
> If you would like to submit a feature request please raise an issue detailing your request.

---

## Installation

Install Mercury using pip:

```bash
pip install mercury-ocip
```

### Basic Usage

Here's a simple example to get you started:

```python
from mercury import Client

#SOAP (recommended for most cases):
client = Client(
    host="https://your-server.com",  # No /wsdl suffix needed
    username="your_user",
    password="your_pass",
    conn_type="SOAP"
)

#TCP (for legacy systems or specific requirements):
client = AsyncClient(
    host="broadworks.company.com",
    port=2209,  # Usually 2209/2208 for TCP
    username="admin",
    password="password",
    conn_type="TCP",
    tls=True  # Set False for unencrypted (not recommended)
)

# example usage
response = client.raw_command("SystemSoftwareVersionGetRequest")

print(response)
# Returns: SystemSoftwareVersionGetResponse(version='24')

print(response.to_dict()) 
# Returns: {'version': '24'}

print(response.to_json()) 
# Returns: '{'version': '24'}'

print(response.to_xml()) 
# Returns: <command ... "SystemSoftwareVersionGetResponse"><version>24</version></command>
```

---

### Agent Usage (In Development)

Here's a simple example to get you started:

```python
from mercury import Client, Agent

client = Client(
    host="url",
    username="username",
    password="password",
)

agent = Agent.get_instance(client)

agent.automate.find_alias(
    "servicePovider",
    "groupId",
    alias=0
) # returns Broadworks enity where alias is assigned.

agent.bulk.create_users_from_csv(
    path="local/file/path"
) # Bulk builds all users in predefined bulk sheet
```

---

## Credits

This package builds upon the excellent work of the Broadworks OCI-P Interface package. Special thanks to:

[@nigelm (Nigel Metheringham)](https://github.com/nigelm/) – Developer of the original Python version.

Karol Skibiński – For extensive testing, bug reporting, and valuable contributions.

[@ewurch (Eduardo Würch)](https://github.com/ewurch) – For contributing the R25 schema update and other improvements.

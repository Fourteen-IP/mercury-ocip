# Automations

The automations command provides automated operations for various entities.

## Usage

```asciinema-player
{
    "file": "/assets/asciinema/find_alias.cast",
    "title": "Find Alias Showcase",
    "mkap_theme": "none",
    "theme": "dracula",
    "fit": "width",
    "cols": 120,
    "rows": 24,
    "autoplay": true
}
```

```
automations <operation> [parameters...]
```

---

## Operations

### find_alias

Finds the entity (user) behind a given alias number.

- Parameters:
    * `service_provider_id` - The Service Provider ID
    * `group_id` - The Group ID
    * `alias` - The alias number to look up

**Example:**
```bash title="Find Alias"
automations find_alias SP123 GROUP456 1234
```

#### Output

**Success:** Shows the user ID associated with the alias.

```
✔ Alias '1234' found: user@example.com
```

**Failure:** Shows that the alias was not found.

```
✘ Alias '1234' not found.
```

---

### group_audit

Performs a comprehensive audit of a group, displaying detailed information about group configuration, service authorizations, and directory numbers.

- Parameters:
    * `service_provider_id` - The Service Provider ID
    * `group_id` - The Group ID

**Example:**
```bash title="Group Audit"
automations group_audit SP123 HOTEL_MAIN
```

#### Output

**Success:** Displays a comprehensive audit report with the following sections:

- **Group Details:** Group name, ID, service provider ID, default domain, user count, time zone, and calling line ID information
- **Group Services Authorization:** List of group-level services and their authorization counts
- **Service Packs Authorization:** List of service packs and their authorization counts
- **User Services Authorization:** List of user-level services and their authorization counts
- **Group Directory Numbers:** Total count and list of all directory numbers assigned to the group

```
╔══════════════════════════════════════════╗
║        GROUP AUDIT REPORT                ║
╚══════════════════════════════════════════╝

📋 GROUP DETAILS
────────────────────────────────────────────────────────────────────────────────
  Group Name:              Grand Hotel
  Group ID:                HOTEL_MAIN
  Service Provider ID:     SP123
  Default Domain:          hotel.example.com
  User Count:              85 / 200
  Time Zone:               (GMT) Greenwich Mean Time
  Calling Line ID Name:    Grand Hotel
  Calling Line ID Phone:   +442012345678
  Display Phone Number:    02012345678

🔧 GROUP SERVICES AUTHORIZATION
────────────────────────────────────────────────────────────────────────────────
  Account/Authorization Codes                  1
  Auto Attendant                               3
  Call Capacity Management                     1
  Call Pickup                                  8
  Enhanced Outgoing Calling Plan               1
  Group Paging                                 2
  Hunt Group                                  15
  Incoming Calling Plan                        1
  Inventory Report                             1
  Music On Hold                                1
  Outgoing Calling Plan                        1
  Trunk Group                                  5
  VoiceXML                                     1

📦 SERVICE PACKS AUTHORIZATION
────────────────────────────────────────────────────────────────────────────────
  service_pack_name_1                          20
  service_pack_name_2                           1
  service_pack_name_3                           8
  service_pack_name_4                           1
  service_pack_name_5                           1


👤 USER SERVICES AUTHORIZATION
────────────────────────────────────────────────────────────────────────────────
  Alternate Numbers                            2
  Authentication                               1
  Call Center Monitoring                       1
  Call Forwarding Always                       1
  Call Forwarding Busy                         2
  Call Forwarding Selective                    4
  Call Me Now                                  3
  Call Recording                               1
  Call Transfer                                1
  Integrated IMP                               1
  Music On Hold User                           1
  Privacy                                      1
  Selective Call Acceptance                    1
  Selective Call Rejection                    1
  Shared Call Appearance                       2
  Third-Party Voice Mail Support               1
  Voice Messaging User                         4

📞 GROUP DIRECTORY NUMBERS
────────────────────────────────────────────────────────────────────────────────
  Total DNs: 142
  +44-2012345678, +44-2012345679, +44-2012345680, +44-2012345681,
  +44-2012345682, +44-2012345683, +44-2012345684, +44-2012345685,
  +44-2012345686, +44-2012345687, +44-2012345688, +44-2012345689,
  +44-2012345690, +44-2012345691, +44-2012345692, +44-2012345693,
  +44-2012345694, +44-2012345695, +44-2012345696, +44-2012345697,
  ...

────────────────────────────────────────────────────────────────────────────────
```

**Failure:** Shows that the group audit failed.

```
✘ Group audit failed for Group ID 'HOTEL_MAIN'.
```

---

### user_digest

Performs a comprehensive audit of a user, displaying detailed information about user configuration, memberships to call centers, hunt groups, pickup groups, forwardings, registered devices, and general information.

- Parameters:
    * `user_id` - The User ID

**Example:**
```bash title="User Audit"
automations user_digest USER123
```

#### Output
```
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                          User Digest Report                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────── Basic Info ─────────────────────────────────────────────────────────────╮
│   Name                    this user has everything      Extension               3457           DND                    🔇 ON          │
│   ID                      userll@ps-soss.1333.cof       Phone                   5550123456     Trunked                ✗              │
│   Service Provider        SERVICE                       Group                   GROUP          CLID                   +15550123456   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────────────────── Active Forwards ───────────────────────────────────────────────────────────╮
│                                              Always: 5747457457457457 | No Answer: 1111                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────── Selective Call Forwarding ──────────────────────────────────────────────────────╮
│                                                                                                                                      │
│   Criteria Name                          Forward To                     Time Schedule                          Call From             │
│  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────  │
│   you know the one!                      2873462978346                  Every Day All Day                      All calls             │
│                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────── Active VM Forwards ─────────────────────────────────────────────────────────╮
│                           Always Redirect To Vm: ✓ | Busy Redirect To Vm: ✓ | No Answer Redirect To Vm: ✓                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Memberships                                                                                                                          │
│ ├── 📞 Call Centers                                                                                                                  │
│ │   ├── Accounts - GROUPAccountsCC@ps-soss.1333.cof - Unavailable - Available for CC ✗                                               │
│ │   └── MichaelTestCC - TestCallCenter@ps-soss.1333.cof - Unavailable - Available for CC ✓                                           │
│ ├── 🎯 Hunt Groups                                                                                                                   │
│ │   └── Front Desk - FrontDesk@ps-soss.1333.cof                                                                                      │
│ └── 📫 Call Pickup Groups                                                                                                            │
│     └── kashdkjahsdkj                                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Failure:** Shows that the digest failed.

```
✘ Digest failed for User ID 'USER123'.
```

### call_center_digest

Performs a detailed report of the given Call Center, including its profile settings and the status of all agents within it.

- Parameters:
    * `service_user_id` - The ID Of the Call Center

**Example:**
```bash title="Call Center Digest"
automations call_center_digest TESTAA123456@domain.com
```
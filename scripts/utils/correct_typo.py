import re
from difflib import get_close_matches
from itertools import product
from typing import Optional

CORRECT_WORDS: list[str] = [
    "Abandoned",
    "Acceptance",
    "Access",
    "Account",
    "Accounting",
    "Accounts",
    "ACL",
    "Action",
    "Activatable",
    "Activate",
    "Activated",
    "Activation",
    "Active",
    "Add",
    "Additional",
    "Address",
    "Addresses",
    "Addressing",
    "Admin",
    "Administrator",
    "Admission",
    "Advanced",
    "Advice",
    "Agent",
    "Agents",
    "Alert",
    "Alerting",
    "Alias",
    "All",
    "Allowed",
    "Alternate",
    "Always",
    "And",
    "Announcement",
    "Anonymous",
    "Answer",
    "Anywhere",
    "Appearance",
    "Application",
    "Apply",
    "ASR",
    "Assign",
    "Assignable",
    "Assigned",
    "Assignment",
    "Assistant",
    "Association",
    "Attendant",
    "Attribute",
    "Audit",
    "Auth",
    "Authentication",
    "Authorization",
    "Authorize",
    "Authorized",
    "Auto",
    "Automatic",
    "Availability",
    "Available",
    "Avp",
    "Away",
    "Barge",
    "Barring",
    "Base",
    "Based",
    "Basic",
    "BCCT",
    "Blocking",
    "Body",
    "Bounced",
    "Branding",
    "Bridge",
    "Broad",
    "Broadworks",
    "Business",
    "Busy",
    "Bw",
    "By",
    "Bypass",
    "Cache",
    "Call",
    "Callback",
    "Caller",
    "Calling",
    "Cancel",
    "Capacity",
    "Capture",
    "Carrier",
    "Category",
    "Cause",
    "Center",
    "Change",
    "Charge",
    "Charging",
    "Class",
    "Classification",
    "Classmark",
    "Clear",
    "CLID",
    "Client",
    "Closed",
    "Cloud",
    "Cluster",
    "Code",
    "Codec",
    "Codes",
    "Collaborate",
    "Collect",
    "Collection",
    "Combined",
    "Comfort",
    "Comm",
    "Common",
    "Communication",
    "Communicator",
    "Completed",
    "Completion",
    "Compose",
    "Composed",
    "Conference",
    "Conferencing",
    "Config",
    "Configurable",
    "Configuration",
    "Confirmation",
    "Connected",
    "Connection",
    "Connections",
    "Consolidated",
    "Contact",
    "Content",
    "Control",
    "Controller",
    "Copy",
    "Cost",
    "Count",
    "Country",
    "CPE",
    "Cr",
    "Create",
    "Created",
    "Creation",
    "Criteria",
    "Current",
    "Custom",
    "Customer",
    "Customization",
    "D",
    "Data",
    "Dates",
    "DAV",
    "DAV20",
    "Deactivate",
    "Default",
    "Delegate",
    "Delete",
    "Delivery",
    "Department",
    "Deposit",
    "Description",
    "Desk",
    "Destination",
    "Detail",
    "Detailed",
    "Details",
    "Device",
    "Dial",
    "Dialable",
    "Dialing",
    "Diameter",
    "Digit",
    "Digits",
    "Direct",
    "Directed",
    "Directory",
    "Disable",
    "Display",
    "Disposition",
    "Distinctive",
    "Distribution",
    "Disturb",
    "Diversion",
    "DN",
    "Dn",
    "DNIS",
    "DNSIPUR",
    "Do",
    "Domain",
    "Dry",
    "DTMF",
    "Duration",
    "Effect",
    "Element",
    "Email",
    "Emergency",
    "Enabled",
    "Endpoint",
    "Enhanced",
    "Enterprise",
    "Entry",
    "Estimated",
    "Event",
    "Events",
    "Exact",
    "Exception",
    "Exchange",
    "Exclusion",
    "Execution",
    "Executive",
    "Exempt",
    "Existing",
    "Expensive",
    "Export",
    "Express",
    "Extended",
    "Extension",
    "Extensions",
    "External",
    "Failover",
    "Family",
    "Fax",
    "Feature",
    "Field",
    "File",
    "Filter",
    "Filtering",
    "Find",
    "First",
    "Flag",
    "Flexible",
    "Follow",
    "For",
    "Force",
    "Forced",
    "Formatting",
    "Forward",
    "Forwarded",
    "Forwarding",
    "From",
    "FTP16",
    "Fully",
    "Function",
    "Gateway",
    "Generate",
    "Geographic",
    "Geographical",
    "Get",
    "GETS",
    "Global",
    "Grace",
    "Greeting",
    "Greetings",
    "Group",
    "Groups",
    "Guest",
    "Hierarchical",
    "Hold",
    "Holiday",
    "Home",
    "Host",
    "Hosted",
    "Hoteling",
    "Hotline",
    "Hour",
    "HPBX",
    "Hunt",
    "Hunting",
    "ID",
    "Id",
    "Identification",
    "Identifiers",
    "Identity",
    "IMP",
    "Imp",
    "Import",
    "IMRN",
    "IN",
    "In",
    "Inclusions",
    "Incoming",
    "Indicator",
    "Info",
    "Information",
    "Inhibited",
    "Instance",
    "Instant",
    "Int",
    "Integrated",
    "Integration",
    "Intercept",
    "Interface",
    "Internal",
    "Interval",
    "Introduction",
    "Inventory",
    "Ior",
    "IP",
    "Is",
    "Key",
    "Keys",
    "Labeled",
    "Lamp",
    "Language",
    "Last",
    "Leaf",
    "Legacy",
    "Length",
    "Level",
    "License",
    "Licensing",
    "Line",
    "Link",
    "Linked",
    "List",
    "Lists",
    "Lived",
    "Local",
    "Location",
    "Lockout",
    "Logic",
    "Login",
    "Logout",
    "Logs",
    "Long",
    "Lookup",
    "MAC",
    "Mail",
    "Main",
    "Malicious",
    "Management",
    "Manipulation",
    "Manual",
    "Map",
    "Mapping",
    "Max",
    "Maximum",
    "Mcc",
    "Me",
    "Measurement",
    "Media",
    "Meet",
    "Meetings",
    "Members",
    "Menu",
    "Menus",
    "Message",
    "Messages",
    "Messaging",
    "MGCP",
    "Migrated",
    "Migration",
    "Minute",
    "Mixed",
    "Mnc",
    "Mobile",
    "Mobility",
    "Modify",
    "Monitor",
    "Monitoring",
    "Monitors",
    "Move",
    "Mp",
    "Msc",
    "Multi",
    "Multimedia",
    "Multiple",
    "Music",
    "MWI",
    "My",
    "Name",
    "Names",
    "Native",
    "NCOS",
    "Negative",
    "Net",
    "Network",
    "New",
    "Night",
    "No",
    "Non",
    "Nor",
    "Not",
    "Note",
    "Notification",
    "Notify",
    "Now",
    "Number",
    "Numbers",
    "Numeric",
    "OCI",
    "Of",
    "Office",
    "On",
    "Only",
    "Opt",
    "Option",
    "Optional",
    "Options",
    "Or",
    "Order",
    "Ordered",
    "Organization",
    "Originated",
    "Originating",
    "Origination",
    "Originator",
    "Out",
    "Outbound",
    "Outgoing",
    "Overflow",
    "Override",
    "Pack",
    "Paged",
    "Paging",
    "Pair",
    "Param",
    "Parameter",
    "Parameters",
    "Parent",
    "Park",
    "Part",
    "Participants",
    "Party",
    "Passcode",
    "Password",
    "Past",
    "Pattern",
    "PBX",
    "Peer",
    "Pending",
    "Performance",
    "Period",
    "Permission",
    "Permissions",
    "Person",
    "Personal",
    "Personalized",
    "Phone",
    "Physical",
    "Pickup",
    "Pilot",
    "Pinhole",
    "Place",
    "Plan",
    "Platform",
    "Play",
    "Point",
    "Policies",
    "Policy",
    "Polycom",
    "Pool",
    "Port",
    "Portability",
    "Portal",
    "Ports",
    "Positive",
    "Pre",
    "Preferred",
    "Prefix",
    "Prepaid",
    "Presentation",
    "Primary",
    "Priority",
    "Privacy",
    "Private",
    "Processing",
    "Profile",
    "Profiles",
    "Progress",
    "Progression",
    "Project",
    "Properties",
    "Protection",
    "Protocol",
    "Provider",
    "Province",
    "Provisioning",
    "Proxy",
    "Public",
    "Publication",
    "Push",
    "Put",
    "Q850",
    "Qualified",
    "Query",
    "Queue",
    "Radius",
    "Random",
    "Range",
    "Ranges",
    "Reachability",
    "Reachable",
    "Read",
    "Realm",
    "Reason",
    "Rebuild",
    "Recall",
    "Receptionist",
    "Record",
    "Recording",
    "Recurrence",
    "Redirected",
    "Redirecting",
    "Redirection",
    "Redundancy",
    "Refresh",
    "Regenerate",
    "Region",
    "Registration",
    "Rejection",
    "Release",
    "Reload",
    "Remote",
    "Removal",
    "Rename",
    "Reorder",
    "Replacement",
    "Reply",
    "Report",
    "Reporting",
    "Repository",
    "Request",
    "Required",
    "Reseller",
    "Reserved",
    "Reset",
    "Resource",
    "Response",
    "Restriction",
    "Restrictions",
    "Retrieval",
    "Retrieve",
    "Return",
    "Review",
    "Revoke",
    "RI",
    "Ring",
    "Ringback",
    "Ringing",
    "Roaming",
    "Room",
    "Route",
    "Routing",
    "Row",
    "Rule",
    "Rules",
    "Run",
    "Runtime",
    "S",
    "Schedule",
    "Scheduled",
    "Schema",
    "Screening",
    "Search",
    "Searched",
    "Seating",
    "Secondary",
    "Security",
    "Select",
    "Selected",
    "Selection",
    "Selective",
    "Send",
    "Sequential",
    "Serial",
    "Series",
    "Server",
    "Service",
    "Services",
    "Session",
    "Set",
    "Setting",
    "Settings",
    "Sh",
    "Shaken",
    "Shared",
    "Sign",
    "Signaling",
    "Silent",
    "Simultaneous",
    "Single",
    "SIP",
    "Sip",
    "SIPURI",
    "Size",
    "Skill",
    "Skilled",
    "Small",
    "SMDI",
    "SMDIMWI",
    "SMPP",
    "Software",
    "Sort",
    "Sorted",
    "Source",
    "Speed",
    "Stage",
    "Stale",
    "Start",
    "State",
    "Statistics",
    "Status",
    "Stir",
    "Stranded",
    "Street",
    "Submenu",
    "Subscriber",
    "Subscription",
    "Summary",
    "Supervised",
    "Supervisor",
    "Support",
    "Sustained",
    "Switch",
    "Sync",
    "Synching",
    "System",
    "Table",
    "Tag",
    "Tags",
    "Talk",
    "Target",
    "Targets",
    "Task",
    "Template",
    "Terminate",
    "Terminating",
    "Termination",
    "Test",
    "Third",
    "Threshold",
    "Thresholds",
    "Time",
    "Title",
    "To",
    "Token",
    "Trace",
    "Tracking",
    "Transfer",
    "Translation",
    "Transmission",
    "Treatment",
    "Tree",
    "Trunk",
    "Tutorial",
    "Two",
    "Type",
    "Unassign",
    "Unavailable",
    "Unbounded",
    "Unlicensed",
    "Unlink",
    "Unreachable",
    "Update",
    "URI",
    "URL",
    "Usage",
    "User",
    "Users",
    "Using",
    "Utilization",
    "V13",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V9",
    "Valid",
    "Validation",
    "Value",
    "Verify",
    "Version",
    "Video",
    "Virtual",
    "Visual",
    "Voice",
    "VPN",
    "Wait",
    "Waiting",
    "Web",
    "Webex",
    "Weight",
    "Weighted",
    "White",
    "With",
    "Works",
    "XML",
    "Xml",
    "Xsi",
    "Yahoo",
    "Zone",
    "Zones",
]


def find_missing_parts(request: str, response: str) -> list[str]:
    """
    Identify word fragments that appear in a request/command name but are absent
    from a corresponding response name.

    Args:
        request: class name (e.g. "SystemMediaGroupUsageListRequest").
        response: class name that may be missing fragments (e.g. "SystemMediaGroupUsageResponse").

    Returns:
        A list of string fragments present in `request` but not in `response`.
        If there are no missing fragments, returns an empty list.
    """
    word_re = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+[0-9]*|[0-9]+")

    request_base = request.replace("Request", "").replace("Response", "")
    response_base = response.replace("Request", "").replace("Response", "")

    request_parts = word_re.findall(request_base)
    response_parts = word_re.findall(response_base)

    missing = []

    for part in request_parts:
        if part not in response_parts:
            missing.append(part)

    return missing


def reconstruct_missing_parts(request: str, response: str) -> str | None:
    """
    Reconstruct a probable, fully-qualified response class name by inserting
    missing fragments from the corresponding request name.

    The routine:
      - strips "Request"/"Response" suffixes and attempts to parse/ignore
        version tokens,
      - splits both names into CamelCase fragments,
      - aligns fragments from `request` and `response` while preserving the
        request order,
      - treats singular/plural and close fuzzy matches as equivalent (so
        "Range" and "Ranges" are considered similar),
      - prefers the request fragment when minor variants differ,
      - inserts any request fragments missing from the response in the
        appropriate positions.

    Similarity is determined by exact equality, simple singular/plural
    normalization, or a difflib.get_close_matches fuzzy comparison
    (cutoff=0.8).

    Args:
        request: Source request/class name (e.g. "SystemMediaGroupUsageListRequest").
        response: Target response name that may be missing fragments
                  (e.g. "SystemMediaGroupUsageResponse").

    Returns:
        A reconstructed CamelCase response name ending with "Response"
        (e.g. "SystemMediaGroupUsageListResponse") if reconstruction is
        possible; otherwise None.
    """

    def similar(a: str, b: str) -> bool:
        if a == b:
            return True
        if a.lower() + "s" == b.lower() or b.lower() + "s" == a.lower():
            return True

        return bool(get_close_matches(a, [b], n=1, cutoff=0.8))

    word_re = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+[0-9]*|[0-9]+")

    req_base = request.replace("Request", "").replace("Response", "")
    resp_base = response.replace("Request", "").replace("Response", "")

    try:
        req_base, _, _, _ = parse_version(req_base)
        resp_base, _, _, _ = parse_version(resp_base)
    except ValueError:
        pass

    req_parts = word_re.findall(req_base)
    resp_parts = word_re.findall(resp_base)

    if not req_parts:
        return None

    merged_parts: list[str] = []
    j = 0

    for i, rp in enumerate(req_parts):
        if j < len(resp_parts) and similar(rp, resp_parts[j]):
            # prefer the request part when they differ (fix singular/plural or minor variants)
            merged_parts.append(rp)
            j += 1
        else:
            # check if this request part matches any upcoming response part
            # if so, we're missing parts from the request before this point
            found_ahead = False
            for k in range(j + 1, len(resp_parts)):
                if similar(rp, resp_parts[k]):
                    # The request part matches later in response
                    # This means current request part was missing from response
                    # Insert it and continue from the matched position
                    merged_parts.append(rp)
                    j = k + 1
                    found_ahead = True
                    break

            if not found_ahead:
                # response is missing this request part -> insert it
                merged_parts.append(rp)

    if not merged_parts:
        return None

    reconstruct = "".join(merged_parts) + "Response"
    return reconstruct


def highest_version_for(command: str, defined_names: set[str]) -> str | None:
    """
    Finds the highest version of a class name based on its base name.

    This function identifies the class in `names` that starts with `base` and has the highest
    version number. If an exact match exists, it is returned. Otherwise, the highest version
    is determined based on the naming convention.

    Args:
        command (str): The name of the command class (e.g., "UserGetRequest22V2").
        defined_names (set[str]: A set of class names to search.

    Returns:
        str: The highest version of the class name, or None if no versioned variant is found.
    """

    base_command, _, _, _ = parse_version(command)

    matching = []
    for name in defined_names:
        try:
            base, major, sp, v = parse_version(name)
            if base_command == base:
                matching.append((name, major, sp, v))
        except ValueError:
            continue

    if not matching:
        return None

    matching.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)

    return matching[0][0]


def parse_version(command: str) -> tuple[str, int, int, int]:
    """
    Parse a versioned command/class name into its components.

    The expected form is:
      <base><major>[sp<service_patch>][V<subsequent_patch>]
    where:
      - <base> is any prefix - UserGetRequest | SystemSoftwareVersionGetRequest
      - <major> is an optional integer - 18 in UserDeleteRequest18
      - sp<service_patch> is an optional service patch integer (e.g. "sp3")
      - V<subsequent_patch> (or v) is an optional subsequent patch integer (e.g. "V2")

    Args:
        command (str): The versioned name to parse (e.g. "UserGetRequest22", "Foo12sp3V2").

    Returns:
        tuple[str, int, int, int]: (base_name, major, service_patch, subsequent_patch)
            service_patch and subsequent_patch default to 0 when absent.

    Raises:
        ValueError: If `command` does not match the expected pattern.
    """
    pattern = r"^([A-Za-z]+)(?:(\d+)(?:sp(\d+))?(?:V(\d+))?)?$"

    match = re.match(pattern, command)
    if not match:
        raise ValueError(f"Invalid command format: {command}")

    base_name = match.group(1)
    major = int(match.group(2)) if match.group(2) else 0
    service_patch: int = int(match.group(3)) if match.group(3) else 0
    subsequent_patch: int = int(match.group(4)) if match.group(4) else 0

    return (base_name, major, service_patch, subsequent_patch)


def correct_typo(
    request: Optional[str], response: str, defined_names: set[str]
) -> str | None:
    """
    Normalize and correct a CamelCase response name using a curated vocabulary.

    The function splits the provided CamelCase-like identifier into word fragments,
    generates multiple correction candidates for each fragment, then tries all
    combinations to find a match in defined_names.

    Correction strategy:
      - Split the identifier into fragments using a regex that handles acronyms,
        numbers, and usual CamelCase boundaries.
      - For each fragment, generate up to 5 correction candidates using difflib
      - Try all combinations of corrected fragments to find a match
      - If exact match found in defined_names, return it
      - Otherwise try to find highest-versioned variant

    Args:
        response (str): The CamelCase-style response name to normalize (e.g. "UserGetReq22V2").
        defined_names (set[str]): A set of valid response/class names to validate against.

    Returns:
        str | None: The corrected name present in defined_names, or None if no
        suitable correction exists.
    """
    if request:
        reconstructed: str | None = reconstruct_missing_parts(request, response)

        if reconstructed:
            response = reconstructed

    word_re = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+[0-9]*|[0-9]+")
    parts = word_re.findall(response)

    candidates_per_part = []
    for part in parts:
        candidates = []

        candidates.append(part)

        if part in CORRECT_WORDS:
            candidates_per_part.append([part])
            continue

        matches = get_close_matches(part, CORRECT_WORDS, n=5, cutoff=0.6)
        for match in matches:
            if match not in candidates:
                candidates.append(match)

        candidates_per_part.append(candidates)

    for combination in product(*candidates_per_part):
        corrected_response = "".join(combination)

        if corrected_response in defined_names:
            return corrected_response

        candidate = highest_version_for(corrected_response, defined_names)
        if candidate and candidate in defined_names:
            return candidate

    return None

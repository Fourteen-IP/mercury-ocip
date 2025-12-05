
[chronicl](https://github.com/minimal-mind/chronicl)

## CODEBASE OVERVIEW
- Mercury is a Python library for interacting with BroadWorks servers.
- It is designed to be a simple and easy to use library for interacting with BroadWorks servers.
- It introduces command classes for each BroadWorks command, and a client class for interacting with the server.
- It has a command dispatch table for each client, and a requester class for sending requests to the server.
- It allows users to decide whether to use synchronous or asynchronous clients.
- It allows users to decide whether to use TCP or SOAP connections.

## TECH STACK
- Entirely Python 3.12+
- Uses attrs for object instantiation and validation
- Uses httpx for HTTP requests
- Uses logging for logging
- Uses pytest for testing
- Has an sycn and asycn version
- Uses pydantic for modeling data

## CONTRIBUTORS
- @Jordan-Prescott
- @KiPageFault
- @malkin0xb8

## DESIGN DECISIONS
- Command classes are used to represent BroadWorks commands.
- Client classes are used to represent connections to BroadWorks servers.
- Requester classes are used to send requests to BroadWorks servers.
- The dispatch table is used to map command names to command classes.
- In the command classes we will maintain latest version of command but allow the user to specify the version of the command they want to use.
- Definition of a feature that will be added to agent must meet the following criteria:
    - Needs to take more than ten mins 
	- A task that can be done in bulk 
	- Needs at least 3 steps to complete 
	- Needs at least 5 people to request it
	- Frequency is at least 4 times a month 
- Response classes will have to_dict, to_csv, etc to allow the user to export the data in a variety of formats.
- Agent scripts will be classes and those that are purely informational will have to_file() to allow the user to export the data in a variety of formats.

## RISKS
- The OCI Schemas from Cisco has been parsed into command classe. The need to green light this from Cisco legally is effecting solution in numerous ways.

## OPEN ENDED

## NEXT STEPS
- Deploy to open source with Mercury CLI included

## NOTES
- Biggest blocker is Cisco copyright stopping open source


## JOURNAL

@malkin0xb8 03.12.25
- Updated commands.py to allow for optional AS/XS parameters, alongside fixing all the typos in the command docstrings.

@malkin0xb8 28.11.25
File Reader encoding was set so that the BOM header: "U+FEFF" is still read, which meant that any bulk command trying to read from the parsed dictionary would fail when trying to read row["operation"] because the actual string was "\ufeffoperation". Changed the encoding to "utf-8-sig" which removes the BOM header when reading the file.

@Jordan-Prescott 25.11.25
- SharedOperations hosts many useful and common requests needed when building auatomtion features
- Automation workflow gives the end automation two methods from baseautomation they are _run and _wrap. Run is the entry and Wrap is the exit to mold the response to defined automation reponse in BA.
- Within Group Audit I have added type safety to the responses which we should be doing as standard moving forward. This has been a mixture of responses from commands.py and custom where I have modified data on response. 

@malkin0xb8 11.11.25
- Refactored BasePlugin and PluginCommand to have a cleaner standard, its easier to write new plugins, and expose them to the CLI.

@Jordan-Prescott 10.11.25
- Refined the data processing pipeline on bulk_ops, this is more dynamic and inline with the rules laid out in the developer docs
- Added ruleset for CSV upload sheets in dev docs to stay consistant throughout the project. This should also allow others to build their own/ modify existing 

@malkin0xb8 06.11.25
- Huge refactor of the Docs generations, and new helpers functions to apply some heuristics to fix all the typos in the schema docs.
- Decided to move away from trial and error and use each unique word in the commands to have a source of truth to compare against.
- Pattern Matching implemented to find missing or misplaced words in the command names. E.g "ServiceInstanceGetProfileCallCenter" vs "ServiceInstanceProfileGetCallCenterList"
- Docs generations is more reliable, showing correct response types.
- Moved the helper functions into the core module so they can be used in other places if needed. This is in utils/docs/correct_typo.py, and contains the correct_typo function, higher_version_for, which can be used to find the higher version of a command, and find_missing_parts which can be used to find missing parts in a command.

Overall, this should make the docs generation more reliable and easier to maintain - we can use this for future schema releases as well due to the dynamic nature of the typo correction.

@Jordan-Prescott 03.11.25
- Adjusted CC for bulk operations this now relies on the pipeline in base_operations

@Jordan-Prescott 28.10.25
- Some small modifications to user.create to remove department and contact from trunk addressing these are hardly used however we can add in if needed
- In _process_row we have multiple functions handling specific edge cases however theyre all to do with handling the tree and nested things within that tree. Future best solution is to refactor this and have something dynamic for all edge cases. 
- Note that user.create can both assign a pre existing device to a user or build a new one and assign

@KiPageFault 24.10.25
- Simplified Agent Plugin Loading | Utilises New Plugin Class System To Gather Members

@malkin0xb8 22.10.25
- Added BasePlugin and Plugin loading system to allow for easy extension of the library.
- Not finished but due to dependency issues using the library, I am pushing the changes now.

@Jordan-Prescott 21.10.25
- Bulk devices added however hitting issue in commands.py with the AS feilds still getting into the class representation
- I did think about refining the bulk_operations file however this is a gateway object just for UX so lets keep it in and let it grow
- Conversation with @malkin0xb8 about session_id, this is in client.py under authentication becuase if the user decides to repurpose client by logging out this will set session id to "" so we can catch this and generate a new one when logging back in.

@malkin0xb8 21.10.25
- Updated types in Client to reflect the actual response from OCI, it would return OCICommand Type, which is not accurate and would cause issues when trying to check for specific response types.
- Updated AsyncClient similarly to Client to reflect accurate response types.
- Fixed type issue in base_command.py where Parser and AsyncParser were being imported from types.py causing circular import issues. Moved XMLDictResult to basic_types.py to resolve this.
- Fixed base_command get_field_aliases to account for the fact not all classes inheriting OICType are dataclasses.

@KiPageFault 15.10.25
- Removed Constructor From UserGetListInGroupRequest as it was accidentally merged from a previous build causing singular command fault
- Normalised Table Construction For OCITable Types To Reflect snake_case Standard
- Spotted a critical error in parser due to failed request: ServiceProviderServicePackGetListRequest. 
I noticed that returns from the request do not fit convential OCITable structure leading to the parser treating items as singletons instead of list components. Typically parser would serialise these values into dictionaries and merge them, however due to the nature of the command it lead to them being seperated. To fix this, I embedded a clause in parser which identifies singleton strings within a multi-item result into an embeds thems into a list.


@KiPageFault 09.10.25
- Refactored Bulk Call Center Operation Mapping To Nullify Premium Only Default Parameters
- Implemented Secure Token Generation Algorithm In Defines To Reflect Default Password Generation

@KiPageFault 08.10.25
- Reworked Bulk Operation Call Center Create Script To Utilise ServiceInstanceAddProfileCallCenter instead of the generic ServiceInstanceAddProfile
- This was implemented to fix XML Invalidation Errors From The OCI And To Adhere To Broadworks Specification

@Jordan-Prescott 29.09.25
- Decided to strip the opertations removing nested commands. The user will need to run root commands and if they want to extend that they will need to run the subcommand in its own file. 
- This will apply to all operations
- For Call Center this means when creating a call center the agents are not in there instead they are in their own modify agent list sheet which will need to be ran after the initial build.
- Added AA upload functionality, this is limited in terms that it doesnt offer the key config. The reason for this is its too many levels down to achieve this. Current thinking is that we offer another upload sheet to tackle the keys.

@Jordan-Prescott 12.09.25
- In client.receive_response added a if statement to check command instance if not a dict we assume a SuccessResponse
- Refined data processes pipeline with _handle methods that take care of nested objects -> These have been added to base_operation.py so that all that inheret from here will have it.

@Jordan-Prescott 03.09.25
- Flow form CSV -> Command -> execute now defined in example of Call Pickup Group Bulk
- Using CPUG as example
- Each BWKS entity has a bulk ops class where all operations are defined on there
- The parsing and execution of above ^^ is dynamic paired with operation in the csv and in field against class to match the command needed. - This is not yet fully flushed out to handle multiple
- The functions needed are also enforced from abstract methods on base_operations.py 

@Jordan-Prescott 29.08.25
- Upload sheets for core BWKS entities has been defined these are v1
- Fields needed in command are marked as optional in sheet to allow the user to remove what they dont need.
- A model with defaaults will be applied if the user decides to pass us an upload without a mandatory field for the command. 
- The above approach makes the upload sheets more dynamic however there are some fields absolulely necessery and if not passed by the user an error will be thrown
- Auto Attendant upload sheet only shows one key this is by design and puts adding what keys to update on the user meaning they will need to add in the remaining keys 

@Jordan-Prescott 20.08.25
- Currently running with Bulk Operations and Automations ONLY being used for sync version. Reasoning: Speed doesnt matter too much in these operations as long as its still seconds. Asycn is more really heavy/ backend ops. Additonally, we had issues making a sync and asycn version at once, splitting these for ease -> will result in some refactoring.

@malkin0xb8 19.08.25
- Removed select from requester, it was causing an issue where delay between packets would cause the connection to drop, which meant that data was only being half recieved. It will now catch drops and exceptions and continue.
- Added a Github Action to ensure the Chronicl file is updated, its important to update this as a team as design decisions are being made and being forgotten later down the line. 


@malkin0xb8 29.07.25
- Login issue was resolved as poor documentation from Cisco's end, in the new release LoginRequest22V5 does not require a signed password as it relies on the encrypted socket for TCP or TLS/SSL for HTTPS SOAP.
- We now let the user choose, and if it they want a raw unencrypted connection, we sign the password and revert to LoginRequest14sp4 to login.

@Jordan-Prescott 28.07.25
- Issue is definatley with the signedPassword however currently no idea what causes this
- Signing in with just the login request works fine 
- Hashing is the same in both Nigels and ours tested and there is no issue there 
- Issue found when we authenticate is there is a logout request sent from the ADP but Nigels does not 

@malkin0xb8 25.07.2025
- Discovered that the password signing is incorrect, after testing with raw password the login succeeded.
- Online suggestions say that since the socket and connection is SSL encrypted the OCI backend expects a different charset or format for the signed password.

@KiPageFault 22.07.2025
- Added Parser class designed for Type/Request/Response type translation between class objects, xml, and dictionaries.
- Added OCI base classes to encapsulate Type/Request/Response objects and provide parser utility.
- Finalised Client _receive_response in accordance with Requester object. It is designed to take a raw string on a successful response or \
  a tuple object containing an exception object and message.
- All above implementations require documentaiton.

@Jordan-Prescott 22.07.2025
- Added absolute import statements as this is a python package its best practuice 
- Imports should follow order: standard packages, internal packages, external packages at the bottom

@Jordan-Prescott 15.07.2025
- Added tests for the client class found in tests/client_tests.py
- Adjusted the _receive_response in client which will use the response object from requester to capture class to return

@Jordan-Prescott 14.07.2025
- Client class now first draft with most of the functionality in place, yet some things still need flushing out.
- Both client and AsycClient done
- Added exceptions for the library in exceptions.py
- Decided to add _receive_response to the client class to handle the response from the server. How this is done needs flushing out.
- Still need to add tests to the library which will start with the client class. 
- Still need to add documentation to the library.

@KiPageFault
- Modified Parser To Accomate OCITable Structure
- Implemented OCITable base class to base_command.py To Handle Listed Return Types
- Modified commands.py to include base OCITable

@KiPageFault
- Modified Parser To Resolve Nested OCIType Objects within a command class
- Updated Command Generation Structure To Reflect True Optional Parameters

@KiPageFault
- Modified Parser To Fix Nested Conversions When Multiple OCIType Objects Were Translated
- Modified OCITable To Construct Table Entries On Initialisation 
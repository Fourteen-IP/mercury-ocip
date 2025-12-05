from typing import Union, Dict, List
from mercury_ocip.exceptions import MError

# Used for when requester returns a successful/unsuccessful result
type RequestResult = Union[str, MError]

# Used for when requester connects to the server
type ConnectResult = Union[None, MError]

# Used for when requester disconnects from the server
type DisconnectResult = None

# Used In Parser For XMLToDict / ClassToDict Conversions
type XMLDictResult = Union[
    Dict[str, Union[str, "XMLDictResult", List["XMLDictResult"]]], str
]
"""
Model Context Protocol (MCP) implementation.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class MCPMessageType(Enum):
    """MCP message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    """MCP method names."""
    INITIALIZE = "initialize"
    PING = "ping"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    COMPLETE = "completion/complete"
    SET_LEVEL = "logging/setLevel"
    SUBSCRIBE = "resources/subscribe"
    UNSUBSCRIBE = "resources/unsubscribe"


@dataclass
class MCPMessage:
    """Base MCP message."""
    jsonrpc: str = "2.0"
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class MCPResource:
    """MCP resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class MCPPrompt:
    """MCP prompt definition."""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


@dataclass
class MCPServerCapabilities:
    """MCP server capabilities."""
    experimental: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None


@dataclass
class MCPClientCapabilities:
    """MCP client capabilities."""
    experimental: Optional[Dict[str, Any]] = None
    sampling: Optional[Dict[str, Any]] = None


@dataclass
class MCPInitializeParams:
    """MCP initialize request parameters."""
    protocolVersion: str
    capabilities: MCPClientCapabilities
    clientInfo: Dict[str, str]


@dataclass
class MCPInitializeResult:
    """MCP initialize response result."""
    protocolVersion: str
    capabilities: MCPServerCapabilities
    serverInfo: Dict[str, str]


class MCPProtocol:
    """Base MCP protocol handler."""
    
    def __init__(self):
        self.initialized = False
        self.capabilities = MCPServerCapabilities()
        
    def create_message(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        id: Optional[Union[str, int]] = None,
        result: Optional[Any] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> MCPMessage:
        """Create an MCP message."""
        return MCPMessage(
            method=method,
            params=params,
            id=id,
            result=result,
            error=error
        )
    
    def serialize_message(self, message: MCPMessage) -> str:
        """Serialize MCP message to JSON."""
        data = {
            "jsonrpc": message.jsonrpc,
        }
        
        if message.method:
            data["method"] = message.method
        if message.params:
            data["params"] = message.params
        if message.id is not None:
            data["id"] = message.id
        if message.result is not None:
            data["result"] = message.result
        if message.error:
            data["error"] = message.error
            
        return json.dumps(data)
    
    def parse_message(self, data: str) -> MCPMessage:
        """Parse JSON string to MCP message."""
        parsed = json.loads(data)
        return MCPMessage(
            jsonrpc=parsed.get("jsonrpc", "2.0"),
            method=parsed.get("method"),
            params=parsed.get("params"),
            id=parsed.get("id"),
            result=parsed.get("result"),
            error=parsed.get("error")
        )
    
    def create_error_response(
        self,
        id: Union[str, int],
        code: int,
        message: str,
        data: Optional[Any] = None
    ) -> MCPMessage:
        """Create an error response."""
        error = {
            "code": code,
            "message": message
        }
        if data:
            error["data"] = data
            
        return MCPMessage(id=id, error=error)


class MCPErrorCode:
    """Standard MCP error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000
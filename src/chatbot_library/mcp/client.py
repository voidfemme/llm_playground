"""
MCP Client implementation for connecting to other MCP servers.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import asdict

from .protocol import (
    MCPProtocol,
    MCPMessage,
    MCPClientCapabilities,
    MCPInitializeParams,
    MCPErrorCode,
    MCPMethod,
)


class MCPClient(MCPProtocol):
    """MCP Client for connecting to external MCP servers."""
    
    def __init__(self, name: str = "chatbot-library-client", version: str = "1.0.0"):
        super().__init__()
        self.name = name
        self.version = version
        self.logger = logging.getLogger(__name__)
        self.request_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        
        # Client capabilities
        self.client_capabilities = MCPClientCapabilities(
            experimental={},
            sampling={}
        )
    
    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with MCP server."""
        params = MCPInitializeParams(
            protocolVersion="2024-11-05",
            capabilities=self.client_capabilities,
            clientInfo={
                "name": self.name,
                "version": self.version
            }
        )
        
        response = await self._send_request(MCPMethod.INITIALIZE.value, asdict(params))
        self.initialized = True
        return response
    
    async def ping(self) -> Dict[str, Any]:
        """Send ping to server."""
        return await self._send_request(MCPMethod.PING.value)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from server."""
        response = await self._send_request(MCPMethod.LIST_TOOLS.value)
        return response.get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        params = {
            "name": name,
            "arguments": arguments
        }
        return await self._send_request(MCPMethod.CALL_TOOL.value, params)
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from server."""
        response = await self._send_request(MCPMethod.LIST_RESOURCES.value)
        return response.get("resources", [])
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server."""
        params = {"uri": uri}
        return await self._send_request(MCPMethod.READ_RESOURCE.value, params)
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts from server."""
        response = await self._send_request(MCPMethod.LIST_PROMPTS.value)
        return response.get("prompts", [])
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a prompt from the server."""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        return await self._send_request(MCPMethod.GET_PROMPT.value, params)
    
    async def _send_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a request and wait for response."""
        request_id = self._next_request_id()
        message = self.create_message(method=method, params=params, id=request_id)
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send message (this would need to be implemented by subclass)
            await self._send_message(message)
            
            # Wait for response
            response = await future
            return response
            
        finally:
            # Clean up
            self.pending_requests.pop(request_id, None)
    
    async def _send_message(self, message: MCPMessage):
        """Send message to server. Must be implemented by subclass."""
        raise NotImplementedError("Subclass must implement _send_message")
    
    async def handle_response(self, message_data: str):
        """Handle response from server."""
        try:
            message = self.parse_message(message_data)
            
            if message.id is not None:
                future = self.pending_requests.get(message.id)
                if future and not future.done():
                    if message.error:
                        future.set_exception(
                            MCPError(
                                message.error.get("code", MCPErrorCode.INTERNAL_ERROR),
                                message.error.get("message", "Unknown error"),
                                message.error.get("data")
                            )
                        )
                    else:
                        future.set_result(message.result or {})
                        
        except Exception as e:
            self.logger.error(f"Error handling response: {e}")


class MCPError(Exception):
    """MCP-specific error."""
    
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


class StdioMCPClient(MCPClient):
    """MCP Client that communicates over stdio."""
    
    def __init__(self, command: List[str], **kwargs):
        super().__init__(**kwargs)
        self.command = command
        self.process: Optional[asyncio.subprocess.Process] = None
        self.reader_task: Optional[asyncio.Task] = None
    
    async def connect(self):
        """Connect to MCP server via stdio."""
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Start reader task
        self.reader_task = asyncio.create_task(self._read_messages())
        
        # Initialize connection
        await self.initialize()
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
        
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    async def _send_message(self, message: MCPMessage):
        """Send message via stdin."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Not connected to server")
        
        message_str = self.serialize_message(message)
        self.process.stdin.write(f"{message_str}\n".encode())
        await self.process.stdin.drain()
    
    async def _read_messages(self):
        """Read messages from stdout."""
        if not self.process or not self.process.stdout:
            return
        
        try:
            async for line in self.process.stdout:
                try:
                    line_str = line.decode().strip()
                    if line_str:
                        await self.handle_response(line_str)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error reading messages: {e}")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
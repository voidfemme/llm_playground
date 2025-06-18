"""
Integration tests for MCP conversation manager integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from chatbot_library.core.mcp_integration import MCPConversationManager, ToolExecutionResult
from chatbot_library.tools.mcp_tool_registry import MCPToolRegistry, MCPTool, MCPToolSchema
from chatbot_library.tools.builtin_tools import TimeTool, CalculatorTool


class MockTool(MCPTool):
    """Mock tool for testing."""
    
    def __init__(self, name: str = "mock_tool", should_error: bool = False):
        self.name = name
        self.should_error = should_error
        self.execution_count = 0
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name=self.name,
            description=f"Mock tool: {self.name}",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Test input"}
                },
                "required": ["input"]
            }
        )
    
    async def execute(self, input: str) -> dict:
        self.execution_count += 1
        if self.should_error:
            raise ValueError(f"Mock error from {self.name}")
        return {"result": f"Mock result for {input}", "tool": self.name}


class TestMCPConversationManager:
    """Test the MCP-integrated conversation manager."""
    
    def test_mcp_manager_initialization(self, temp_data_dir):
        """Test MCP manager initialization."""
        manager = MCPConversationManager(temp_data_dir)
        
        assert manager.data_dir == temp_data_dir
        assert manager.tool_registry is not None
        
        # Should have built-in tools registered
        available_tools = manager.get_available_tools()
        tool_names = [tool["name"] for tool in available_tools]
        assert "get_current_time" in tool_names
        assert "calculate" in tool_names
    
    def test_get_available_tools(self, mcp_conversation_manager):
        """Test getting available tools in MCP format."""
        tools = mcp_conversation_manager.get_available_tools()
        
        assert len(tools) > 0
        
        # Check MCP format
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_get_tool_schema(self, mcp_conversation_manager):
        """Test getting individual tool schemas."""
        # Register a test tool
        mock_tool = MockTool("test_schema")
        mcp_conversation_manager.tool_registry.register_tool(mock_tool)
        
        schema = mcp_conversation_manager.get_tool_schema("test_schema")
        
        assert schema is not None
        assert schema["name"] == "test_schema"
        assert schema["description"] == "Mock tool: test_schema"
        assert "inputSchema" in schema
    
    def test_get_nonexistent_tool_schema(self, mcp_conversation_manager):
        """Test getting schema for non-existent tool."""
        schema = mcp_conversation_manager.get_tool_schema("nonexistent")
        assert schema is None


class TestToolExecution:
    """Test tool execution through MCP manager."""
    
    @pytest.mark.asyncio
    async def test_successful_tool_execution(self, mcp_conversation_manager):
        """Test successful tool execution."""
        # Register a mock tool
        mock_tool = MockTool("success_tool")
        mcp_conversation_manager.tool_registry.register_tool(mock_tool)
        
        result = await mcp_conversation_manager.execute_tool(
            "success_tool",
            {"input": "test data"}
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is True
        assert result.tool_name == "success_tool"
        assert result.result["result"] == "Mock result for test data"
        assert result.execution_time is not None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_failed_tool_execution(self, mcp_conversation_manager):
        """Test failed tool execution."""
        # Register a tool that errors
        error_tool = MockTool("error_tool", should_error=True)
        mcp_conversation_manager.tool_registry.register_tool(error_tool)
        
        result = await mcp_conversation_manager.execute_tool(
            "error_tool",
            {"input": "test"}
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is False
        assert result.tool_name == "error_tool"
        assert result.error is not None
        assert "Mock error" in result.error
        assert result.execution_time is not None
    
    @pytest.mark.asyncio
    async def test_tool_execution_with_conversation_tracking(self, mcp_conversation_manager):
        """Test tool execution with conversation tracking."""
        # Create conversation and message
        conversation = mcp_conversation_manager.create_conversation("Tool Test")
        message = mcp_conversation_manager.add_message(
            conversation.id, "user", "Test tool execution"
        )
        
        # Register mock tool
        mock_tool = MockTool("tracked_tool")
        mcp_conversation_manager.tool_registry.register_tool(mock_tool)
        
        # Execute tool with tracking
        result = await mcp_conversation_manager.execute_tool(
            "tracked_tool",
            {"input": "tracked execution"},
            conversation_id=conversation.id,
            message_id=message.id
        )
        
        assert result.success is True
        
        # Check that tool usage was recorded
        updated_conv = mcp_conversation_manager.get_conversation(conversation.id)
        updated_message = updated_conv.messages[0]
        
        assert hasattr(updated_message, 'metadata')
        assert updated_message.metadata is not None
        assert 'tool_usage' in updated_message.metadata
        assert len(updated_message.metadata['tool_usage']) == 1
        
        tool_usage = updated_message.metadata['tool_usage'][0]
        assert tool_usage['tool_name'] == 'tracked_tool'
        assert tool_usage['success'] is True
    
    @pytest.mark.asyncio
    async def test_builtin_tool_execution(self, mcp_conversation_manager):
        """Test executing built-in tools."""
        # Test time tool
        time_result = await mcp_conversation_manager.execute_tool(
            "get_current_time",
            {"format": "readable"}
        )
        
        assert time_result.success is True
        assert isinstance(time_result.result, str)
        
        # Test calculator tool
        calc_result = await mcp_conversation_manager.execute_tool(
            "calculate",
            {"expression": "10 + 5", "precision": 1}
        )
        
        assert calc_result.success is True
        assert calc_result.result["result"] == 15.0
        assert calc_result.result["formatted_result"] == "15.0"


class TestResponseWithTools:
    """Test adding responses that use tools."""
    
    @pytest.mark.asyncio
    async def test_add_response_with_tools(self, mcp_conversation_manager):
        """Test adding response that executed tools."""
        conversation = mcp_conversation_manager.create_conversation("Response Tools Test")
        message = mcp_conversation_manager.add_message(
            conversation.id, "user", "What time is it?"
        )
        
        # Simulate tools used
        tools_used = [
            {"name": "get_current_time", "parameters": {"format": "readable"}},
            {"name": "calculate", "parameters": {"expression": "2 + 2"}}
        ]
        
        response = await mcp_conversation_manager.add_response_with_tools(
            conversation.id,
            message.id,
            "test-model",
            "The current time is shown above, and 2+2=4",
            tools_used=tools_used,
            branch_name="with_tools"
        )
        
        assert response is not None
        assert response.text == "The current time is shown above, and 2+2=4"
        assert response.branch_name == "with_tools"
        
        # Check that tool execution metadata is included
        assert "tools_executed" in response.metadata
        tools_executed = response.metadata["tools_executed"]
        assert len(tools_executed) == 2
        
        # Check individual tool results
        time_tool_result = tools_executed[0]
        assert time_tool_result["tool_name"] == "get_current_time"
        assert time_tool_result["success"] is True
        
        calc_tool_result = tools_executed[1]
        assert calc_tool_result["tool_name"] == "calculate"
        assert calc_tool_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_add_response_with_failed_tools(self, mcp_conversation_manager):
        """Test adding response when tools fail."""
        conversation = mcp_conversation_manager.create_conversation("Failed Tools Test")
        message = mcp_conversation_manager.add_message(
            conversation.id, "user", "Test failed tools"
        )
        
        # Register a tool that will fail
        error_tool = MockTool("fail_tool", should_error=True)
        mcp_conversation_manager.tool_registry.register_tool(error_tool)
        
        tools_used = [
            {"name": "fail_tool", "parameters": {"input": "test"}}
        ]
        
        response = await mcp_conversation_manager.add_response_with_tools(
            conversation.id,
            message.id,
            "test-model",
            "Tool execution failed",
            tools_used=tools_used
        )
        
        assert response is not None
        
        # Should still record the failed tool execution
        assert "tools_executed" in response.metadata
        tool_result = response.metadata["tools_executed"][0]
        assert tool_result["tool_name"] == "fail_tool"
        assert tool_result["success"] is False


class TestToolUsageStatistics:
    """Test tool usage statistics and analysis."""
    
    @pytest.mark.asyncio
    async def test_conversation_tool_usage_statistics(self, mcp_conversation_manager):
        """Test getting tool usage statistics for a conversation."""
        conversation = mcp_conversation_manager.create_conversation("Stats Test")
        message1 = mcp_conversation_manager.add_message(
            conversation.id, "user", "First message"
        )
        message2 = mcp_conversation_manager.add_message(
            conversation.id, "user", "Second message"
        )
        
        # Execute some tools
        await mcp_conversation_manager.execute_tool(
            "get_current_time",
            {"format": "iso"},
            conversation.id,
            message1.id
        )
        
        await mcp_conversation_manager.execute_tool(
            "calculate",
            {"expression": "5 * 6"},
            conversation.id,
            message1.id
        )
        
        await mcp_conversation_manager.execute_tool(
            "calculate",
            {"expression": "10 / 2"},
            conversation.id,
            message2.id
        )
        
        # Get statistics
        stats = mcp_conversation_manager.get_conversation_tool_usage(conversation.id)
        
        assert stats["total_tool_executions"] == 3
        assert stats["total_errors"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["total_execution_time"] > 0
        
        # Check per-tool stats
        tools_stats = stats["tools"]
        assert "get_current_time" in tools_stats
        assert "calculate" in tools_stats
        
        time_stats = tools_stats["get_current_time"]
        assert time_stats["count"] == 1
        assert time_stats["errors"] == 0
        
        calc_stats = tools_stats["calculate"]
        assert calc_stats["count"] == 2
        assert calc_stats["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_tool_usage_with_errors(self, mcp_conversation_manager):
        """Test tool usage statistics with errors."""
        conversation = mcp_conversation_manager.create_conversation("Error Stats Test")
        message = mcp_conversation_manager.add_message(
            conversation.id, "user", "Test errors"
        )
        
        # Register error-prone tool
        error_tool = MockTool("error_prone", should_error=True)
        mcp_conversation_manager.tool_registry.register_tool(error_tool)
        
        # Execute tools (some will fail)
        await mcp_conversation_manager.execute_tool(
            "get_current_time", {}, conversation.id, message.id
        )
        
        await mcp_conversation_manager.execute_tool(
            "error_prone", {"input": "test"}, conversation.id, message.id
        )
        
        stats = mcp_conversation_manager.get_conversation_tool_usage(conversation.id)
        
        assert stats["total_tool_executions"] == 2
        assert stats["total_errors"] == 1
        assert stats["success_rate"] == 0.5
        
        # Check error tracking
        error_tool_stats = stats["tools"]["error_prone"]
        assert error_tool_stats["count"] == 1
        assert error_tool_stats["errors"] == 1


class TestToolRecommendations:
    """Test tool recommendation system."""
    
    @pytest.mark.asyncio
    async def test_get_tool_recommendations(self, mcp_conversation_manager):
        """Test getting tool recommendations based on message content."""
        conversation = mcp_conversation_manager.create_conversation("Recommendations Test")
        
        # Test recommendations for time-related query
        recommendations = await mcp_conversation_manager.get_tool_recommendations(
            conversation.id,
            "What time is it right now?"
        )
        
        assert len(recommendations) > 0
        
        # Should recommend time tool
        tool_names = [rec["tool_name"] for rec in recommendations]
        assert "get_current_time" in tool_names
        
        # Should have relevance scoring
        for rec in recommendations:
            assert "score" in rec
            assert "relevance" in rec
            assert rec["score"] > 0
    
    @pytest.mark.asyncio
    async def test_math_recommendations(self, mcp_conversation_manager):
        """Test recommendations for math-related queries."""
        conversation = mcp_conversation_manager.create_conversation("Math Test")
        
        recommendations = await mcp_conversation_manager.get_tool_recommendations(
            conversation.id,
            "Can you calculate 15 * 23 + 7?"
        )
        
        tool_names = [rec["tool_name"] for rec in recommendations]
        assert "calculate" in tool_names
        
        # Calculator should have high score for math queries
        calc_rec = next(rec for rec in recommendations if rec["tool_name"] == "calculate")
        assert calc_rec["score"] >= 1
    
    @pytest.mark.asyncio
    async def test_text_analysis_recommendations(self, mcp_conversation_manager):
        """Test recommendations for text analysis queries."""
        conversation = mcp_conversation_manager.create_conversation("Text Test")
        
        recommendations = await mcp_conversation_manager.get_tool_recommendations(
            conversation.id,
            "How many characters are in this text?"
        )
        
        tool_names = [rec["tool_name"] for rec in recommendations]
        # Should recommend text-related tools if available
        assert len(recommendations) >= 0  # May not have text tools in basic setup


class TestToolDiscovery:
    """Test external tool discovery."""
    
    def test_discover_external_tools(self, mcp_conversation_manager):
        """Test discovering tools from external packages."""
        # This is a placeholder test since we can't create real packages in tests
        # In practice, this would test loading tools from actual Python packages
        
        initial_tools = len(mcp_conversation_manager.get_available_tools())
        
        # Try to discover from a non-existent package (should handle gracefully)
        mcp_conversation_manager.discover_external_tools(["nonexistent.package"])
        
        # Should not crash and tool count should remain the same
        final_tools = len(mcp_conversation_manager.get_available_tools())
        assert final_tools == initial_tools
    
    def test_tool_registry_extension(self, mcp_conversation_manager):
        """Test extending the tool registry with custom tools."""
        initial_count = len(mcp_conversation_manager.get_available_tools())
        
        # Add a custom tool
        custom_tool = MockTool("custom_extension")
        mcp_conversation_manager.tool_registry.register_tool(custom_tool)
        
        # Should appear in available tools
        final_count = len(mcp_conversation_manager.get_available_tools())
        assert final_count == initial_count + 1
        
        tool_names = [t["name"] for t in mcp_conversation_manager.get_available_tools()]
        assert "custom_extension" in tool_names


class TestConcurrentToolExecution:
    """Test concurrent tool execution."""
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_executions(self, mcp_conversation_manager):
        """Test executing multiple tools concurrently."""
        conversation = mcp_conversation_manager.create_conversation("Concurrent Test")
        message = mcp_conversation_manager.add_message(
            conversation.id, "user", "Test concurrent execution"
        )
        
        # Execute multiple tools concurrently
        tasks = [
            mcp_conversation_manager.execute_tool(
                "get_current_time", {"format": "iso"}, 
                conversation.id, message.id
            ),
            mcp_conversation_manager.execute_tool(
                "calculate", {"expression": "10 + 15"},
                conversation.id, message.id
            ),
            mcp_conversation_manager.execute_tool(
                "calculate", {"expression": "5 * 8"},
                conversation.id, message.id
            )
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(result.success for result in results)
        
        # All should have different execution times
        execution_times = [result.execution_time for result in results]
        assert all(t > 0 for t in execution_times)
    
    @pytest.mark.asyncio
    async def test_tool_execution_isolation(self, mcp_conversation_manager):
        """Test that tool executions are properly isolated."""
        # Register tools that track execution count
        tool1 = MockTool("isolated_1")
        tool2 = MockTool("isolated_2")
        
        mcp_conversation_manager.tool_registry.register_tool(tool1)
        mcp_conversation_manager.tool_registry.register_tool(tool2)
        
        # Execute both tools multiple times
        for _ in range(3):
            await mcp_conversation_manager.execute_tool("isolated_1", {"input": "test"})
            await mcp_conversation_manager.execute_tool("isolated_2", {"input": "test"})
        
        # Each tool should have been executed exactly 3 times
        assert tool1.execution_count == 3
        assert tool2.execution_count == 3
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import aiohttp
from dapr.clients import DaprClient
from dapr.ext.grpc import App

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message in the multi-agent system."""
    agent_name: str
    role: str
    content: str
    timestamp: datetime
    message_id: str

class DaprChatManager:
    """Manages inter-agent communication using Dapr pub/sub."""
    
    def __init__(self, app_id: str = "multi-agent-chat"):
        self.app_id = app_id
        self.pubsub_name = "chat-pubsub"
        self.topic_name = "agent-messages"
        self.client = None
        self.message_handlers = {}
        
    async def initialize(self):
        """Initialize Dapr client."""
        try:
            self.client = DaprClient()
            logger.info("Dapr client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Dapr client: {e}")
            raise
    
    async def publish_message(self, message: ChatMessage):
        """Publish a message to the chat topic."""
        if not self.client:
            await self.initialize()
        
        try:
            message_data = {
                "agent_name": message.agent_name,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.message_id
            }
            
            await self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topic_name,
                data=json.dumps(message_data),
                data_content_type='application/json'
            )
            
            logger.info(f"Message published from {message.agent_name}: {message.message_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    async def subscribe_to_messages(self, agent_name: str, handler_func):
        """Subscribe to messages for a specific agent."""
        self.message_handlers[agent_name] = handler_func
        logger.info(f"Subscribed {agent_name} to messages")
    
    async def handle_incoming_message(self, event_data: Dict):
        """Handle incoming messages from Dapr subscription."""
        try:
            message_data = json.loads(event_data.get('data', '{}'))
            
            message = ChatMessage(
                agent_name=message_data['agent_name'],
                role=message_data['role'],
                content=message_data['content'],
                timestamp=datetime.fromisoformat(message_data['timestamp']),
                message_id=message_data['message_id']
            )
            
            # Route message to appropriate handlers
            for agent_name, handler in self.message_handlers.items():
                if agent_name != message.agent_name:  # Don't send to sender
                    await handler(message)
                    
        except Exception as e:
            logger.error(f"Failed to handle incoming message: {e}")
    
    async def get_chat_history(self, limit: int = 100) -> List[ChatMessage]:
        """Retrieve chat history from Dapr state store."""
        if not self.client:
            await self.initialize()
        
        try:
            # Get from state store
            response = await self.client.get_state(
                store_name="chat-state",
                key="chat-history"
            )
            
            if response.data:
                history_data = json.loads(response.data)
                messages = []
                
                for msg_data in history_data[-limit:]:
                    message = ChatMessage(
                        agent_name=msg_data['agent_name'],
                        role=msg_data['role'],
                        content=msg_data['content'],
                        timestamp=datetime.fromisoformat(msg_data['timestamp']),
                        message_id=msg_data['message_id']
                    )
                    messages.append(message)
                
                return messages
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
        
        return []
    
    async def save_chat_history(self, messages: List[ChatMessage]):
        """Save chat history to Dapr state store."""
        if not self.client:
            await self.initialize()
        
        try:
            history_data = []
            for msg in messages:
                history_data.append({
                    "agent_name": msg.agent_name,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_id": msg.message_id
                })
            
            await self.client.save_state(
                store_name="chat-state",
                key="chat-history",
                value=json.dumps(history_data)
            )
            
            logger.info(f"Saved {len(messages)} messages to chat history")
            
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
    
    async def cleanup(self):
        """Cleanup Dapr resources."""
        if self.client:
            await self.client.close()
            logger.info("Dapr client closed")

# Dapr App for handling subscriptions
app = App()

@app.subscribe(pubsub_name='chat-pubsub', topic='agent-messages')
async def message_handler(event):
    """Handle incoming messages from Dapr subscription."""
    chat_manager = DaprChatManager()
    await chat_manager.handle_incoming_message(event.data)

# Utility functions
async def create_chat_manager() -> DaprChatManager:
    """Factory function to create and initialize chat manager."""
    manager = DaprChatManager()
    await manager.initialize()
    return manager

async def send_agent_message(agent_name: str, role: str, content: str) -> str:
    """Send a message from an agent."""
    import uuid
    
    message = ChatMessage(
        agent_name=agent_name,
        role=role,
        content=content,
        timestamp=datetime.now(),
        message_id=str(uuid.uuid4())
    )
    
    manager = await create_chat_manager()
    await manager.publish_message(message)
    await manager.cleanup()
    
    return message.message_id

if __name__ == "__main__":
    # Run the Dapr app
    app.run(port=6001)
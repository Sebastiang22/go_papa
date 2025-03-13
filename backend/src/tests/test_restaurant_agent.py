import asyncio
import logging
from datetime import datetime
from inference.graphs.restaurant_graph import RestaurantChatAgent
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_restaurant_agent():
    try:
        # Initialize the agent
        agent = RestaurantChatAgent()
        logger.info("RestaurantChatAgent initialized successfully")

        # Test parameters
        test_input = "me llamo sebastian"
        conversation_id = "test_conversation_123"
        conversation_name = "Test Conversation"
        user_id = "test_user_123"
        restaurant_name = "papa"

        logger.info(f"Sending test message: {test_input}")
        
        # Invoke the agent
        new_state, message_id = await agent.invoke_flow(
            user_input=test_input,
            conversation_id=conversation_id,
            conversation_name=conversation_name,
            user_id=user_id,
            restaurant_name=restaurant_name
        )
        print(new_state['messages'][-1].content)
        # Log the response
        if new_state and "messages" in new_state and new_state["messages"]:
            logger.info(f"Response received - message_id: {message_id}")
            logger.info(f"Last message content: {new_state['messages'][-1].content}")

        else:
            logger.error("No messages found in the response state")
            logger.debug(f"Complete state: {new_state}")


    except Exception as e:
        logger.exception(f"Error during agent testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_restaurant_agent())
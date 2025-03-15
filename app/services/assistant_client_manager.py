import logging
from app.core.config import settings

from typing import Any, AsyncGenerator, Dict, List, Optional, Sequence, Union, Literal

from langgraph_sdk import get_client

# Set logger level based on DEBUG flag from configuration.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.ERROR)


class GraphManager:
    """
    A scalable manager class for interacting with LangGraph.

    This class provides methods for managing graph-level operations including assistants,
    threads, runs, crons, and persistent storage. Additionally, it encapsulates assistant-level
    interactions such as sending and streaming messages on a specific assistant.

    Attributes:
        client: The LangGraph asynchronous client.
        graph_id: The ID of the graph for which operations are performed.
        assistant_id: (Optional) The assistant ID used for messaging operations.
    """

    def __init__(
            self,
            deployment_url: str,
            graph_id: str,
            assistant_id: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Initialize the GraphManager.

        Args:
            deployment_url (str): The base URL of the LangGraph API.
            graph_id (str): The graph identifier.
            assistant_id (Optional[str]): An optional assistant identifier.
            api_key (Optional[str]): API key for authentication (if not provided, loaded from environment).
        """
        self.client = get_client(url=deployment_url, api_key=api_key)
        self.graph_id = graph_id
        self.assistant_id = assistant_id
        logger.info(f"GraphManager initialized for graph_id: {graph_id}")
        if self.assistant_id:
            logger.info(f"Default assistant_id set: {self.assistant_id}")

    # ===== Assistant Operations =====
    async def create_assistant(
            self,
            config: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            assistant_id: Optional[str] = None,
            name: Optional[str] = "Untitled Assistant",
            if_exists: Literal["raise", "do_nothing"] = "raise",
    ) -> Dict[str, Any]:
        """
        Create a new assistant for the current graph.

        Args:
            config (Optional[Dict[str, Any]]): Configuration options for the assistant.
            metadata (Optional[Dict[str, Any]]): Metadata to attach to the assistant.
            assistant_id (Optional[str]): Optional assistant ID (generated if not provided).
            name (Optional[str]): Name for the assistant.
            if_exists (Literal["raise", "do_nothing"]): Behavior if the assistant already exists.

        Returns:
            Dict[str, Any]: The created assistant object.
        """
        logger.info("Creating new assistant...")
        assistant = await self.client.assistants.create(
            graph_id=self.graph_id,
            config=config,
            metadata=metadata,
            assistant_id=assistant_id,
            if_exists=if_exists,
            name=name,
        )
        self.assistant_id = assistant.get("assistant_id")
        logger.debug(f"Assistant created: {assistant}")
        return assistant

    async def load_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Load and set the assistant for this manager.

        Args:
            assistant_id (str): The assistant ID to load.

        Returns:
            Dict[str, Any]: The assistant object.
        """
        logger.info(f"Loading assistant {assistant_id}...")
        assistant = await self.client.assistants.get(assistant_id)
        self.assistant_id = assistant.get("assistant_id")
        logger.debug(f"Assistant loaded: {assistant}")
        return assistant

    async def update_assistant(
            self,
            assistant_id: str,
            config: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            name: Optional[str] = None,
            graph_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing assistant.

        Args:
            assistant_id (str): The assistant ID to update.
            config (Optional[Dict[str, Any]]): New configuration.
            metadata (Optional[Dict[str, Any]]): Metadata to merge.
            name (Optional[str]): New name.
            graph_id (Optional[str]): Optionally update the graph ID.

        Returns:
            Dict[str, Any]: The updated assistant object.
        """
        logger.info(f"Updating assistant {assistant_id}...")
        updated = await self.client.assistants.update(
            assistant_id=assistant_id,
            graph_id=graph_id or self.graph_id,
            config=config,
            metadata=metadata,
            name=name,
        )
        logger.debug(f"Assistant updated: {updated}")
        return updated

    async def delete_assistant(self, assistant_id: str) -> None:
        """
        Delete an assistant by its ID.

        Args:
            assistant_id (str): The assistant ID to delete.
        """
        logger.info(f"Deleting assistant {assistant_id}...")
        await self.client.assistants.delete(assistant_id)
        logger.debug("Assistant deleted.")

    # ===== Thread Operations =====
    async def create_thread(
            self,
            metadata: Optional[Dict[str, Any]] = None,
            thread_id: Optional[str] = None,
            if_exists: Literal["raise", "do_nothing"] = "raise",
    ) -> Dict[str, Any]:
        """
        Create a new thread.

        Args:
            metadata (Optional[Dict[str, Any]]): Metadata for the thread.
            thread_id (Optional[str]): Optional thread identifier.
            if_exists (Literal["raise", "do_nothing"]): Behavior if the thread exists.

        Returns:
            Dict[str, Any]: The created thread object.
        """
        logger.info("Creating new thread...")
        thread = await self.client.threads.create(metadata=metadata, thread_id=thread_id, if_exists=if_exists)
        logger.debug(f"Thread created: {thread}")
        return thread

    async def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Retrieve a thread by ID.

        Args:
            thread_id (str): The thread identifier.

        Returns:
            Dict[str, Any]: The thread object.
        """
        logger.info(f"Fetching thread {thread_id}...")
        thread = await self.client.threads.get(thread_id)
        logger.debug(f"Thread retrieved: {thread}")
        return thread

    async def delete_thread(self, thread_id: str) -> None:
        """
        Delete a thread.

        Args:
            thread_id (str): The thread ID to delete.
        """
        logger.info(f"Deleting thread {thread_id}...")
        await self.client.threads.delete(thread_id)
        logger.debug("Thread deleted.")

    async def get_thread_state(
            self, thread_id: str, checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the current state of a thread.

        Args:
            thread_id (str): The thread identifier.
            checkpoint_id (Optional[str]): Optional checkpoint identifier.

        Returns:
            Dict[str, Any]: The thread state.
        """
        logger.info(f"Getting state for thread {thread_id}...")
        state = await self.client.threads.get_state(thread_id, checkpoint_id=checkpoint_id)
        logger.debug(f"Thread state: {state}")
        return state

    async def _get_or_create_thread(self, conversation_id: str, thread_id: Optional[str] = None) -> str:
        """
        Ensure a thread exists for a conversation.

        If a thread_id is provided, it is returned. Otherwise, a new thread is created
        with metadata including the conversation_id.

        Args:
            conversation_id (str): A conversation identifier.
            thread_id (Optional[str]): Existing thread ID.

        Returns:
            str: The thread ID.
        """
        if thread_id:
            logger.debug(f"Using existing thread_id: {thread_id}")
            return thread_id
        logger.info(f"Creating new thread for conversation {conversation_id}")
        thread = await self.create_thread(metadata={"conversation_id": conversation_id})
        new_thread_id = thread.get("thread_id")
        logger.info(f"New thread created with id: {new_thread_id}")
        return new_thread_id

    # ===== Run Operations (Assistant Interaction) =====
    async def send_message(
            self,
            message: str,
            conversation_id: str,
            max_tokens: int = 10000,
            response_model_kwargs: Optional[Dict[str, Any]] = None,
            thread_id: Optional[str] = None,
            assistant_id: Optional[str] = None,
            images: Optional[List[Any]] = None,
    ) -> Optional[str]:
        """
        Send a message to the assistant and return the final response.

        This method creates a run, waits for its completion, and extracts the last AI response.

        Args:
            message (str): The user's message.
            conversation_id (str): Identifier for the conversation.
            max_tokens (int): Maximum tokens for the assistant's response.
            response_model_kwargs (Optional[Dict[str, Any]]): Additional configuration for the run.
            thread_id (Optional[str]): An optional thread identifier.
            assistant_id (Optional[str]): Optional assistant ID to override the default.
            images (Optional[List[Any]]): Optional list of images to include with the message.

        Returns:
            Optional[str]: The assistant's response content, if available.
        """
        try:
            logger.info(f"Sending message: {message}")
            aid = assistant_id or self.assistant_id
            if not aid:
                raise ValueError("Assistant ID is not set. Please load or create an assistant first.")
            tid = await self._get_or_create_thread(conversation_id, thread_id)
            # Build input payload with optional images if provided
            if images:
                input_payload = {"messages": [{"role": "user", "content": message}], "images": images}
            else:
                input_payload = {"messages": [{"role": "user", "content": message}]}
            if response_model_kwargs is None:
                response_model_kwargs = {"max_tokens": max_tokens}
            run_config = {"configurable": {"response_model_kwargs": response_model_kwargs}}

            run = await self.client.runs.create(
                thread_id=tid,
                assistant_id=aid,
                input=input_payload,
                config=run_config,
            )
            logger.debug(f"Run created with run_id: {run.get('run_id')}")
            await self.client.runs.join(tid, run["run_id"])
            logger.debug("Run completed; fetching thread state...")
            state = await self.get_thread_state(tid)
            messages = state.get("values", {}).get("messages", [])
            ai_messages = [msg for msg in messages if msg.get("type") == "ai"]
            if ai_messages:
                response_content = ai_messages[-1].get("content")
                logger.info(f"Received response: {response_content}")
                return response_content
            logger.warning("No AI response found in thread state.")
            return None
        except Exception as exc:
            logger.exception("Exception occurred while sending message.")
            raise exc

    async def stream_message(
            self,
            message: str,
            conversation_id: str,
            max_tokens: int = 10000,
            response_model_kwargs: Optional[Dict[str, Any]] = None,
            thread_id: Optional[str] = None,
            assistant_id: Optional[str] = None,
            images: Optional[List[Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream the assistant's response as it is generated.

        Yields:
            str: Chunks of the assistant's response.
        """
        try:
            logger.info(f"Streaming message: {message}")
            aid = assistant_id or self.assistant_id
            if not aid:
                raise ValueError("Assistant ID is not set. Please load or create an assistant first.")
            tid = await self._get_or_create_thread(conversation_id, thread_id)
            if images:
                input_payload = {"messages": [{"role": "user", "content": message}], "images": images}
            else:
                input_payload = {"messages": [{"role": "user", "content": message}]}
            if response_model_kwargs is None:
                response_model_kwargs = {"max_tokens": max_tokens}
            run_config = {"configurable": {"response_model_kwargs": response_model_kwargs}}

            async for chunk in self.client.runs.stream(
                    thread_id=tid,
                    assistant_id=aid,
                    input=input_payload,
                    config=run_config,
                    stream_mode=["values", "debug"],
            ):
                if chunk.event == "values" and chunk.data:
                    msgs = chunk.data.get("messages", [])
                    for msg in reversed(msgs):
                        if msg.get("type") == "ai":
                            content = msg.get("content", "")
                            if content:
                                logger.debug(f"Streaming content chunk: {content}")
                                yield content
                            break
        except Exception as exc:
            logger.exception("Exception occurred while streaming message.")
            raise exc

    # ===== Cron Operations =====
    async def create_cron_for_thread(
            self,
            thread_id: str,
            schedule: str,
            input_data: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            config: Optional[Dict[str, Any]] = None,
            interrupt_before: Optional[List[str]] = None,
            interrupt_after: Optional[List[str]] = None,
            webhook: Optional[str] = None,
            multitask_strategy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a cron job for a specific thread.

        Args:
            thread_id (str): The thread identifier.
            schedule (str): The cron schedule (e.g., "0 9 * * *").
            input_data (Optional[Dict[str, Any]]): Input payload for the cron run.
            metadata (Optional[Dict[str, Any]]): Metadata for the cron run.
            config (Optional[Dict[str, Any]]): Configuration options.
            interrupt_before (Optional[List[str]]): Nodes to interrupt before execution.
            interrupt_after (Optional[List[str]]): Nodes to interrupt after execution.
            webhook (Optional[str]): Webhook URL for notifications.
            multitask_strategy (Optional[str]): Strategy for concurrent runs.

        Returns:
            Dict[str, Any]: The created cron job details.
        """
        logger.info("Creating cron job for thread...")
        cron = await self.client.crons.create_for_thread(
            thread_id=thread_id,
            assistant_id=self.graph_id,
            schedule=schedule,
            input=input_data,
            metadata=metadata,
            config=config,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
            webhook=webhook,
            multitask_strategy=multitask_strategy,
        )
        logger.debug(f"Cron job created: {cron}")
        return cron

    async def delete_cron(self, cron_id: str) -> None:
        """
        Delete a cron job.

        Args:
            cron_id (str): The cron job identifier.
        """
        logger.info(f"Deleting cron job {cron_id}...")
        await self.client.crons.delete(cron_id)
        logger.debug("Cron job deleted.")

    async def search_crons(
            self,
            assistant_id: Optional[str] = None,
            thread_id: Optional[str] = None,
            limit: int = 10,
            offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search for cron jobs.

        Args:
            assistant_id (Optional[str]): Filter by assistant ID.
            thread_id (Optional[str]): Filter by thread ID.
            limit (int): Maximum results.
            offset (int): Pagination offset.

        Returns:
            List[Dict[str, Any]]: A list of cron jobs.
        """
        logger.info("Searching for cron jobs...")
        crons = await self.client.crons.search(
            assistant_id=assistant_id, thread_id=thread_id, limit=limit, offset=offset
        )
        logger.debug(f"Cron jobs found: {crons}")
        return crons

    # ===== Store Operations =====
    async def put_item(
            self,
            namespace: Sequence[str],
            key: str,
            value: Dict[str, Any],
            index: Optional[Union[Literal[False], List[str]]] = None,
            ttl: Optional[int] = None,
    ) -> None:
        """
        Store or update an item in the shared key-value store.

        Args:
            namespace (Sequence[str]): The namespace path.
            key (str): Unique key for the item.
            value (Dict[str, Any]): The data to store.
            index (Optional[Union[Literal[False], List[str]]]): Optional indexing configuration.
            ttl (Optional[int]): Time-to-live in minutes.
        """
        logger.info(f"Putting item '{key}' in namespace {namespace}...")
        await self.client.store.put_item(namespace, key, value, index=index, ttl=ttl)
        logger.debug("Item stored/updated.")

    async def get_item(
            self, namespace: Sequence[str], key: str, refresh_ttl: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Retrieve an item from the shared store.

        Args:
            namespace (Sequence[str]): The namespace path.
            key (str): The item key.
            refresh_ttl (Optional[bool]): Whether to refresh the TTL.

        Returns:
            Dict[str, Any]: The retrieved item.
        """
        logger.info(f"Getting item '{key}' from namespace {namespace}...")
        item = await self.client.store.get_item(namespace, key, refresh_ttl=refresh_ttl)
        logger.debug(f"Item retrieved: {item}")
        return item

    async def delete_item(self, namespace: Sequence[str], key: str) -> None:
        """
        Delete an item from the shared store.

        Args:
            namespace (Sequence[str]): The namespace path.
            key (str): The item key.
        """
        logger.info(f"Deleting item '{key}' from namespace {namespace}...")
        await self.client.store.delete_item(namespace, key)
        logger.debug("Item deleted.")

    async def search_items(
            self,
            namespace_prefix: Sequence[str],
            filter: Optional[Dict[str, Any]] = None,
            limit: int = 10,
            offset: int = 0,
            query: Optional[str] = None,
            refresh_ttl: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Search for items within a namespace prefix.

        Args:
            namespace_prefix (Sequence[str]): The namespace prefix.
            filter (Optional[Dict[str, Any]]): Filter criteria.
            limit (int): Maximum number of items.
            offset (int): Pagination offset.
            query (Optional[str]): Natural language query.
            refresh_ttl (Optional[bool]): Whether to refresh TTL on items.

        Returns:
            Dict[str, Any]: The search result.
        """
        logger.info("Searching for items in store...")
        response = await self.client.store.search_items(
            namespace_prefix, filter=filter, limit=limit, offset=offset, query=query, refresh_ttl=refresh_ttl
        )
        logger.debug(f"Search response: {response}")
        return response

    async def list_namespaces(
            self,
            prefix: Optional[List[str]] = None,
            suffix: Optional[List[str]] = None,
            max_depth: Optional[int] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List namespaces with optional filtering.

        Args:
            prefix (Optional[List[str]]): Namespace prefix filter.
            suffix (Optional[List[str]]): Namespace suffix filter.
            max_depth (Optional[int]): Maximum depth of namespace hierarchy.
            limit (int): Maximum namespaces returned.
            offset (int): Pagination offset.

        Returns:
            Dict[str, Any]: The list of namespaces.
        """
        logger.info("Listing namespaces...")
        namespaces = await self.client.store.list_namespaces(
            prefix=prefix, suffix=suffix, max_depth=max_depth, limit=limit, offset=offset
        )
        logger.debug(f"Namespaces: {namespaces}")
        return namespaces

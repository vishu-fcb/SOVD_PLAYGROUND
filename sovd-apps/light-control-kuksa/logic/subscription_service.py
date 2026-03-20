"""
KUKSA subscription service for real-time light state updates.
"""

import asyncio
import logging
from typing import Callable, Any
from kuksa_client.grpc import Field, SubscribeEntry, View

from .kuksa_client import KuksaClientManager

logger = logging.getLogger(__name__)


class KuksaSubscriptionService:
    """Manages real-time subscriptions to KUKSA databroker signals."""

    def __init__(self, client_manager: KuksaClientManager):
        self.client_manager = client_manager
        self._subscription_task = None
        self._update_callbacks = []

    def add_update_callback(self, callback: Callable[[str, Any], None]):
        """Add a callback function to be called when updates are received."""
        self._update_callbacks.append(callback)

    async def subscribe_to_paths(self, vss_paths: list):
        """
        Subscribe to specified VSS paths for real-time updates.
        Enables bidirectional synchronization with KUKSA databroker.
        """
        try:
            async with self.client_manager.get_client() as client:
                entries = [
                    SubscribeEntry(path, View.FIELDS, (Field.VALUE, Field.ACTUATOR_TARGET))
                    for path in vss_paths
                ]

                async for updates in client.subscribe(entries=entries):
                    for update in updates:
                        # Extract the actual value from either current value or actuator target
                        new_value = None
                        if update.entry.actuator_target is not None:
                            new_value = update.entry.actuator_target.value
                        elif update.entry.value is not None:
                            new_value = (
                                update.entry.value.value
                                if hasattr(update.entry.value, 'value')
                                else update.entry.value
                            )

                        if new_value is not None:
                            # Notify all registered callbacks
                            for callback in self._update_callbacks:
                                try:
                                    callback(update.entry.path, new_value)
                                except Exception as e:
                                    logger.error(f"Error in subscription callback: {e}")

        except Exception as e:
            logger.error(f"Failed to subscribe to datapoints: {e}")
            # Wait before retrying
            await asyncio.sleep(5)

    def start_subscription(self, vss_paths: list):
        """Start the subscription as a background task."""
        if self._subscription_task is None or self._subscription_task.done():
            self._subscription_task = asyncio.create_task(self.subscribe_to_paths(vss_paths))
        return self._subscription_task

    def stop_subscription(self):
        """Stop the subscription background task."""
        if self._subscription_task and not self._subscription_task.done():
            self._subscription_task.cancel()

import logging
from typing import Dict, Any
from kuksa_client.grpc import Datapoint
from kuksa_client.grpc.aio import VSSClient

logger = logging.getLogger(__name__)


class KuksaClientManager:
    # Manages KUKSA databroker client
    def __init__(self, kuksa_ip: str, kuksa_port: int):
        self.kuksa_ip = kuksa_ip
        self.kuksa_port = kuksa_port

    def get_client(self):
        # Create VSSClient for KUKSA databroker communication
        return VSSClient(self.kuksa_ip, self.kuksa_port)

    async def check_connection(self) -> bool:
        # Verify connection to the KUKSA databroker
        try:
            async with self.get_client() as client:
                # Lightweight call to verify gRPC connectivity
                await client.get_server_info()
            return True
        except Exception as e:
            logger.warning(f"KUKSA connection failed: {e}")
            return False

    async def set_datapoint(self, vss_path: str, value: Any) -> bool:
        # Set a single datapoint value
        try:
            async with self.get_client() as client:
                await client.set_target_values({vss_path: Datapoint(value=value)})
            return True
        except Exception as e:
            logger.error(f"Failed to set {vss_path} to {value}: {e}")
            return False

    async def set_datapoints(self, datapoints: Dict[str, Any]) -> bool:
        # Set multiple datapoint values
        try:
            async with self.get_client() as client:
                formatted_datapoints = {
                    path: Datapoint(value=value)
                    for path, value in datapoints.items()
                }
                await client.set_target_values(formatted_datapoints)
            return True
        except Exception as e:
            logger.error(f"Failed to set datapoints: {e}")
            return False

    async def get_datapoint(self, vss_path: str) -> Any:
        # Get current value of a single datapoint
        try:
            async with self.get_client() as client:
                current_values = await client.get_current_values([vss_path])
                return current_values[vss_path].value
        except Exception as e:
            logger.error(f"Failed to get {vss_path}: {e}")
            return None

    async def get_datapoints(self, vss_paths: list) -> Dict[str, Any]:
        # Get current values of multiple datapoints
        try:
            async with self.get_client() as client:
                current_values = await client.get_current_values(vss_paths)
                return {path: current_values[path].value for path in vss_paths}
        except Exception as e:
            logger.error(f"Failed to get datapoints: {e}")
            return {}

from __future__ import annotations

from typing import Any

from tuya_iot import (
    TuyaOpenMQ,
    TuyaOpenAPI
)

from tuya_iot.openmq import (
    CONNECT_FAILED_NOT_AUTHORISED,
    mqtt,
)

from ...const import (
    LOGGER,
)

class XTIOTOpenMQ(TuyaOpenMQ):
    def __init__(self, api: TuyaOpenAPI) -> None:
        super().__init__(api)

    def _on_connect(self, mqttc: mqtt.Client, user_data: Any, flags, rc):
        if rc == 0:
            for (key, value) in self.mq_config.source_topic.items():
                LOGGER.warning(f"Subscribing tp {value}")
                mqttc.subscribe(value)
        elif rc == CONNECT_FAILED_NOT_AUTHORISED:
            self.__run_mqtt()
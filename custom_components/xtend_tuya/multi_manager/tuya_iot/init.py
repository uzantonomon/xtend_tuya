from __future__ import annotations

import requests
from typing import Optional, Literal, Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from tuya_iot import (
    AuthType,
    TuyaOpenAPI,
)

from .xt_tuya_iot_manager import (
    XTIOTDeviceManager,
)
from ..shared.interface.device_manager import (
    XTDeviceManagerInterface,
)
from ..shared.shared_classes import (
    XTConfigEntry,
)
from ..shared.device import (
    XTDevice,
)

from .const import (
    CONF_ACCESS_ID,
    CONF_AUTH_TYPE,
    CONF_ENDPOINT_OT,
    CONF_ACCESS_SECRET,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_COUNTRY_CODE,
    CONF_APP_TYPE,
)
from .util import (
    prepare_value_for_property_update,
)

from .xt_tuya_iot_data import (
    TuyaIOTData,
)
from .xt_tuya_iot_mq import (
    XTIOTOpenMQ,
)
from .xt_tuya_iot_home_manager import (
    XTIOTHomeManager,
)
from ..multi_manager import (
    MultiManager,
)
from ...const import (
    DOMAIN,
    MESSAGE_SOURCE_TUYA_IOT,
    LOGGER,
)

def get_plugin_instance() -> XTTuyaIOTDeviceManagerInterface | None:
    return XTTuyaIOTDeviceManagerInterface()

class XTTuyaIOTDeviceManagerInterface(XTDeviceManagerInterface):
    def __init__(self) -> None:
        super().__init__()
        self.iot_account: TuyaIOTData = None
        self.hass: HomeAssistant = None

    def get_type_name(self) -> str:
        return MESSAGE_SOURCE_TUYA_IOT

    async def setup_from_entry(self, hass: HomeAssistant, config_entry: XTConfigEntry, multi_manager: MultiManager) -> bool:
        self.multi_manager: MultiManager = multi_manager
        self.hass = hass
        self.sharing_account: TuyaIOTData = await self._init_from_entry(hass, config_entry)
        if self.sharing_account:
            return True
        return False
    
    async def _init_from_entry(self, hass: HomeAssistant, config_entry: XTConfigEntry) -> TuyaIOTData | None:
        if (
            config_entry.options is None
            or CONF_AUTH_TYPE     not in config_entry.options
            or CONF_ENDPOINT_OT   not in config_entry.options
            or CONF_ACCESS_ID     not in config_entry.options
            or CONF_ACCESS_SECRET not in config_entry.options
            or CONF_USERNAME      not in config_entry.options
            or CONF_PASSWORD      not in config_entry.options
            or CONF_COUNTRY_CODE  not in config_entry.options
            or CONF_APP_TYPE      not in config_entry.options
            ):
            return None
        auth_type = AuthType(config_entry.options[CONF_AUTH_TYPE])
        api = TuyaOpenAPI(
            endpoint=config_entry.options[CONF_ENDPOINT_OT],
            access_id=config_entry.options[CONF_ACCESS_ID],
            access_secret=config_entry.options[CONF_ACCESS_SECRET],
            auth_type=auth_type,
        )
        api.set_dev_channel("hass")
        try:
            if auth_type == AuthType.CUSTOM:
                response = await hass.async_add_executor_job(
                    api.connect, config_entry.options[CONF_USERNAME], config_entry.options[CONF_PASSWORD]
                )
            else:
                response = await hass.async_add_executor_job(
                    api.connect,
                    config_entry.options[CONF_USERNAME],
                    config_entry.options[CONF_PASSWORD],
                    config_entry.options[CONF_COUNTRY_CODE],
                    config_entry.options[CONF_APP_TYPE],
                )
        except requests.exceptions.RequestException as err:
            raise ConfigEntryNotReady(err) from err

        if response.get("success", False) is False:
            raise ConfigEntryNotReady(response)
        mq = XTIOTOpenMQ(api)
        mq.start()
        device_manager = XTIOTDeviceManager(self, api, mq)
        device_ids: list[str] = list()
        home_manager = XTIOTHomeManager(api, mq, device_manager, self)
        device_manager.add_device_listener(self.multi_device_listener)
        return TuyaIOTData(
            device_manager=device_manager,
            mq=mq,
            device_ids=device_ids,
            home_manager=home_manager)

    def update_device_cache(self):
        self.iot_account.home_manager.update_device_cache()
        new_device_ids: list[str] = [device_id for device_id in self.iot_account.device_manager.device_map]
        self.iot_account.device_ids.clear()
        self.iot_account.device_ids.extend(new_device_ids)
    
    def get_available_device_maps(self) -> list[dict[str, XTDevice]]:
        return [self.iot_account.device_manager.device_map]
    
    def refresh_mq(self):
        pass
    
    def remove_device_listeners(self) -> None:
        self.iot_account.device_manager.remove_device_listener(self.multi_device_listener)
    
    def unload(self):
        pass
    
    def on_message(self, msg: str):
        self.iot_account.device_manager.on_message(msg)
    
    def query_scenes(self) -> list:
        return self.iot_account.home_manager.query_scenes()
    
    def get_device_stream_allocate(
            self, device_id: str, stream_type: Literal["flv", "hls", "rtmp", "rtsp"]
    ) -> Optional[str]:
        if device_id in self.iot_account.device_ids:
            return self.iot_account.device_manager.get_device_stream_allocate(device_id, stream_type)
    
    def get_device_registry_identifiers(self) -> list:
        return [DOMAIN]
    
    def get_domain_identifiers_of_device(self, device_id: str) -> list:
        return [DOMAIN]

    def on_add_device(self, device: XTDevice):
        pass
    
    def on_mqtt_stop(self):
        if self.iot_account.device_manager.mq:
            self.iot_account.device_manager.mq.stop()
    
    def on_post_setup(self):
        pass
    
    def get_platform_descriptors_to_merge(self, platform: Platform) -> Any:
        pass
    
    def send_commands(self, device_id: str, commands: list[dict[str, Any]]):
        open_api_regular_commands: list[dict[str, Any]] = []
        property_commands: list[dict[str, Any]] = []
        devices = self.get_devices_from_device_id(device_id)
        for command in commands:
            command_code  = command["code"]
            command_value = command["value"]

            #Filter commands that don't require the use of OpenAPI
            skip_command = False
            prop_command = False
            regular_command = False
            for device in devices:
                if dpId := self.multi_manager._read_dpId_from_code(command_code, device):
                    if not device.local_strategy[dpId].get("use_open_api", False):
                        skip_command = True
                        break
                    if device.local_strategy[dpId].get("property_update", False):
                        prop_command = True
                    else:
                        regular_command = True
                else:
                    skip_command = True
            if not skip_command:
                if regular_command:
                    command_dict = {"code": command_code, "value": command_value}
                    open_api_regular_commands.append(command_dict)
                elif prop_command:
                    command_value = prepare_value_for_property_update(device.local_strategy[dpId], command_value)
                    property_dict = {str(command_code): command_value}
                    property_commands.append(property_dict)
        
        if open_api_regular_commands:
            LOGGER.debug(f"Sending Open API regular command : {open_api_regular_commands}")
            self.iot_account.device_manager.send_commands(device_id, open_api_regular_commands)
        if property_commands:
            LOGGER.debug(f"Sending property command : {property_commands}")
            self.iot_account.device_manager.send_property_update(device_id, property_commands)

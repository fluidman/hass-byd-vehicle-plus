"""Base entity mixins for BYD Vehicle."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pybyd import (
    BydControlPasswordError,
    BydEndpointNotSupportedError,
    BydRemoteControlError,
    VehicleSnapshot,
)
from pybyd.models.gps import GpsInfo
from pybyd.models.hvac import HvacStatus
from pybyd.models.realtime import VehicleRealtimeData
from pybyd.models.vehicle import Vehicle

from .const import DOMAIN
from .coordinator import BydDataUpdateCoordinator, get_vehicle_display

_LOGGER = logging.getLogger(__name__)


class BydVehicleEntity(CoordinatorEntity[BydDataUpdateCoordinator]):
    """Mixin providing common properties for BYD vehicle entities."""

    _vin: str
    _vehicle: Vehicle

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._vin)},
            name=get_vehicle_display(self._vehicle),
            manufacturer=self._vehicle.brand_name or "BYD",
            model=self._vehicle.model_name,
            serial_number=self._vin,
            hw_version=self._vehicle.tbox_version or None,
        )

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        return self.coordinator.data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"vin": self._vin}

    def _snapshot(self) -> VehicleSnapshot | None:
        return self.coordinator.data

    def _get_realtime(self) -> VehicleRealtimeData | None:
        snap = self._snapshot()
        return snap.realtime if snap is not None else None

    def _get_hvac_status(self) -> HvacStatus | None:
        snap = self._snapshot()
        return snap.hvac if snap is not None else None

    def _get_gps(self) -> GpsInfo | None:
        snap = self._snapshot()
        return snap.gps if snap is not None else None

    def _get_source_obj(self, source: str = "realtime") -> Any | None:
        if source == "realtime":
            return self._get_realtime()
        if source == "hvac":
            return self._get_hvac_status()
        if source == "gps":
            return self._get_gps()
        return None

    def _is_vehicle_on(self) -> bool:
        realtime = self._get_realtime()
        if realtime is None:
            return False
        return bool(realtime.is_vehicle_on)

    def _command_pin_error_message(self) -> str:
        if self.coordinator.has_pin_configured:
            return (
                "Command PIN is invalid or cloud control is locked — "
                "reconfigure the integration to update your Control PIN"
            )
        return "Control PIN is not configured; set Control PIN to enable actions"

    async def _execute_car_command(self, coro: Any, *, command: str) -> None:
        if not self.coordinator.has_operation_pin:
            raise HomeAssistantError(self._command_pin_error_message())
        try:
            await coro
        except BydRemoteControlError as exc:
            _LOGGER.warning(
                "%s command sent but cloud reported failure — pyBYD state engine handles projection: %s",
                command,
                exc,
            )
        except BydControlPasswordError as exc:
            if exc.code == "5006":
                msg = "Cloud control temporarily locked by BYD — try again later"
            elif exc.code == "commands_disabled":
                msg = "Command access not verified — reconfigure your Control PIN"
            elif exc.code == "5005":
                msg = "Command PIN is wrong — reconfigure the integration"
            else:
                msg = f"Command PIN error: {exc}"
            _LOGGER.warning("%s command failed: %s (code=%s)", command, msg, exc.code)
            raise HomeAssistantError(msg) from exc
        except BydEndpointNotSupportedError as exc:
            msg = "This command is not supported by your vehicle"
            _LOGGER.warning("%s command blocked: %s", command, exc)
            raise HomeAssistantError(msg) from exc
        except Exception as exc:
            raise HomeAssistantError(str(exc)) from exc


class BydActionEntity(BydVehicleEntity):
    """Base for action entities requiring a verified Control PIN."""

    @property
    def entity_registry_enabled_default(self) -> bool:
        enabled_default = getattr(self, "_attr_entity_registry_enabled_default", None)
        if enabled_default is None:
            description = getattr(self, "entity_description", None)
            enabled_default = getattr(description, "entity_registry_enabled_default", True)
        return bool(enabled_default) and self.coordinator.has_pin_configured

    def _ensure_action_allowed(self) -> None:
        if not self.coordinator.has_operation_pin:
            raise HomeAssistantError(self._command_pin_error_message())

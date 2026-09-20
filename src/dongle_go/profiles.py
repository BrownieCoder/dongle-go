"""Hardware validation is an explicit release gate, never inferred from USB IDs."""
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Profile:
    name: str
    manufacturer: str
    model: str
    firmware: str
    usbnet: Mapping[str, int]
    evidence: str
    requires_reboot: bool = True
    vid: int | None = None
    pid: int | None = None
    at_interfaces: tuple[str, ...] = ()


# No real module/firmware combination has yet completed hardware qualification.
# Do not add a profile without publishing reproducible qualification evidence.
VERIFIED_PROFILES: tuple[Profile, ...] = ()


def match_profile(manufacturer: str, model: str, firmware: str,
                  profiles: tuple[Profile, ...] = VERIFIED_PROFILES, *,
                  vid=None, pid=None, interface=None) -> Profile | None:
    return next((p for p in profiles if p.evidence and
                 p.vid == vid and p.pid == pid and
                 interface in p.at_interfaces and
                 (p.manufacturer, p.model, p.firmware) ==
                 (manufacturer, model, firmware)), None)

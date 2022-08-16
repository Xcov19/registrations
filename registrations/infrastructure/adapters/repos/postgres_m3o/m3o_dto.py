from __future__ import annotations

from registrations.domain.hospital import registration


def parse_to_dict(table: str, hospital_entry: registration.HospitalEntityType) -> dict:
    """Parses a hospital entry to a dictionary."""
    hospital_dict: dict[str, str | float | dict] = {}
    hospital_dict["id"] = hospital_entry.hospital_id.hex
    hospital_dict["name"] = hospital_entry.hospital_name
    hospital_dict = {
        **hospital_dict,
        "address": hospital_entry.address.dict(exclude_unset=True),
    }
    if hospital_entry.ownership_type:
        hospital_dict["ownership_type"] = str(hospital_entry.ownership_type.value)
    hospital_dict["contact_number"] = hospital_entry.phone_number.number
    hospital_dict["added_since"] = hospital_entry.added_since.isoformat(
        timespec="milliseconds"
    )
    if hospital_entry.geo_location:
        hospital_dict = {
            **hospital_dict,
            "geo_location": hospital_entry.geo_location.dict(exclude_unset=True),
        }
    if table == "unverified_hospital" and isinstance(
        hospital_entry, registration.UnverifiedRegisteredHospital
    ):
        hospital_dict = {
            **hospital_dict,
            "key_contact_registrar": hospital_entry.key_contact_registrar.dict(
                exclude_unset=True
            ),
        }
    elif table == "unclaimed_hospital" and isinstance(
        hospital_entry, registration.UnclaimedHospital
    ):
        hospital_dict["verified_status"] = str(hospital_entry.verified_status.value)
    return hospital_dict

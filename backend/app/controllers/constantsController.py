from fastapi import APIRouter

router = APIRouter(tags=["Constants"])

CONSTANTS = {
    "property_types": ["house", "apartment", "land", "commercial"],
    "transaction_types": ["sale", "rent"],
    "property_statuses": ["pending", "approved", "rejected", "sold"],
    "appointment_statuses": ["pending", "confirmed", "completed", "cancelled"],
    "appointment_types": ["viewing", "inspection"],
    "user_roles": ["admin", "advisor", "client"],
    "followup_types": ["satisfaction_survey", "check_in_call", "referral_request", "maintenance_reminder"],
    "followup_statuses": ["pending", "completed", "skipped"],
    "contact_statuses": ["new", "contacted", "closed"],
}


@router.get("/constants")
def get_constants():
    return CONSTANTS

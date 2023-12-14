from fastapi import APIRouter, Depends

vendor_router = APIRouter()

# @vendor_router.get("/{vendor_username}", dependencies=[Depends(get_current_vendor)])
# async def get_vendor(vendor_username: str, session: Annotated[Session, Depends(get_session)]):
#     return vendor.get_vendor_username(session, vendor_username)

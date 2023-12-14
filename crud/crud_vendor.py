from crud.base import CRUDBase
from db.models import Vendor
from schemas.vendor import VendorCreate


class CRUDVendor(CRUDBase[Vendor, VendorCreate]):
    pass

vendor = CRUDVendor(Vendor)

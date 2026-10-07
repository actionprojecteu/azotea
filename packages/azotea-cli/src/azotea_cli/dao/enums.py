
from sqlalchemy import Enum
from lica.sqlalchemy.metadata import metadata
from ..core.enums import BayerPattern, HeaderType, ImageType, ValidState

# --------------
# Database Enums
# --------------
#
DbValidState: Enum = Enum(
    ValidState,
    name="db_valid_state",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

DbBayerPattern: Enum = Enum(
    BayerPattern,
    name="db_bayer_pattern",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

DbHeaderType: Enum = Enum(
    HeaderType,
    name="db_header_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

DbImageType: Enum = Enum(
    ImageType,
    name="db_image_type",
    create_constraint=False,
    metadata=metadata,
    validate_strings=True,
    values_callable=lambda x: [e.name for e in x],
)

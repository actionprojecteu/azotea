caso de uso de repors, cada resultado de report una dataclass y emplear mappings()

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SkyBrightnessDTO:
    image_id: int
    name: str
    display_name: str
    comment: str | None
    width: int
    height: int
    aver_R: float
    vari_R: float
    aver_G1: float
    vari_G1: float
    aver_G2: float
    vari_G2: float
    aver_B: float
    vari_B: float


def get_sky_brightness(self) -> list[SkyBrightnessDTO]:
    with get_db_session() as session:
        result = session.execute(selectable).mappings()

        return [
            SkyBrightnessDTO(**row)
            for row in result
        ]

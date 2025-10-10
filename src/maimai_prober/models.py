from datetime import datetime
from decimal import Decimal
from typing import Self

from maimai_py import Score as MpyScore
from maimai_py.models import FCType, FSType, LevelIndex, RateType, SongType
from sqlmodel import JSON, Column, Field, SQLModel


class Score(SQLModel, table=True):
    __tablename__ = "tbl_score"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    song_id: int = Field(index=True)
    level_index: LevelIndex
    achievements: Decimal = Field(default=None, max_digits=7, decimal_places=4)
    dx_score: int
    dx_rating: float
    play_count: int
    fc: FCType | None
    fs: FSType | None
    rate: RateType
    type: SongType
    uuid: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def from_mpy(mpy_score: MpyScore, uuid: str):
        return Score(
            song_id=mpy_score.id,
            level_index=mpy_score.level_index,
            achievements=Decimal(mpy_score.achievements or 0),
            fc=mpy_score.fc,
            fs=mpy_score.fs,
            dx_score=mpy_score.dx_score or 0,
            dx_rating=mpy_score.dx_rating or 0,
            play_count=mpy_score.play_count or 0,
            rate=mpy_score.rate,
            type=mpy_score.type,
            uuid=uuid,
        )

    def as_mpy(self) -> MpyScore:
        return MpyScore(
            id=self.song_id,
            level="Unknown",
            level_index=self.level_index,
            achievements=float(self.achievements),
            fc=self.fc,
            fs=self.fs,
            dx_score=self.dx_score,
            dx_rating=self.dx_rating,
            play_time=None,
            play_count=self.play_count,
            rate=self.rate,
            type=self.type,
        )

    def merge_mpy(self, new: MpyScore | None) -> Self:
        if new is not None:
            if self.song_id != new.id or self.level_index != new.level_index or self.type != new.type:
                raise ValueError("Cannot join scores with different songs, level indexes or types")
            selected_value = None
            if self.achievements != new.achievements:
                selected_value = Decimal(max(self.achievements or 0, new.achievements or 0))
                self.achievements = selected_value
            if self.dx_rating != new.dx_rating and new.dx_rating is not None:
                # theoretically, this should be trigger only when level_value changes or better score is achieved
                selected_value = new.dx_rating
                self.dx_rating = selected_value
            if self.dx_score != new.dx_score:
                selected_value = max(self.dx_score or 0, new.dx_score or 0)
                self.dx_score = selected_value
            if self.fc != new.fc:
                self_fc = self.fc.value if self.fc is not None else 100
                other_fc = new.fc.value if new.fc is not None else 100
                selected_value = min(self_fc, other_fc)
                self.fc = FCType(selected_value) if selected_value != 100 else None
            if self.fs != new.fs:
                self_fs = self.fs.value if self.fs is not None else -1
                other_fs = new.fs.value if new.fs is not None else -1
                selected_value = max(self_fs, other_fs)
                self.fs = FSType(selected_value) if selected_value != -1 else None
            if self.rate != new.rate:
                selected_value = min(self.rate.value, new.rate.value)
                self.rate = RateType(selected_value)
            if self.play_count != new.play_count:
                selected_value = max(self.play_count or 0, new.play_count or 0)
                self.play_count = selected_value
            if selected_value is not None:
                self.updated_at = datetime.utcnow()
        return self

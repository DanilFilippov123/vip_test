from pydantic import field_validator, BaseModel


class SensorDataErrorInfo(BaseModel):
    offset: int
    error: str


class SensorDataInfo(BaseModel):
    success_batches_read: int
    errors: list[SensorDataErrorInfo]


class Batch(BaseModel):
    status: int
    current_value_counter: int
    pressure_value: float

    @staticmethod
    def from_bytearray(data: bytearray):
        val = float(int.from_bytes((data[2], data[3]), "big"))
        return Batch(status=data[0], current_value_counter=data[1], pressure_value=val)

    @field_validator("status")
    @classmethod
    def check_status(cls, v: int):
        assert v == 0x80, "Invalid status"
        return hex(v)[2:]

    @field_validator("current_value_counter")
    @classmethod
    def check_counter(cls, v):
        assert 0 <= v <= 0x7f, "Invalid current value counter"
        return v

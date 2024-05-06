import re

from fastapi import UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models import SensorData
from scheme import Batch, SensorDataInfo, SensorDataErrorInfo


async def process_good_batch(batch: Batch, db: Session):
    db_sensor_data = SensorData(
        status=batch.status,
        current_value_counter=batch.current_value_counter,
        pressure_value=batch.pressure_value,
    )
    db.add(db_sensor_data)
    db.commit()


async def process_sensor_file(file: UploadFile, db: Session, mode: str = "soft") -> SensorDataInfo:
    """
    Обработка текстового файла с информацией от датчика в HEX формате
    :param file: Файловый объект, который содержит данные
    :param db: Сессия базы, куда сохранить данные
    :param mode: Режим обработки, может быть:
                    - "soft": Обработка с возможностью пропуска пакетов, ищет пакеты по паттерну
                    - "strict": Последовательная обработка данных, без возможности пропусков
    :return:
    """
    byte_array = await file.read()
    file_str = byte_array.decode("ascii")
    match mode:
        case "soft":
            return await process_sensor_data_str_soft(file_str, db)
        case "strict":
            return await process_sensor_data_from_string_strict(file_str, db)
        case _:
            raise ValueError("Invalid mode")


async def process_sensor_data_str_soft(hex_str: str, db: Session) -> SensorDataInfo:
    """
        Ищет в строке байты похожие на пакеты начинающиеся на 0x80, допускает пропуски, может не определить ошибки!!!
        :param hex_str: Строка с данными в формате HEX
        :param db: Сессия базы, куда сохранить данные
        :return: Pydantic модель  содержащую информацию о считанных пакетах
    """
    errors: list[SensorDataErrorInfo] = []
    success_batches = 0
    for match_batch in re.finditer(r"80[0-9a-fA-F]{6}", hex_str):
        data = bytearray.fromhex(match_batch.group(0))
        try:
            batch = Batch.from_bytearray(data)
            await process_good_batch(batch, db)
            success_batches += 1
        except ValidationError as e:
            errors.append(SensorDataErrorInfo(offset=match_batch.pos, error="Validation error}"))
    return SensorDataInfo(success_batches_read=success_batches, errors=errors)


async def process_sensor_data_from_string_strict(s: str, db: Session) -> SensorDataInfo:
    """
    Последовательно читает строку по 4 байта, не допускает пропуски
    :param s: Строка с данными в формате HEX
    :param db: Сессия базы, куда сохранить данные
    :return: Pydantic модель  содержащую информацию о считанных пакетах
    """
    if len(s) % 4 != 0:
        s = s[:len(s) - (len(s) % 4)]
    try:
        decoded_hex = bytearray.fromhex(s)
    except ValueError as e:
        return SensorDataInfo(success_batches_read=0,
                              errors=[SensorDataErrorInfo(offset=0,
                                                          error="Invalid hex string")])
    return await process_sensor_data_bytes_strict(decoded_hex, db)


async def process_sensor_data_bytes_strict(decoded_hex: bytearray, db: Session) -> SensorDataInfo:
    errors: list[SensorDataErrorInfo] = []
    success_batches = 0

    for i in range(0, len(decoded_hex), 4):
        try:
            batch: Batch = Batch.from_bytearray(decoded_hex)
            await process_good_batch(batch, db)
            success_batches += 1
        except ValidationError as e:
            errors.append(SensorDataErrorInfo(offset=i, error="Validation error}"))
        except IndexError:
            errors.append(SensorDataErrorInfo(offset=i, error="Invalid length"))

    return SensorDataInfo(success_batches_read=success_batches, errors=errors)

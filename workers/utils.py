from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import (
    INTEGER,
    NVARCHAR,
    BOOLEAN,
    VARBINARY,
    DATE,
    DATETIME,
    FLOAT,
)
from sqlalchemy.sql.expression import ColumnExpressionArgument
from datetime import datetime, date
from sqlalchemy import between, or_
from typing import Dict, List
import logging
import json


def cast_value(column: Column, value: str):
    """Helper function to cast values based on column type"""
    # Get the type in Python of the column in the DB
    python_type = column.type.python_type
    try:
        if python_type is str:
            return str(value)
        elif python_type is int:
            return int(value)
        elif python_type is float:
            return float(value)
        elif python_type is bool:
            return bool(value)
        elif python_type is bytes:
            return bytes(value, "utf-8")
        elif python_type is date:
            return datetime.strptime(value, "%Y-%m-%d").date()
        elif python_type is datetime:
            return datetime.strptime(value, "%Y-%m-%d")
        return value
    except Exception as e:
        logging.error(f"Error casting value for column {column.name}: {e}")
        raise ValueError(f"Error casting value for column {column.name}: {e}")


def handle_between_condition(column: Column, value: str) -> ColumnExpressionArgument:
    """Handle BETWEEN condition"""
    # convert the str to list
    value_list = json.loads(value)
    # checking and casting
    if not isinstance(value_list, list) or len(value_list) != 2:
        raise ValueError("BETWEEN operator requires a list of two values.")
    start_value = cast_value(column, value_list[0])
    end_value = cast_value(column, value_list[1])
    return between(column, start_value, end_value)


def handle_contains_condition(column: Column, value: str) -> ColumnExpressionArgument:
    """Handle CONTAINS condition"""
    # convert the str to list
    value_list = json.loads(value)
    or_conditions = []
    # checking
    if not isinstance(value_list, list) or len(value_list) < 2:
        raise ValueError(
            "CONTAINS operator requires a list with at least 2 values separated by a comma."
        )
    for value in value_list:
        casted_value = cast_value(column, value)
        or_conditions.append(column == casted_value)
    return or_(*or_conditions)


def building_filters(
    column_schema: dict, conditions: List[Dict[str, str]]
) -> List[ColumnExpressionArgument]:
    """Build conditions using SQLAlchemy"""
    operator_map = {
        "=": lambda col, val: col == val,
        "<>": lambda col, val: col != val,
        ">": lambda col, val: col > val,
        "<": lambda col, val: col < val,
        ">=": lambda col, val: col >= val,
        "<=": lambda col, val: col <= val,
        # TODO: Not support "LIKE" for now. Will implement later
        # "like": lambda col, val: cast(col, String).like(val),
        # TODO: Think more about casting the varbinary type here
    }

    built_filters = []
    for col in conditions:
        # Get the column as SQL structure, value and the operator for each condition
        column: Column = column_schema[col["column_name"]]
        operator = col["operator"].strip().lower()
        value = col["value"]

        if operator == "between":
            built_filters.append(handle_between_condition(column, value))
        elif operator == "contains":
            built_filters.append(handle_contains_condition(column, value))
        elif operator in operator_map:
            casted_value = cast_value(column, value)
            built_filters.append(operator_map[operator](column, casted_value))
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    return built_filters


def forming_columns_schema(conditions: list[dict]):
    """Convert text columns to columns defined in SQLAlchemy based on the list of passed conditions"""
    column_definitions = {}
    for condition in conditions:
        column_name = condition["column_name"]
        data_type = condition["data_type"]
        # Ignoring some type checks here because SQLAlchemy Column schema captured correctly the Column type,
        # but MyPy keeps warning the mismatching, which is potentially misleading
        if data_type == "int":
            column_definitions[column_name] = Column(column_name, INTEGER)
        elif data_type == "date":
            column_definitions[column_name] = Column(column_name, DATE)  # type: ignore
        elif data_type == "datetime":
            column_definitions[column_name] = Column(column_name, DATETIME)  # type: ignore
        elif data_type == "float":
            column_definitions[column_name] = Column(column_name, FLOAT)
        elif data_type == "nvarchar":
            column_definitions[column_name] = Column(column_name, NVARCHAR)  # type: ignore
        elif data_type == "varbinary":
            column_definitions[column_name] = Column(column_name, VARBINARY)  # type: ignore
        elif data_type == "boolean":
            column_definitions[column_name] = Column(column_name, BOOLEAN)  # type: ignore
    return column_definitions

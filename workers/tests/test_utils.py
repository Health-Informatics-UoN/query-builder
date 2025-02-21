import pytest
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import (
    INTEGER,
    NVARCHAR,
    BOOLEAN,
    VARBINARY,
    DATE,
    DATETIME,
    FLOAT,
)
from datetime import date, datetime

# Ignore the error missing import below because this import was set up by pytest.ini file,
# but MyPy can't recognise this
from utils import (  # type: ignore
    cast_value,
    handle_between_condition,
    handle_contains_condition,
    building_filters,
    forming_columns_schema,
)


class TestCastValue:
    def test_string_casting(self):
        # Test NVARCHAR column
        str_col = Column("name", NVARCHAR(50))
        assert cast_value(str_col, "test") == "test"
        assert cast_value(str_col, "123") == "123"
        assert isinstance(cast_value(str_col, "456"), str)

    def test_integer_casting(self):
        # Test INTEGER column
        int_col = Column("id", INTEGER)
        assert cast_value(int_col, "123") == 123
        assert isinstance(cast_value(int_col, "456"), int)

        # Test error handling for invalid integer
        with pytest.raises(ValueError):
            cast_value(int_col, "abc")

    def test_float_casting(self):
        # Test FLOAT column
        float_col = Column("price", FLOAT)
        assert cast_value(float_col, "123.45") == 123.45
        assert isinstance(cast_value(float_col, "456.78"), float)

        # Test error handling for invalid float
        with pytest.raises(ValueError):
            cast_value(float_col, "abc")

    def test_boolean_casting(self):
        # Test BOOLEAN column
        bool_col = Column("active", BOOLEAN)
        # Python bool() converts any non-empty string to True
        assert cast_value(bool_col, "True") is True
        assert (
            cast_value(bool_col, "False") is True
        )  # Note: "False" as string is truthy!
        assert cast_value(bool_col, "") is False
        assert isinstance(cast_value(bool_col, "1"), bool)

    def test_varbinary_casting(self):
        # Test VARBINARY column
        binary_col = Column("data", VARBINARY(100))
        test_str = "hello world"
        result = cast_value(binary_col, test_str)
        print("result: ", result)
        assert isinstance(result, bytes)
        assert result == test_str.encode("utf-8")

        # Test with special characters
        special_chars = "áéíóú!@#$%"
        special_result = cast_value(binary_col, special_chars)
        assert special_result == special_chars.encode("utf-8")

    def test_date_casting(self):
        # Test DATE column
        date_col = Column("birth_date", DATE)
        result = cast_value(date_col, "2023-05-15")
        assert isinstance(result, date)
        assert result == date(2023, 5, 15)

        # Test error handling for invalid date format
        with pytest.raises(ValueError):
            cast_value(date_col, "15/05/2023")  # Wrong format

    def test_datetime_casting(self):
        # Test DATE column
        datetime_col = Column("birth_date", DATETIME)
        result = cast_value(datetime_col, "2023-05-15")
        assert isinstance(result, datetime)
        assert result == datetime(2023, 5, 15, 00, 00, 00)

        # Test error handling for invalid date format
        with pytest.raises(ValueError):
            cast_value(datetime_col, "15/05/2023 00:00:00")

    def test_unsupported_type(self):
        # Create a mock column with an unsupported type
        class MockType:
            @property
            def python_type(self):
                return complex  # Not handled in the function

        mock_col = Column("complex_num")
        mock_col.type = MockType()

        # Function should return the original value for unsupported types
        assert cast_value(mock_col, "1+2j") == "1+2j"


class TestHandleBetween:
    def test_handle_between_condition(self):
        column = Column("test_date", DATE)
        value = '["2025-02-20", "2025-02-21"]'
        condition = handle_between_condition(column, value)
        assert str(condition) == "test_date BETWEEN :test_date_1 AND :test_date_2"

    def test_handle_between_condition_invalid_value(self):
        column = Column("test_date", DATE)
        invalid_value = '["2025-02-20"]'  # Only one value instead of two
        with pytest.raises(
            ValueError,
            match="BETWEEN operator requires a list of two values.",
        ):
            handle_between_condition(column, invalid_value)


class TestHandleContains:
    def test_handle_contains_condition(self):
        column = Column("test_str", NVARCHAR)
        value = '["test1", "test2"]'
        condition = handle_contains_condition(column, value)
        assert str(condition) == "test_str = :test_str_1 OR test_str = :test_str_2"

    def test_handle_contains_invalid_condition(self):
        column = Column("test_str", NVARCHAR)
        invalid_value = '["test1"]'
        with pytest.raises(
            ValueError,
            match="CONTAINS operator requires a list with at least 2 values separated by a comma.",
        ):
            handle_contains_condition(column, invalid_value)


class TestBuildingFilters:
    def test_building_filters(self):
        column_schema = {
            "test_int": Column("test_int", INTEGER),
            "test_str": Column("test_str", NVARCHAR),
            "test_date": Column("test_date", DATE),
        }
        conditions = [
            {"column_name": "test_int", "operator": "=", "value": "123"},
            {
                "column_name": "test_str",
                "operator": "contains",
                "value": '["test1", "test2"]',
            },
            {
                "column_name": "test_date",
                "operator": "between",
                "value": '["2025-02-20", "2025-02-21"]',
            },
        ]
        filters = building_filters(column_schema, conditions)
        assert len(filters) == 3
        assert str(filters[0]) == "test_int = :test_int_1"
        assert str(filters[1]) == "test_str = :test_str_1 OR test_str = :test_str_2"
        assert str(filters[2]) == "test_date BETWEEN :test_date_1 AND :test_date_2"

    def test_building_filters_unsupported_operator(self):
        column_schema = {
            "test_int": Column("test_int", INTEGER),
        }
        conditions = [
            {"column_name": "test_int", "operator": "randomOperator", "value": "123"},
        ]
        with pytest.raises(
            ValueError,
            match="Unsupported operator: randomoperator",
        ):
            building_filters(column_schema, conditions)


def test_forming_columns_schema():
    conditions = [
        {"column_name": "test_int", "data_type": "int"},
        {"column_name": "test_str", "data_type": "nvarchar"},
        {"column_name": "test_date", "data_type": "date"},
        {"column_name": "test_datetime", "data_type": "datetime"},
        {"column_name": "test_float", "data_type": "float"},
        {"column_name": "test_bool", "data_type": "boolean"},
        {"column_name": "test_binary", "data_type": "varbinary"},
    ]
    column_schema = forming_columns_schema(conditions)
    assert isinstance(column_schema["test_int"], Column)
    assert isinstance(column_schema["test_str"], Column)
    assert isinstance(column_schema["test_date"], Column)
    assert isinstance(column_schema["test_datetime"], Column)
    assert isinstance(column_schema["test_float"], Column)
    assert isinstance(column_schema["test_bool"], Column)
    assert isinstance(column_schema["test_binary"], Column)
    assert str(column_schema["test_int"].type) == "INTEGER"
    assert str(column_schema["test_str"].type) == "NVARCHAR"
    assert str(column_schema["test_date"].type) == "DATE"
    assert str(column_schema["test_datetime"].type) == "DATETIME"
    assert str(column_schema["test_float"].type) == "FLOAT"
    assert str(column_schema["test_bool"].type) == "BOOLEAN"
    assert str(column_schema["test_binary"].type) == "VARBINARY"

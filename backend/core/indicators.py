from dataclasses import dataclass
from typing import Any, Callable, Protocol


class IndicatorModule(Protocol):
    CODE: str
    NAME: str
    DEFAULT_PROVINCE: str
    DEFAULT_TARGET_COVERAGE: float

    def validate_data_file(self, filepath): ...
    def load_sample_data(self, filepath): ...
    def build_report_summary(self, data, cutoff_date=None, province=None, target_coverage=None): ...
    def search_by_dni(self, data, dni: str, reference_date=None, province=None): ...
    def get_filter_options(self, data): ...


@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    module: object
    build_report_summary: Callable
    get_filter_options: Callable
    load_sample_data: Callable
    search_by_dni: Callable
    validate_data_file: Callable
    default_province: str = "ABANCAY"
    default_target_coverage: float = 0.0

    @classmethod
    def from_module(cls, module: Any) -> "IndicatorDefinition":
        return cls(
            code=module.CODE,
            name=module.NAME,
            module=module,
            build_report_summary=module.build_report_summary,
            get_filter_options=module.get_filter_options,
            load_sample_data=module.load_sample_data,
            search_by_dni=module.search_by_dni,
            validate_data_file=module.validate_data_file,
            default_province=getattr(module, "DEFAULT_PROVINCE", "ABANCAY"),
            default_target_coverage=getattr(module, "DEFAULT_TARGET_COVERAGE", 0.0),
        )

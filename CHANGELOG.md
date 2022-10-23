## [0.0.2] - 2022-10-07
### Added
- Group meals with different ids according to "magic table"
- New db tables meal_counter
- Logging on file

### Changed
- Meal implemented as dataclass
- Meal_id built inside Meal classes, as well as meal timestamp.
- Meal_repository accepting and returning Meal objects
- Simplified validation of meal form in controller
- Retrieving count from meal_counter_table

### Fixed
- Bug in retrieving last_week number from meal_service
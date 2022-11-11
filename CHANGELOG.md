## [0.0.3] - 2022-11-10
## Added
- Get replacement list 
- Extended meal service tests
- _pytest.ini_ file

## Fixed
- Returning current week also when requested with week number parameter

## [0.0.2] - 2022-10-07
### Added
- New db table meal_counter to store meal occurrences
- Domain object Meal Occurrences
- Db table aka to store id replacement
- Logging on file

### Changed
- Meal implemented as dataclass
- Meal_id built inside Meal classes, as well as meal timestamp.
- Meal_repository accepting and returning Meal objects
- Simplified validation of meal form in controller
- Retrieving count from meal_counter_table

### Fixed
- Bug in retrieving last_week number from meal_service
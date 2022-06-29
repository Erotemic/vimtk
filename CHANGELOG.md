# Changelog

We are currently working on porting this changelog to the specifications in
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Version 0.3.1] - Unreleased

### Fixed:

* vimtk.CONFIG can now be used to set the config.
* autoimport now respects the vimtk_auto_importable_modules config param


## [Version 0.3.0] - Unreleased

### Added:

* function `vimtk.mockvim` for easier development
* POC for python refactoring code


## [Version 0.2.9] - Unreleased

### Added 
* `vimtk.Mode` with basic functionality
* `vimtk.TextInsertor.overwrite` 

## [Version 0.2.8] - Unreleased

### Added 
* Simple mocking for vim args
* my special "dirty" paragraph formatter that still need to be cleaned up


## [Version 0.2.3] - Unreleased

### Added 
* snippets
* new config variable `g:vimtk_sys_path`

### Fixed
* Fails more gracefully when pyperclip not available 


## [Version 0.2.2] - Unreleased

### Added 
* vimtk#py_format_doctest
* vimtk#py_unformat_doctest

## [Version 0.2.1] - Unreleased

### Added 
* vimtk#remap_all_modes
* vimtk#remap_swap_keys


## [Version 0.2.0] 

### Added 
* vimtk#quickopen
* vimtk#insert_print_var_at_cursor
* vimtk#insert_timerit
* `_demo.vimmock` fork with enhancements for doctests.


## Version 0.1.1 - Unreleased

### Added
* Jedi google-docstring monkey patch


### Changed
* Cleanups
* Cleanup requirements


## Version 0.1.0

### Added
* Add `AutoImport`

### Fixed
* Fix requirements


## Version 0.0.2

### Added
* Add config option `vimtk_multiline_num_press_enter`.


## VERSION 0.0.1

* Initial version

# CHANGELOG


## v0.4.0 (2025-08-22)

### Chores

- Sync lock file and move test to dependency-groups
  ([`02937d3`](https://github.com/arunoruto/RefIdxDB/commit/02937d38096e878982d9e6fd86eb51acff9b1c88))

This changes makes the test suite unavailable for normal users!

- Try latin-1 encoding for dat files (aria too)
  ([`b5c0b27`](https://github.com/arunoruto/RefIdxDB/commit/b5c0b27024e0794d337e3e3fe4e971b1b1faf76a))

- Update refidxdb database
  ([`6b0799e`](https://github.com/arunoruto/RefIdxDB/commit/6b0799e3f9c471118230b658c225429d0807e15a))

### Code Style

- Format code with isort and Ruff Formatter
  ([`67b3aaf`](https://github.com/arunoruto/RefIdxDB/commit/67b3aaf7530ec750d59c912d83259a8dc78bb36f))

This commit fixes the style issues introduced in b5c0b27 according to the output from isort and Ruff
  Formatter.

Details: None

- Format code with isort and Ruff Formatter
  ([`4612ba2`](https://github.com/arunoruto/RefIdxDB/commit/4612ba22f0470f477f61195eec9ee01e576d70c4))

This commit fixes the style issues introduced in 47e13db according to the output from isort and Ruff
  Formatter.

Details: None

### Continuous Integration

- Fix name typo in job dependecies
  ([`32948cc`](https://github.com/arunoruto/RefIdxDB/commit/32948cc80e0c37f354a921b3b6a06110b9bd2fd5))

### Features

- Move from flake to devenv
  ([`2647fa5`](https://github.com/arunoruto/RefIdxDB/commit/2647fa584045a989177693e970002e2e50626752))

devenv seems to be easier to manage compared to flakes now and enables easier development between
  people!


## v0.3.0 (2025-04-30)

### Features

- Add w_column to handler
  ([`502a71f`](https://github.com/arunoruto/RefIdxDB/commit/502a71fa4ef34bb9d00ab1fe7a0c912bbb1bfba6))


## v0.2.1 (2025-04-30)

### Bug Fixes

- Remove exception for csv handling
  ([`e4dd329`](https://github.com/arunoruto/RefIdxDB/commit/e4dd329b69eb5ad4468306f467168370739284a2))


## v0.2.0 (2025-04-30)

### Features

- Add CSV support in handler
  ([`3b53cfe`](https://github.com/arunoruto/RefIdxDB/commit/3b53cfec421fe20d287771af2518b3c48b7de0aa))


## v0.1.2 (2025-04-29)

### Bug Fixes

- Trigger new release 2
  ([`10a0f2e`](https://github.com/arunoruto/RefIdxDB/commit/10a0f2e292be8572b73394b7672cb3c07c69bd34))


## v0.1.1 (2025-04-29)

### Bug Fixes

- Trigger new release
  ([`fc885fd`](https://github.com/arunoruto/RefIdxDB/commit/fc885fd3de91261a0c2304930944fa26b6790cfe))

### Continuous Integration

- Comment out build step
  ([`560d7a0`](https://github.com/arunoruto/RefIdxDB/commit/560d7a0b3b50b9f9cde4aead3b6cf03cd7ceb877))

This should have been done in the previous step

- Split coverage report into separate workflow
  ([`a78712e`](https://github.com/arunoruto/RefIdxDB/commit/a78712e78aca574e5b6fd695b28e3ac80646f117))


## v0.1.0 (2025-04-29)

### Bug Fixes

- Install uv as the build_command for semantic versioning
  ([`a1eacf5`](https://github.com/arunoruto/RefIdxDB/commit/a1eacf529d924ee7084fa148066978394346baf9))

- Install uv before semantic versioning starts
  ([`bca922c`](https://github.com/arunoruto/RefIdxDB/commit/bca922cc619db7d9ce2146e024e9f76ad9dada53))

### Continuous Integration

- Move to semantic versioning
  ([`78c034f`](https://github.com/arunoruto/RefIdxDB/commit/78c034f3e3c44bc04b2c295b6af537dd09648340))

### Features

- Remove poetry lock
  ([`eddf551`](https://github.com/arunoruto/RefIdxDB/commit/eddf551a6d55d1034679f608b52707b3e0b69768))

should trigger the first minor upgrade


## v0.0.8 (2024-12-14)

### Continuous Integration

- Add .deepsource.toml
  ([`73551ea`](https://github.com/arunoruto/RefIdxDB/commit/73551eafab74edac660426e91bddf1b5350ecc55))

### Refactoring

- Remove commented out code
  ([`ecf5b0b`](https://github.com/arunoruto/RefIdxDB/commit/ecf5b0bdc55705c93e6d1f4b94ae5c71afa64e80))

It is recommended to remove any commented code in your codebase.

- Remove unnecessary `pass`
  ([`7bc6970`](https://github.com/arunoruto/RefIdxDB/commit/7bc6970418834097b1851666257bb6da756c59ad))

The `pass` statement used here is not necessary. You can safely remove this.


## v0.0.6 (2024-12-09)


## v0.0.5 (2024-12-06)


## v0.0.4 (2024-12-03)


## v0.0.3 (2024-12-02)

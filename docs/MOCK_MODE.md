# Mock Mode

## Purpose

Mock mode allows users to prepare their Home Assistant setup before vehicle delivery or without access to the real BYD backend.

## Principles

- the Home Assistant integration remains the single user-facing integration
- mock mode connects to a separate emulator server
- entities should behave as closely as practical to real mode
- vehicle capabilities should be configurable per mock profile

## Planned configuration

When mock mode is selected, the integration should support settings such as:

- mock server URL
- optional mock API token
- optional vehicle profile
- optional scenario selection
- optional polling overrides

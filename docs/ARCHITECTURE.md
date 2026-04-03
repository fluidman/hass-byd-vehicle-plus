# Architecture

## Overview

This project is a Home Assistant custom integration with two connection modes:

- `real`: uses the real BYD backend through the existing integration logic
- `mock`: uses a separate mock server

## Design principles

- one Home Assistant integration for end users
- separate emulator backend in a different repository
- minimal changes to entity logic
- backend abstraction so entities do not care whether data comes from real or mock mode

## Planned backend abstraction

- `RealBydBackend`
- `MockBydBackend`

Both should expose the same internal methods for:
- authentication
- vehicle listing
- realtime data
- GPS data
- HVAC data
- charging data
- energy data
- remote commands

# hass-byd-vehicle-plus

A Home Assistant custom integration based on `jkaberg/hass-byd-vehicle`, extended with support for both:

- Real mode: connects to the real BYD backend like the original project
- Mock mode: connects to a separate mock server for testing, demos, and pre-delivery Home Assistant preparation

## Goals

- Keep compatibility with the original integration behavior in real mode
- Add a clean mock mode for users who want to prepare their dashboards, automations, and layouts before vehicle delivery
- Support a separate emulator project with configurable vehicle profiles and scenarios

## Project status

Early planning / bootstrap phase.

## Related project

- `byd-vehicle-mock-server`

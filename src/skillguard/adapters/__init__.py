"""Translate external storage formats to and from SkillGuard domain records.

The files adapter reads single files or repository folders, checks size limits,
and surfaces invalid-input diagnostics. Adapters do not detect capabilities.
Reporting and database adapters can be added without changing detector logic.
"""

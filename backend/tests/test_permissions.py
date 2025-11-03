"""
Unit tests for RBAC permission system

Tests permission logic without HTTP layer.
"""

import pytest
from app.core.permissions import (
    can_edit_environment,
    has_permission,
    Permission,
)
from app.models.user import User


class TestEnvironmentPermissions:
    """Test environment-level permission checks"""

    @pytest.mark.ci_critical
    def test_admin_can_edit_all_environments(self):
        """CI: Admin user can edit dev, staging, and production"""
        admin = User(
            id="admin-1",
            email="admin@example.com",
            password_hash="hash",
            name="Admin User",
            role="admin",
            is_active=True,
        )

        assert can_edit_environment(admin, "dev") is True
        assert can_edit_environment(admin, "staging") is True
        assert can_edit_environment(admin, "production") is True

    @pytest.mark.ci_critical
    def test_developer_blocked_from_production(self):
        """CI: Developer cannot edit production (security critical)"""
        developer = User(
            id="dev-1",
            email="dev@example.com",
            password_hash="hash",
            name="Developer User",
            role="developer",
            is_active=True,
        )

        # Developer can edit dev and staging
        assert can_edit_environment(developer, "dev") is True
        assert can_edit_environment(developer, "staging") is True
        
        # But NOT production (this is the critical security test)
        assert can_edit_environment(developer, "production") is False

    def test_qa_can_edit_staging_only(self):
        """QA role can edit staging but not dev/production"""
        qa_user = User(
            id="qa-1",
            email="qa@example.com",
            password_hash="hash",
            name="QA User",
            role="qa",
            is_active=True,
        )

        # QA can edit staging
        assert can_edit_environment(qa_user, "staging") is True
        
        # But not dev or production (read-only)
        assert can_edit_environment(qa_user, "dev") is False
        assert can_edit_environment(qa_user, "production") is False

    def test_viewer_readonly_everywhere(self):
        """Viewer role cannot edit any environment (read-only)"""
        viewer = User(
            id="viewer-1",
            email="viewer@example.com",
            password_hash="hash",
            name="Viewer User",
            role="viewer",
            is_active=True,
        )

        # Viewer cannot edit anything
        assert can_edit_environment(viewer, "dev") is False
        assert can_edit_environment(viewer, "staging") is False
        assert can_edit_environment(viewer, "production") is False

    def test_invalid_role_defaults_to_viewer(self):
        """Unknown role is treated as viewer (fail-safe)"""
        unknown_user = User(
            id="unknown-1",
            email="unknown@example.com",
            password_hash="hash",
            name="Unknown Role User",
            role="hacker",  # Invalid role
            is_active=True,
        )

        # Should default to viewer (read-only everywhere)
        assert can_edit_environment(unknown_user, "dev") is False
        assert can_edit_environment(unknown_user, "staging") is False
        assert can_edit_environment(unknown_user, "production") is False

    def test_inactive_user_blocked_from_editing(self):
        """Inactive user cannot edit any environment"""
        inactive_admin = User(
            id="inactive-1",
            email="inactive@example.com",
            password_hash="hash",
            name="Inactive Admin",
            role="admin",
            is_active=False,  # User deactivated
        )

        # Even admin role, but inactive = no permissions
        assert can_edit_environment(inactive_admin, "dev") is False
        assert can_edit_environment(inactive_admin, "staging") is False
        assert can_edit_environment(inactive_admin, "production") is False


class TestPermissionConstants:
    """Test Permission class constants exist"""

    def test_permission_constants_defined(self):
        """Permission constants are defined correctly"""
        # Just verify they exist and are strings
        assert isinstance(Permission.VIEW_PROJECT, str)
        assert isinstance(Permission.EDIT_PROJECT, str)
        assert isinstance(Permission.DELETE_PROJECT, str)
        assert isinstance(Permission.VIEW_CONFIG, str)
        assert isinstance(Permission.EDIT_CONFIG, str)
        assert isinstance(Permission.MANAGE_USERS, str)


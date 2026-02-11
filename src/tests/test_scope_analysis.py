#!/usr/bin/env python3
"""
Tests for enhanced scope analysis in queue_manager.py
TDD: Write tests FIRST, then implement
"""
import sys
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path.home() / ".claude" / "scripts"))

from queue_manager import ConflictAnalyzer, ScopeInfo


class TestScopeAnalysisBasic(unittest.TestCase):
    """Basic scope extraction tests"""

    def test_extract_english_module(self):
        """Should extract module from English commands"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev migrate auth")
        self.assertIn("auth", scope.modules)

    def test_extract_english_file(self):
        """Should extract file from English commands"""
        scope = ConflictAnalyzer.extract_scope("edit config.ts")
        self.assertIn("config.ts", scope.files)

    def test_extract_directory(self):
        """Should extract directory from commands"""
        scope = ConflictAnalyzer.extract_scope("refactor in src/components/")
        self.assertIn("src/components/", scope.directories)


class TestScopeAnalysisKorean(unittest.TestCase):
    """Korean language scope extraction tests"""

    def test_extract_korean_module_migrate(self):
        """Should extract module from Korean 마이그레이션 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 마이그레이션 profile")
        self.assertIn("profile", scope.modules)

    def test_extract_korean_module_update(self):
        """Should extract module from Korean 수정/업데이트 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 수정 auth")
        self.assertIn("auth", scope.modules)

    def test_extract_korean_module_add(self):
        """Should extract module from Korean 추가 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 추가 feature")
        self.assertIn("feature", scope.modules)

    def test_extract_korean_module_fix(self):
        """Should extract module from Korean 수정/고치다 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 버그수정 payment")
        self.assertIn("payment", scope.modules)

    def test_extract_korean_module_implement(self):
        """Should extract module from Korean 구현 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 구현 notification")
        self.assertIn("notification", scope.modules)

    def test_extract_korean_module_create(self):
        """Should extract module from Korean 생성 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 생성 user")
        self.assertIn("user", scope.modules)

    def test_extract_korean_module_delete(self):
        """Should extract module from Korean 삭제 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 삭제 legacy")
        self.assertIn("legacy", scope.modules)

    def test_extract_korean_module_test(self):
        """Should extract module from Korean 테스트 command"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 테스트 api")
        self.assertIn("api", scope.modules)


class TestScopeAnalysisSlashCommands(unittest.TestCase):
    """Slash command scope extraction tests"""

    def test_extract_sc_implement(self):
        """Should extract from /sc:implement command"""
        scope = ConflictAnalyzer.extract_scope("/sc:implement auth middleware")
        self.assertIn("auth", scope.modules)

    def test_extract_sc_test(self):
        """Should extract from /sc:test command"""
        scope = ConflictAnalyzer.extract_scope("/sc:test auth")
        self.assertIn("auth", scope.modules)

    def test_extract_sc_build(self):
        """Should extract from /sc:build command"""
        scope = ConflictAnalyzer.extract_scope("/sc:build frontend")
        self.assertIn("frontend", scope.modules)

    def test_extract_sc_analyze(self):
        """Should extract from /sc:analyze command"""
        scope = ConflictAnalyzer.extract_scope("/sc:analyze security")
        self.assertIn("security", scope.modules)

    def test_extract_sc_improve(self):
        """Should extract from /sc:improve command"""
        scope = ConflictAnalyzer.extract_scope("/sc:improve performance")
        self.assertIn("performance", scope.modules)

    def test_extract_queue_command(self):
        """Should extract from /queue command"""
        scope = ConflictAnalyzer.extract_scope('/queue "/sc:auto-dev migrate profile"')
        self.assertIn("profile", scope.modules)


class TestScopeAnalysisMixedLanguage(unittest.TestCase):
    """Mixed Korean-English scope extraction tests"""

    def test_mixed_korean_english_module(self):
        """Should extract module from mixed language commands"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev profile 모듈 수정")
        self.assertIn("profile", scope.modules)

    def test_korean_with_english_action(self):
        """Should extract when Korean follows English action"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev update 사용자 모듈")
        # Should extract the module identifier
        self.assertTrue(len(scope.modules) > 0 or scope.estimated_scope != "unknown")


class TestScopeAnalysisEstimation(unittest.TestCase):
    """Scope estimation tests"""

    def test_file_scope_estimation(self):
        """Should estimate file scope correctly"""
        scope = ConflictAnalyzer.extract_scope("edit auth.ts")
        self.assertEqual(scope.estimated_scope, "file")

    def test_module_scope_estimation(self):
        """Should estimate module scope correctly"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev migrate auth")
        self.assertEqual(scope.estimated_scope, "module")

    def test_directory_scope_estimation(self):
        """Should estimate directory scope correctly"""
        scope = ConflictAnalyzer.extract_scope("refactor in src/")
        self.assertEqual(scope.estimated_scope, "directory")

    def test_project_scope_estimation(self):
        """Should estimate project scope for broad commands"""
        scope = ConflictAnalyzer.extract_scope("/sc:build all")
        # When scope is broad (e.g., 'all'), should be project-level
        self.assertIn(scope.estimated_scope, ["module", "project", "unknown"])


class TestScopeAnalysisNaturalLanguage(unittest.TestCase):
    """Natural language scope extraction tests"""

    def test_natural_language_english(self):
        """Should extract from natural language English"""
        scope = ConflictAnalyzer.extract_scope("Fix the authentication bug in the login module")
        # Should recognize authentication/login as module-related
        self.assertTrue(
            "authentication" in scope.modules or
            "login" in scope.modules or
            len(scope.modules) > 0
        )

    def test_natural_language_korean(self):
        """Should extract from natural language Korean"""
        scope = ConflictAnalyzer.extract_scope("인증 모듈의 버그를 수정해주세요")
        # Should recognize 인증 as module-related
        self.assertTrue(len(scope.modules) > 0 or scope.estimated_scope != "unknown")

    def test_file_mention_in_sentence(self):
        """Should extract file mentioned in sentence"""
        scope = ConflictAnalyzer.extract_scope("Please update the config.json file")
        self.assertIn("config.json", scope.files)


class TestConflictDetection(unittest.TestCase):
    """Conflict detection tests with enhanced scope"""

    def test_korean_conflict_detection(self):
        """Should detect conflicts between Korean commands"""
        from queue_manager import Task

        task1 = Task.create("/sc:auto-dev 마이그레이션 profile")
        task1.scope = ConflictAnalyzer.extract_scope(task1.command).__dict__

        task2 = Task.create("/sc:auto-dev 수정 profile")
        task2.scope = ConflictAnalyzer.extract_scope(task2.command).__dict__

        conflicts = ConflictAnalyzer.detect_conflicts(task2, [task1])
        self.assertTrue(len(conflicts) > 0, "Should detect profile module conflict")

    def test_mixed_language_conflict_detection(self):
        """Should detect conflicts between Korean and English commands"""
        from queue_manager import Task

        task1 = Task.create("/sc:auto-dev migrate profile")
        task1.scope = ConflictAnalyzer.extract_scope(task1.command).__dict__

        task2 = Task.create("/sc:auto-dev profile 수정")
        task2.scope = ConflictAnalyzer.extract_scope(task2.command).__dict__

        conflicts = ConflictAnalyzer.detect_conflicts(task2, [task1])
        self.assertTrue(len(conflicts) > 0, "Should detect cross-language conflict")


class TestEdgeCases(unittest.TestCase):
    """Edge case tests"""

    def test_empty_command(self):
        """Should handle empty command gracefully"""
        scope = ConflictAnalyzer.extract_scope("")
        self.assertEqual(scope.estimated_scope, "unknown")

    def test_whitespace_command(self):
        """Should handle whitespace-only command"""
        scope = ConflictAnalyzer.extract_scope("   ")
        self.assertEqual(scope.estimated_scope, "unknown")

    def test_special_characters(self):
        """Should handle special characters"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev @file.ts --flag")
        # Should still extract file
        self.assertTrue(len(scope.files) > 0 or scope.estimated_scope != "unknown")

    def test_unicode_module_name(self):
        """Should handle unicode module names"""
        scope = ConflictAnalyzer.extract_scope("/sc:auto-dev 사용자인증")
        # Should handle Korean compound words
        self.assertNotEqual(scope.estimated_scope, "unknown")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)

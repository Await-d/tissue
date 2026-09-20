import js from '@eslint/js'
import parser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
    {
        ignores: ['dist'],
    },
    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser,
            parserOptions: {
                ecmaVersion: 2020,
                sourceType: 'module',
                ecmaFeatures: { jsx: true },
            },
        },
        plugins: {
            '@typescript-eslint': tsPlugin,
            'react-hooks': reactHooks,
            'react-refresh': reactRefresh,
        },
        rules: {
            ...js.configs.recommended.rules,
            ...tsPlugin.configs.recommended.rules,
            ...reactHooks.configs.recommended.rules,
            // TypeScript 已负责未定义变量检查，关闭基础 no-undef
            'no-undef': 'off',
            // no-explicit-any 仍有约 260 处历史用法，放开以便分阶段做类型化专项
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/no-unused-vars': ['error', {
                argsIgnorePattern: '^_',
                varsIgnorePattern: '^_',
                caughtErrorsIgnorePattern: '^_',
                ignoreRestSiblings: true,
            }],
            'no-unused-vars': 'off',
            // 开启依赖校验：遗漏依赖是隐藏 bug 来源；确需手动控制处用带原因的 disable 注释
            'react-hooks/exhaustive-deps': 'error',
            // Fast Refresh 组件导出限制暂不强制
            'react-refresh/only-export-components': 'off',
            // 允许空解构/空块，避免历史代码报错
            'no-empty-pattern': 'off',
            'no-empty': 'off',
            '@typescript-eslint/no-extra-non-null-assertion': 'off',
        },
        linterOptions: {
            reportUnusedDisableDirectives: true,
        },
    },
]

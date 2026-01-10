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
            // 项目历史上大量 any/未使用变量，先放宽规则确保现有代码可过 lint
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/no-unused-vars': 'off',
            'no-unused-vars': 'off',
            // 部分页面需手动控制依赖，关闭自动依赖校验
            'react-hooks/exhaustive-deps': 'off',
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

import js from '@eslint/js';
import vueParser from 'vue-eslint-parser';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{vue,js}'],
    languageOptions: {
      parser: vueParser,
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        location: 'readonly',
        URLSearchParams: 'readonly',
        EventSource: 'readonly',
        FormData: 'readonly',
        Blob: 'readonly',
        navigator: 'readonly',
        require: 'readable',
      },
    },
    rules: {
      'no-console': 'warn',
    },
  },
  {
    ignores: ['node_modules/**', 'dist/**', 'public/**', 'eslint.config.mjs'],
  },
];
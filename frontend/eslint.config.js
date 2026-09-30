import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import ts from 'typescript-eslint';
import globals from 'globals';

export default ts.config(
  { ignores: ['.quasar/**', 'dist/**', 'node_modules/**'] },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: { parserOptions: { parser: ts.parser, extraFileExtensions: ['.vue'] } },
  },
  {
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      'vue/html-self-closing': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      // Formatting is handled by Prettier; semantic Vue rules remain enabled.
      'vue/multiline-html-element-content-newline': 'off',
      'vue/html-closing-bracket-newline': 'off',
      'vue/html-indent': 'off',
    },
  },
);

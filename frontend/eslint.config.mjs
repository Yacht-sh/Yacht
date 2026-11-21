import js from "@eslint/js";
import prettierRecommended from "eslint-plugin-prettier/recommended";
import vue from "eslint-plugin-vue";
import globals from "globals";

const isProduction = process.env.NODE_ENV === "production";

export default [
  {
    ignores: ["dist/**", "node_modules/**"],
  },
  js.configs.recommended,
  ...vue.configs["flat/vue2-essential"],
  {
    files: ["src/**/*.{js,vue}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "no-console": isProduction ? "warn" : "off",
      "no-debugger": isProduction ? "warn" : "off",
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "vue/multi-word-component-names": "off",
      "vue/no-mutating-props": ["warn", { shallowOnly: true }],
      "vue/no-multiple-template-root": "off",
      "vue/no-reserved-component-names": "off",
      "vue/no-useless-template-attributes": "off",
      "vue/no-v-text-v-html-on-component": "warn",
      "vue/valid-v-slot": ["error", { allowModifiers: true }],
    },
  },
  {
    ...prettierRecommended,
    rules: {
      ...prettierRecommended.rules,
      "prettier/prettier": "warn",
    },
  },
];

import { extend } from "vee-validate";
import * as rules from "vee-validate/dist/rules";
import { messages } from "vee-validate/dist/locale/en.json";

Object.keys(rules).forEach(rule => {
  extend(rule, {
    ...rules[rule],
    message: messages[rule]
  });
});

extend("url", {
  validate: str => {
    const pattern = /https?:\/\/(([a-z0-9$-_@.&+!*"'(),]+(\.[a-z0-9$-_ @.&+!*"'(),]+)*)|(\d+.\d+.\d+.\d+))(:\d+)?\/.*/i;
    return !!pattern.test(str);
  },
  message: "This is not a valid URL"
});

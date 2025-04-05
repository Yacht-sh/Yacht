import { extend } from "vee-validate";
// import { required, email, max } from "vee-validate/dist/rules";
//
// extend("required", {
//   ...required,
//   message: "This field is required"
// });
//
// extend("max", {
//   ...max,
//   message: "This field must be {length} characters or less"
// });
//
// extend("email", {
//   ...email,
//   message: "This field must be a valid email"
// });
//
// // BUG
// // import { url } from "vee-validate/dist/rules";
// //
// // extend("url", {
// //   ...url,
// //   message: "This is not a valid URL"
// // });

import * as rules from "vee-validate/dist/rules";
import { messages } from "vee-validate/dist/locale/en.json";
Object.keys(rules).forEach(rule => {
  extend(rule, {
    ...rules[rule], // copies rule configuration
    message: messages[rule] // assign message
  });
});

extend("url", {
  validate: str => {
    const pattern = /https?:\/\/(([a-z0-9$-_@.&+!*"'(),]+(\.[a-z0-9$-_ @.&+!*"'(),]+)*)|(\d+.\d+.\d+.\d+))(:\d+)?\/.*/i;
    // var pattern = new RegExp('^(https?:\\/\\/)'+ // protocol
    //     '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
    //     '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
    //     '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
    //     '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
    //     '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
    return !!pattern.test(str);
  },
  message: "This is not a valid URL"
});

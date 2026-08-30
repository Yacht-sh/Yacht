import moment from "moment";

const VueUtils = {
  install(Vue) {
    Vue.filter("formatDate", (value, format) => {
      if (value) {
        return moment(moment.utc(value).toDate())
          .local()
          .format(format || "LLL");
      }
    });

    Vue.filter("truncate", function(value, limit, suffix) {
      if (value.length > limit) {
        let idx = value.lastIndexOf(" ", limit - 1);
        value = value.substring(0, idx ? idx : limit - 1) + (suffix || "…");
      }
      return value;
    });
  }
};

export default VueUtils;
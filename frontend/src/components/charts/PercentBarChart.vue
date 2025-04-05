<script>
import { mixins, Bar } from "vue-chartjs"; // We specify what type of chart we want from vue-chartjs and the mixins module
const { reactiveProp } = mixins;
export default {
  extends: Bar, //We are extending the base chart class as mentioned above
  mixins: [reactiveProp],
  props: {
    chartdata: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      options: {
        responsive: true,
        animation: {
          duration: 0
        },
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                stepSize: 1,
                min: 0,
                max: 100,
                maxTicksLimit: 5
              }
            }
          ]
        }
      }
    };
  },
  mounted() {
    this.renderChart(this.chartData, this.options);
  }
};
</script>

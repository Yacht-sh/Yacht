<script>
import { Line, mixins } from "vue-chartjs"; // We specify what type of chart we want from vue-chartjs and the mixins module
const { reactiveProp } = mixins;
export default {
  extends: Line, //We are extending the base chart class as mentioned above
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
        //Chart.js options
        animation: {
          duration: 0
        },
        responsiveAnimationDuration: 0,
        tooltips: {
          mode: "index",
          intersect: false,
          callbacks: {
            label: function(tooltipItems) {
              return tooltipItems.yLabel + "%";
            }
          }
        },
        hover: {
          mode: "index",
          intersect: true,
          animationDuration: 0
        },
        scales: {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                stepSize: 1,
                min: 0,
                max: 100,
                maxTicksLimit: 10
              },
              gridLines: {
                display: true
              }
            }
          ],
          xAxes: [
            {
              ticks: {
                min: 1,
                sampleSize: 5,
                autoSkip: true,
                autoSkipPadding: 15,
                maxRotation: 0,
                maxTicksLimit: 2,
                padding: 10
              },
              type: "time",
              time: {
                unit: "second"
              },
              displayFormats: {
                second: "h:mm:ss a"
              },
              gridLines: {
                display: false
              },
              distribution: "series"
            }
          ]
        },
        legend: {
          display: true
        },
        responsive: true,
        maintainAspectRatio: false
      }
    };
  },
  mounted() {
    // this.chartData is created in the mixin
    this.renderChart(this.chartData, this.options);
  }
};
</script>

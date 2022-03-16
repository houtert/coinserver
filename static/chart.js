var chart = LightweightCharts.createChart(document.getElementById('chart'), {
	width: 800,
  height: 500,
	layout: {
		backgroundColor: '#ffffff',
		textColor: 'rgba(0, 0, 0, 0.9)',
	},
	grid: {
		vertLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
		horzLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
	},
	crosshair: {
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	rightPriceScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
	},
	timeScale: {
		borderColor: 'rgba(0, 0, 0, 0.8)',
	},
});

var candleSeries = chart.addCandlestickSeries({
  upColor: '#00ff00',
  downColor: '#ff0000',
  borderDownColor: 'rgba(255, 144, 0, 1)',
  borderUpColor: 'rgba(255, 144, 0, 1)',
  wickDownColor: 'rgba(255, 144, 0, 1)',
  wickUpColor: 'rgba(255, 144, 0, 1)',
});
url= "http://mycrypto.duckdns.org:4000/v1/livecandle/";
symbol= window.location.href.split("/").pop();
myURL = url+symbol;
console.log(myURL, {mode: 'no-cors'});
fetch(myURL)
	.then((r) => r.json())
	.then((response) => {
		console.log(candleSeries)
		candleSeries.setData(response);

	})

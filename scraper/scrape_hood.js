const getJSON = require('get-json')
const fs = require('fs')
const path = require('path')
const chalk = require('chalk')
const figlet = require('figlet')
const _ = require('underscore')

const maxstreams = 8
const dataDir = __dirname + '/../data'

console.log(`\nMarket: ${chalk.yellow(process.argv[2])}\n`)
const market = process.argv[2]
var today = new Date();

const dates = {
	from: {					// No data before this day
		year: 2018,
		month: 2,
		day: 23
	},

	to: {
		year: today.getFullYear(),
		month: today.getMonth() + 1,
		day: today.getDate() + 1,
	},
}

const baseApiUrl = 'https://api.cobinhood.com/v1/chart/candles/'

// Full parms: BTC-USDT?end_time=1536022101000&start_time=1530838041000&timeframe=1h
const formatApiUrl = (market, endtime, starttime) => {
	const apiUrl = `${baseApiUrl}${market}?end_time=${endtime}&start_time=${starttime}&timeframe=1m`
	return apiUrl
}

console.log(chalk.dim(`Running with maxstreams=${chalk.yellow(maxstreams)} \n`))

Date.prototype.addDays = function (days) {
	const dat = new Date(this.valueOf())
	dat.setDate(dat.getDate() + days)
	return dat
}

const getDates = (startDate, stopDate) => {
	const dateArray = new Array()
	let currentDate = startDate
	while (currentDate <= stopDate) {
		dateArray.push(currentDate)
		currentDate = currentDate.addDays(1)
	}
	return dateArray
}

const get_24h = (day) => {
	return new Date(day.getFullYear(), day.getMonth(), day.getDate() - 1).getTime()
}

const start = new Date(dates.from.year, dates.from.month - 1, dates.from.day)
const end = new Date(dates.to.year, dates.to.month - 1, dates.to.day)
const dateStack = getDates(start, end)

// Return only base file name without dir
function getLatestFile(dirpath) {

	// Check if dirpath exist or not right here

	let latest;

	const files = fs.readdirSync(dirpath);
	files.forEach(filename => {
		// Get the stat
		const stat = fs.lstatSync(path.join(dirpath, filename));
		// Pass if it is a directory
		if (stat.isDirectory())
			return;

		// latest default to first file
		if (!latest) {
			latest = { filename, mtime: stat.mtime };
			return;
		}
		// update latest if mtime is greater than the current latest
		if (stat.mtime > latest.mtime) {
			latest.filename = filename;
			latest.mtime = stat.mtime;
		}
	});

	return latest.filename;
}

function format_data(candles) {
	var dataparsed = [];
	var arrayLength = candles.length;
	for (var i = 0; i < arrayLength; i++) {
		dataparsed.push([(candles[i].timestamp / 1000), parseFloat(candles[i].open), parseFloat(candles[i].high), parseFloat(candles[i].low), parseFloat(candles[i].close), parseFloat(candles[i].volume), (candles[i].volume * candles[i].close), parseFloat(candles[i].close)]);
	}
	return dataparsed
}

console.log(`Deleting lastest files\n`);

for (let i = 0; i < maxstreams + 1; i += 1) {
	var delfileName = getLatestFile(dataDir);
	var delfilePath = path.join(dataDir, delfileName);

	// Let's delete the last saved file
	if (fs.existsSync(delfilePath)) {
		fs.unlinkSync(delfilePath, (err) => {
			if (err) throw err;
			console.log(`${chalk.white(delfileName)} deleted`);
		});
	}
}

const go = () => new Promise((resolve, reject) => {
	if (dateStack.length === 0) {
		return resolve('Done!')
	}

	const pipeline = []

	for (let i = 0; i < maxstreams; i += 1) {
		const date = dateStack.shift()

		if (!date) {
			continue
		}

		const prettyDate = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate()
		const start = get_24h(date)
		const dataPath = formatApiUrl(market, date.getTime(), start)
		const fileName = `${market}-${prettyDate}.json`
		const filePath = path.join(dataDir, fileName)

		if (fs.existsSync(filePath)) {
			console.log(`Passover: ${chalk.magenta(filePath)} (already exists)`)
			continue
		}

		pipeline.push(new Promise((resolve, reject) => {
			console.log(`Fetching: ${chalk.yellow(prettyDate)} - ${chalk.yellow.dim(dataPath)}`)

			getJSON(dataPath, (error, response) => {
				let cursoryUsd = null

				if (response["success"] === true) {
					real_data = response.result.candles
					cursoryUsd = real_data[0].close
					console.log(`Recevied: ${chalk.green(prettyDate)} - ${chalk.red('$' + cursoryUsd)}`)
				}

				if (response["success"] === false) {
					console.log(chalk.red(`Received "Undefined" data for ${chalk.white(prettyDate)}. Too many streams? (Data for one dates are not available, eg: '2011-10-1')`))
					response = []
				}

				var parsed_data = format_data(real_data)
				const output = JSON.stringify(parsed_data)

				fs.writeFile(filePath, output, 'utf8', err => {
					if (err) {
						return reject(err)
					} else {
						console.log(`Saved to: ${chalk.blue(filePath)}`)
						resolve('Ok')
					}
				})
			})
		}))
	}

	Promise.all(pipeline).then(() => {
		resolve(go())
	}).catch(err => {
		reject(err)
	})
})

function go_today() {

	const prettyDate = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + (today.getDate() + 1)
	const start = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
	const dataPath = formatApiUrl(market, today.getTime(), start)
	const fileName = `${market}-${prettyDate}.json`
	const filePath = path.join(dataDir, fileName)

	if (fs.existsSync(filePath)) {
		fs.unlinkSync(filePath, (err) => {
			if (err) throw err;
			console.log(`${chalk.white(fileName)} deleted`);
		});
	}

	console.log(`Fetching: ${chalk.yellow(prettyDate)} - ${chalk.yellow.dim(dataPath)}`)

	getJSON(dataPath, (error, response) => {
		let cursoryUsd = null

		if (response["success"] === true) {
			real_data = response.result.candles
			cursoryUsd = real_data[0].close
			console.log(`Recevied: ${chalk.green(prettyDate)} - ${chalk.red('$' + cursoryUsd)}`)
		}

		if (response["success"] === false) {
			console.log(chalk.red(`Received "Undefined" data for ${chalk.white(prettyDate)}. Too many streams? (Data for one dates are not available, eg: '2011-10-1')`))
			response = []
		}

		var parsed_data = format_data(real_data)
		const output = JSON.stringify(parsed_data)

		fs.writeFile(filePath, output, 'utf8', err => {
			if (err) {
				return reject(err)
			} else {
				console.log(`Saved to: ${chalk.blue(filePath)}`)
			}
		})
	})
}

go().then(() => {
	console.log(chalk.magenta('Done with historical data'))
}).catch(err => {
	console.error(err)
})

go_today();
console.log(chalk.magenta('Done with todays data'));


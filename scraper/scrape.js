const getJSON = require('get-json')
const fs = require('fs')
const path = require('path')
const chalk = require('chalk')
const figlet = require('figlet')
const _ = require('underscore')

const maxstreams = 8
const dataDir = __dirname + '/../data'

const market = 'bitstampUSD'
var today = new Date();

const dates = {
	from: {
		year: today.getFullYear() - 5,
		month: today.getMonth() + 1,
		day: today.getDate()
	},

	to: {
		year: today.getFullYear(),
		month: today.getMonth() + 1,
		day: today.getDate(),
	},
}

const baseApiUrl = 'http://bitcoincharts.com/charts/chart.json?'

// Full parms: m=bitstampUSD&SubmitButton=Draw&r=60&i=1-min&c=1&s=2011-09-14&e=2011-09-14&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3=&i4=&v=1&cv=0&ps=0&l=0&p=0&
const formatApiUrl = (market, date) => {
	const apiUrl = `${baseApiUrl}m=${market}&SubmitButton=Draw&r=60&i=1-min&c=1&s=${date}&e=${date}&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3=&i4=&v=1&cv=0&ps=0&l=0&p=0&`
	return apiUrl
}

console.log(chalk.dim(`Running with maxstreams=${chalk.yellow(maxstreams)} \n`))

const url = (baseurl, date) => {
	return baseurl + date
}

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

function isDirEmpty(dirpath) {
	logic = false
	fs.readdir(dirpath, function (err, files) {
		if (err) {
			// some sort of error
		} else {
			if (!files.length) {
				logic = true
			}
		}
	});
	return logic
}

console.log(`Deleting lastest files`)

if (!isDirEmpty(dataDir)) {
	for (let i = 0; i < maxstreams; i += 1) {
		var delfileName = getLatestFile(dataDir)
		var delfilePath = path.join(dataDir, delfileName)

		// Let's delete the last saved file
		if (fs.existsSync(delfilePath)) {
			fs.unlinkSync(delfilePath, (err) => {
				if (err) throw err;
				console.log(`${chalk.white(delfileName)} deleted`);
			});
		}
	}
}
else {
	console.log(`Directory is Empty`)
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

		const prettyDate = date.getFullYear() + '-' + (date.getUTCMonth() + 1) + '-' + date.getUTCDate()
		const dataPath = formatApiUrl(market, prettyDate)
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

				if (response !== undefined) {
					cursoryUsd = response[0][7]
				}
				console.log(`Recevied: ${chalk.green(prettyDate)} - ${chalk.red('$' + cursoryUsd)}`)

				if (response === undefined) {
					console.log(chalk.red(`Received "Undefined" data for ${chalk.white(prettyDate)}. Too many streams? (Data for ome dates are not avilable, eg: '2011-10-1')`))
					response = []
				}


				const output = JSON.stringify(response)

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

go().then(() => {
	console.log(chalk.magenta('DONE!'))
}).catch(err => {
	console.error(err)
})


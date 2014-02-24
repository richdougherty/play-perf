#/usr/bin/env python

import argparse, os, re, select, subprocess, time
from collections import namedtuple
from decimal import Decimal

############

def head(l):
	if len(l) == 1:
		return l[0]
	else:
		raise Exception("Can't get head, %s items in list" % len(l))

##########

App = namedtuple('App', ['name', 'args'])

helloworldApp = App('helloworld', [])
zentasksApp = App('zentasks', ['-DapplyEvolutions.default=true'])
#benchApp = App('bench', [])
bench2App = App('bench2', [])

apps = [helloworldApp, zentasksApp, bench2App]

Version = namedtuple('Version', ['name'])

masterVersion = Version('master')
itTrampVersion = Version('it-tramp')
playTrampVersion = Version('play-tramp')
itInlineVersion = Version('it-inline')
reqOptsVersion = Version('req-opts')
trampListVersion = Version('tramp-list')
master23Version = Version('master-2.3')

versions = [
	masterVersion,
	itTrampVersion,
	playTrampVersion,
	itInlineVersion,
	reqOptsVersion,
	trampListVersion,
	master23Version
]

defaultVersions = [
	# masterVersion,
	# playTrampVersion,
	# reqOptsVersion,
	# trampListVersion,
	master23Version
]

Lang = namedtuple('Lang', ['name'])
scalaLang = Lang('scala')
javaLang = Lang('java')
langs = [scalaLang, javaLang]

defaultLangs = [scalaLang]

Build = namedtuple('Build', ['app', 'lang', 'version', 'path'])

builds = [
	Build(helloworldApp, scalaLang, masterVersion,    'apps/hw-master1/bin/helloworld'),
	Build(helloworldApp, scalaLang, itTrampVersion,   'apps/hw-perf1/bin/helloworld'),
	Build(helloworldApp, scalaLang, playTrampVersion, 'apps/hw-st3/bin/helloworld'),
	Build(helloworldApp, scalaLang, itInlineVersion,  'apps/hw-itinline4/bin/helloworld'),
	Build(helloworldApp, scalaLang, reqOptsVersion,   'apps/hw-reqopt5/bin/helloworld'),
	Build(helloworldApp, scalaLang, trampListVersion, 'apps/hw-tramplist6/bin/helloworld'),
	Build(helloworldApp, scalaLang, master23Version,  'apps/scala-hw-master-2.3/bin/helloworld'),
	Build(helloworldApp, javaLang,  master23Version,  'apps/java-hw-master-2.3/bin/helloworld'),

	#Build(benchApp,      scalaLang, masterVersion,    'apps/bench-master1/bin/bench'),
	#Build(benchApp,      scalaLang, itTrampVersion,   'apps/bench-perf2/bin/bench'),
	#Build(benchApp,      scalaLang, playTrampVersion, 'apps/bench-st3/bin/bench'),

	Build(bench2App,     scalaLang, masterVersion,    'apps/bench2-master1/bin/bench'),
	Build(bench2App,     scalaLang, itTrampVersion,   'apps/bench2-perf1/bin/bench'),
	Build(bench2App,     scalaLang, playTrampVersion, 'apps/bench2-st3/bin/bench'),
	Build(bench2App,     scalaLang, itInlineVersion,  'apps/bench2-itinline4/bin/bench'),
	Build(bench2App,     scalaLang, reqOptsVersion,   'apps/bench2-reqopt5/bin/bench'),
	Build(bench2App,     scalaLang, trampListVersion, 'apps/bench2-tramplist6/bin/bench'),
	Build(bench2App,     scalaLang, master23Version,  'apps/scala-bench-master-2.3/bin/scala-bench'),
	Build(bench2App,     javaLang,  master23Version,  'apps/java-bench-master-2.3/bin/java-bench'),

	Build(zentasksApp,   scalaLang, masterVersion,    'apps/zt-master1/bin/zentask'),
	Build(zentasksApp,   scalaLang, itTrampVersion,   'apps/zt-perf1/bin/zentask'),
	Build(zentasksApp,   scalaLang, playTrampVersion, 'apps/zt-st3/bin/zentask'),
	Build(zentasksApp,   scalaLang, itInlineVersion,  'apps/zt-itinline4/bin/zentask'),
	Build(zentasksApp,   scalaLang, reqOptsVersion,   'apps/zt-reqopt5/bin/zentask'),
	Build(zentasksApp,   scalaLang, trampListVersion, 'apps/zt-tramplist6/bin/zentask'),
	Build(zentasksApp,   scalaLang, master23Version,  'apps/scala-zt-master-2.3/bin/zentask'),
	Build(zentasksApp,   javaLang,  master23Version,  'apps/java-zt-master-2.3/bin/zentask'),
]

Test = namedtuple('Test', ['name', 'appTests'])
AppTest = namedtuple('AppTest', ['app', 'path', 'wrkArgs'])

tests = [
	Test('helloworld-sample', [AppTest(helloworldApp, '/', [])]),
	Test('simple-result', [
		#AppTest(benchApp, '/helloworld', []),
		AppTest(bench2App, '/helloworld', []),
	]),
	Test('50k-download2', [
		AppTest(bench2App, '/download/51200', [])
	]),
	Test('50k-download-chunked', [
		#AppTest(benchApp, '/download/51200', []),
		AppTest(bench2App, '/download-chunked/51200', []) # ['--timeout', '5s']
	]),
	Test('50k-upload', [
		#AppTest(benchApp, '/upload', ['-M', 'PUT', '--body', '50k.bin']),
		AppTest(bench2App, '/upload', ['-M', 'PUT', '--body', '50k.bin']),
	]),
	Test('zentasks-sample', [
		AppTest(zentasksApp, '/', [
		'-H',
		'Cookie: PLAY_SESSION="0a28e06a3342d31a45af7182fc4598c202d11890-email=guillaume%40sample.com"']),
	])
]

#########

WrkOutput = namedtuple('WrkOutput', ['rps', 'socketErrors', 'responseErrors'])

def parseWrkOutput(output):
	rps = Decimal(re.compile(r'Requests/sec:(\s+)([0-9.]+)').search(output).group(2))
	socketErrors = 'Socket errors' in output
	responseErrors = 'Non-2xx or 3xx responses' in output
	#print output
	return WrkOutput(rps, socketErrors, responseErrors)

assert(parseWrkOutput("""Running 15s test @ http://127.0.0.1:9000/
  12 threads and 25 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.20ms    1.47ms  20.65ms   88.32%
    Req/Sec     1.00k   237.58     1.78k    73.29%
  170659 requests in 15.00s, 324.69MB read
Requests/sec:  11376.38
Transfer/sec:     21.64MB""") == WrkOutput(Decimal('11376.38'), False, False))

assert(parseWrkOutput("""Running 10s test @ http://127.0.0.1:9000/download/51200
  2 threads and 4 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    47.15ms   10.17ms  54.33ms  100.00%
    Req/Sec    35.00      0.00    35.00    100.00%
  660 requests in 10.00s, 32.47MB read
  Socket errors: connect 0, read 0, write 0, timeout 4
Requests/sec:     65.98
Transfer/sec:      3.25MB""") == WrkOutput(Decimal('65.98'), True, False))

assert(parseWrkOutput("""Running 5s test @ http://127.0.0.1:9000/
  1 threads and 1 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.34ms  220.43us   2.97ms   81.12%
    Req/Sec   794.79    112.91     1.00k    79.33%
  3608 requests in 5.00s, 7.02MB read
  Non-2xx or 3xx responses: 3608
Requests/sec:    721.54
Transfer/sec:      1.40MB""") == WrkOutput(Decimal('721.54'), False, True))

def drainPipe(process):
	f = process.stdout
	r, w, e = select.select([f], [], [], 0)
	if r: os.read(f.fileno(), 4096) # safe to read this size?

def startApp(app, build):
	appCommand = [build.path] + app.args
	#print appCommand
	appProcess = subprocess.Popen(appCommand, stdout=subprocess.PIPE)
	stdoutIter = iter(appProcess.stdout.readline, '')
	for line in stdoutIter:
		if 'Listening for HTTP' in line: break
	return appProcess

def runWrk(appTest, allowErrors=False):
	wrkCommand = ['wrk', '-t%s' % args.threads, '-c%s' % args.connections, '-d'+args.runDuration] + \
								appTest.wrkArgs + \
								['http://127.0.0.1:9000'+appTest.path]
	#print wrkCommand
	try:
		rawOutput = subprocess.check_output(wrkCommand, stderr=subprocess.STDOUT)
		#print output
		parsedOutput = parseWrkOutput(rawOutput)
		return (parsedOutput, rawOutput)
	except subprocess.CalledProcessError as e:
		print e.output
		raise

def runAndCollect(appTest, count, appProcess):
	results = []
	for i in xrange(0, count):
		print 'Run %2d/%2d' % (i+1, count),
		drainPipe(appProcess)
		(wrkOutput, rawWrkOutput) = runWrk(appTest)
		print '%10.2f, %s, %s' % (
			wrkOutput.rps,
			'SOCKETERROR' if wrkOutput.socketErrors else 'ok',
			'RESPONSEERRORS' if wrkOutput.responseErrors else 'ok'
		)
		if wrkOutput.socketErrors or wrkOutput.responseErrors: print rawWrkOutput
		results.append(wrkOutput)
	return results

def runTest(appTest, build):
	appProcess = startApp(appTest.app, build)
	try:
		print "Warmup"
		unusedResults = runAndCollect(appTest, args.warmupRuns, appProcess)
		print "Test"
		results = runAndCollect(appTest, args.testRuns, appProcess)
		#print results
		return results
	finally:
		appProcess.terminate()

#############

def byName(l):
	return lambda name: head(filter(lambda x: x.name == name, l))

parser = argparse.ArgumentParser(description='Run benchmarks')
parser.add_argument('--test', nargs='*', type=byName(tests), default=tests, dest='tests')
parser.add_argument('--versions', nargs='*', type=byName(versions), default=defaultVersions, dest='versions')
parser.add_argument('--langs', nargs='*', type=byName(langs), default=defaultLangs, dest='langs')
parser.add_argument('--warmup-runs', default=5, type=int, dest='warmupRuns')
parser.add_argument('--test-runs', default=10, type=int, dest='testRuns')
parser.add_argument('--connections', default='32', type=int, dest='connections')
parser.add_argument('--threads', default='16', type=int, dest='threads')
parser.add_argument('--run-duration', default='10s', dest='runDuration')

args = parser.parse_args()
#print args

print 'Tests: ' + ', '.join([x.name for x in args.tests])
print 'Versions: ' + ', '.join([x.name for x in args.versions])
print 'Langs: ' + ', '.join([x.name for x in args.langs])

for test in args.tests:
	for appTest in test.appTests:
		for build in filter(lambda b: b.app == appTest.app and b.version in args.versions and b.lang in args.langs, builds):
			print
			print '=== %s/%s ===' % (test.name, build.version.name)
			testResults = runTest(appTest, build)
			print 'AVERAGE %12.2f' % (sum([r.rps for r in testResults])/len(testResults))



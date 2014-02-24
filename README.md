
Usage

python perf.py


Apps

helloworld-sample

An HTML page displaying a form.
* App: `PLAY/samples/scala/helloworld`
* wrk: `/`

simple-result

Returning a short string.
* App: `BENCH/app-src/scala-bench`
* wrk: `/helloworld`

50k-download2

Returning 50KB in one piece.
* App: `BENCH/app-src/scala-bench`
* wrk: `/download/51200`

50k-download-chunked

Returning 50KB in 12 chunks.
* App: `BENCH/app-src/scala-bench`
* wrk `/download-chunked/51200`

50k-upload

Receiving a 50KB PUT request.
* App: `BENCH/app-src/scala-bench`
* wrk `/upload`, `-M PUT --body 50k.bin`

zentasks-sample

An HTML page showing tasks for a logged-in user.
* App: `PLAY/samples/scala/zentasks`
* wrk: `/`, `-H Cookie: PLAY_SESSION="0a28e06a3342d31a45af7182fc4598c202d11890-email=guillaume%40sample.com"`

Versions

2.2 benchmarking

* `master`
* `it-tramp`
* `play-tramp`
* `it-inline`
* `req-opts`
* `tramp-list`

2.3 benchmarking

* `2.3-master` (master from 20 Feb 2014, `d62623a0b86760bd4e1788f8d28c6025ee89f48f`)

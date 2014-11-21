#!/usr/bin/env ruby

require 'pty'

raise 'Must run as root' unless Process.uid == 0

wpr_file = "/tmp/t.wpr"
cmd = "./replay.py --record #{wpr_file}"
(wpr_out, wpr_in, wpr_pid) = PTY.spawn cmd
[wpr_out, wpr_in].each { |stream| stream.close }
Process.kill("TERM", wpr_pid)
Process.wait wpr_pid

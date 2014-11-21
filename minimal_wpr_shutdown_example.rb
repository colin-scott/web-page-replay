#!/usr/bin/env ruby

require 'pty'

raise 'Must run as root' unless Process.uid == 0

# Spawn wpr:
wpr_file = "/tmp/t.wpr"
cmd = "./replay.py --record #{wpr_file}"
(wpr_out, wpr_in, wpr_pid) = PTY.spawn cmd

# Wait for wpr to boot up:
wpr_out.each do |line|
  puts "WPR: #{line}"
  break if line =~ /HTTPS server started on/
end

# Kill wpr:
[wpr_out, wpr_in].each { |stream| stream.close }
Process.kill("TERM", wpr_pid)
Process.wait wpr_pid

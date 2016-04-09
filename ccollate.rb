#!/usr/bin/env ruby

HEADER_EXTS = %w(.h .hh .hpp)

$include_dirs = ['.']

$visited = []

def parse(file_name)
  if $visited.include? file_name
    return ''
  else
    $visited << file_name
  end

  contents = File.open file_name, 'r' do |file|
    file.read
  end

  contents.gsub!(/\/\*\*(?:.|[\r\n])*?\*\/\s*/, '') # remove documentation comments

  contents = contents.each_line.with_index.collect do |line, lineno|
    lineno = lineno + 1 # line numbers start at 1
    line.gsub!(/^\s*\/\/.*\s*$/, '') # remove c-style comments on their own lines

    if line =~ /^#include\s+"([^"]+)"\s*$/ # recurse and copy
      include_file = nil
      include_dirs = [File.split(file_name).first] + $include_dirs
      include_dirs.each do |inc|
        include_path = File.expand_path File.join(inc, $1)
        if File.exist? include_path
          include_file = include_path
          break
        end
      end

      raise "Fatal Error: The file #{$1} was not found in any of the include paths #{$include_dirs.inspect}" unless include_file

      include = parse(include_file)
      include << "#line #{lineno + 1} \"#{file_name}\"\n"
    else
      line
    end
  end.join
  contents = ["#line 1 \"#{file_name}\"\n", contents].join unless contents.empty?
  contents
end

if ARGV.empty?
  exit(-1)
else
  start_file = File.expand_path ARGV.first
  raise "#{ARGV.first} is not a valid header file." unless HEADER_EXTS.include?(File.extname(start_file))
  $include_dirs << File.split(start_file).first # automatically include the starting directory
  puts parse(start_file)
end

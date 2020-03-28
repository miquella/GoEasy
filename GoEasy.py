import sublime
import sublime_plugin

import golangconfig
import subprocess

from GoEasy.Patch import patch_view

class GoFmtCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		return self.view.score_selector(0, 'source.go') > 0

	def description(self):
		return 'GoEasy: GoFmt'

	def run(self, edit):
		view = self.view
		try:
			# Get the view content and encode it
			content = view.substr(sublime.Region(0, view.size()))
			encoded_content = content.encode('utf-8')

			# Find the gofmt executable
			executable_path, env = golangconfig.subprocess_info('gofmt', [], optional_vars=['GOPATH', 'GOROOT'], view=self.view)

			# Format the content
			proc = subprocess.Popen('gofmt', executable=executable_path, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = proc.communicate(input=encoded_content)
			if proc.returncode != 0:
				self.view.window().status_message('GoEasy: Cannot format file — please check for syntax errors')
				return

			# Decode and patch the view
			decoded_content = stdout.decode('utf-8')
			patch_view(self.view, edit, decoded_content)

		except (golangconfig.ExecutableError) as ex:
			pass

		except (golangconfig.GoRootNotFoundError, golangconfig.GoPathNotFoundError) as ex:
			pass

class GoEasyListener(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		view.run_command('go_fmt')

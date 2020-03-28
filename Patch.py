import sublime
import sublime_plugin

from diffmatchpatch.python3 import diff_match_patch

def patch_view(view, edit, new_content):
	# Prevent tabs being translated to spaces while patching
	translate_tabs_to_spaces = view.settings().get('translate_tabs_to_spaces')
	view.settings().set('translate_tabs_to_spaces', False)

	original_content = view.substr(sublime.Region(0, view.size()))
	try:
		# Attempt to patch the file incrementally
		dmp = diff_match_patch()
		diffs = dmp.diff_main(original_content, new_content)
		dmp.diff_cleanupEfficiency(diffs)

		pos = 0
		for op, text in diffs:
			op_len = len(text)
			if op == diff_match_patch.DIFF_INSERT:
				view.insert(edit, pos, text)
				pos += op_len
			elif op == diff_match_patch.DIFF_EQUAL:
				pos += op_len
			elif op == diff_match_patch.DIFF_DELETE:
				view.erase(edit, sublime.Region(pos, pos + op_len))
			else:
				raise Exception('Unknown diff_match_patch operation')

	except Exception as ex:
		# Incremental patching failed, replace the whole file
		print("GoEasy: Couldn't patch the view nicely. Doing it un-nicely.")
		view.replace(edit, sublime.Region(0, view.size()), new_content)

	finally:
		view.settings().set('translate_tabs_to_spaces', translate_tabs_to_spaces)

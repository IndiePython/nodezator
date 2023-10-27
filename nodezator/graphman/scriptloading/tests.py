import unittest
from nodezator.graphman import scriptloading
from nodezator.graphman.exception import NodeScriptsError


class LoadTest(unittest.TestCase):
	
	def test_success(self):
		scriptloading.load_scripts(["D:\OtherDevStuff\\nodezator\\test_nodezator_nodes"],[])
		
	def test_no_callable(self):
		# the script is simply lacking the main_callable assigment
		fail=True
		try:
			scriptloading.load_scripts(["D:\OtherDevStuff\\nodezator\\test_nodezator_nodes_no_callable"],[])
			fail=False
		except NodeScriptsError as err:
			assert "node script is missing a" in str(err)
			pass
		
		assert fail
		
	def test_no_signature(self):
		# callable but no signature?		
		assert fail
	
	def test_installed_not_loaded(self):
		# no idea how this works.
		assert fail
	
	def test_no_callable_object(self):
		# main_callable is an int
		fail=True
		try:
			scriptloading.load_scripts(["D:\OtherDevStuff\\nodezator\\test_nodezator_nodes_not_callable_object"],[])
			fail = False
		except NodeScriptsError as err:
			assert "must be callable" in str(err)
			pass
		
		assert fail
	
	def test_not_loaded(self):
		# ... intentional syntax error
		fail=True
		
		try:
			scriptloading.load_scripts(["D:\OtherDevStuff\\nodezator\\test_nodezator_nodes_not_inspectable"],[])
			fail = False
		except NodeScriptsError as err:
			assert "error while trying to load" in str(err)
			pass
		
		assert fail
	
if __name__=="__main__":
	unittest.main()

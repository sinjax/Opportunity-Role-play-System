The Roleplay system
===================

Details of this system can be found in the pdf file


Refactoring
===========
Currently the core components of characters including their weapons and so on are held in characters.py. The stuff about the die are held in dice.py. Currently combat.py contains all the static functions about combat, but i've created the opportunity.py and violence.py, it might be useful to make the distinction between these two stages but that might be pointless.

Run the Test
============

You can run the tests like this:

	nosetests -s opportunity.test.test_combat

To make this work you need to install nose:

	easy_install pip
	pip install nose

Leave out the -s if you don't care about the output

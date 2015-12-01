# See file COPYING distributed with fsutils for copyright and license.

test : 
	python -m unittest -vb tests

clean : 
	rm -f MANIFEST xnatrest/*.pyc tests/*.pyc

# eof

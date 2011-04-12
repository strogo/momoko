News/Changelog
==============


0.2.0 (2011-??-??)
------------------

* Added a wrapper class, ``Momoko``, for ``Pool``, ``BatchQuery`` and ``QueryChain``.
* Added the ``QueryChain`` class for executing a chain of queries (and callables)
  in a certain order.
* Added the ``BatchQuery`` class for executing batches of queries at the same time.
* Improved ``Pool._clean_pool``. It threw an ``IndexError`` when more than one
  connection needed to be closed.


0.1.0 (2011-03-13)
-------------------

* Initial release.